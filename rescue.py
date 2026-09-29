"""Turn actual failed games into short, provably recoverable challenges."""
from collections import deque
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from random import Random
from time import perf_counter
import json
from engine import Game,DIRECTIONS,slide,can_move,valid_board

PRACTICE=Path(__file__).with_name('rescue_practice.json')

def validate(extra):
    if not isinstance(extra,dict):raise ValueError('Invalid rescue state')
    e=deepcopy(extra)
    if type(e.get('limit')) is not int or not 1<=e['limit']<=7 or type(e.get('goal')) is not int or not 2<=e['goal']<=5:raise ValueError('Invalid rescue objective')
    if not isinstance(e.get('challenge'),str) or len(e['challenge'])>80:raise ValueError('Invalid rescue id')
    if type(e.get('par')) is not int or not 1<=e['par']<=e['limit']:raise ValueError('Invalid rescue reference')
    return {k:e[k] for k in ('limit','goal','challenge','par')}

def spawn(board,state):
    # Use the same choice()+random() sequence as the original classic game;
    # random consumption depends on empty-cell count, so each branch carries
    # its own complete RNG state. A fixed stream of floats would be incorrect.
    b=list(board);empty=[i for i,v in enumerate(b) if not v];r=Random();r.setstate(state)
    if empty:
        index=r.choice(empty);b[index]=2 if r.random()<.9 else 4
    return tuple(b),r.getstate()

def solve(board,state,goal=3,remaining=6,budget=2.):
    start=perf_counter();deadline=start+budget;board=tuple(board);nodes=0;previews={}
    remaining=max(0,min(7,remaining))
    if board.count(0)>=goal:return dict(direction=None,solution=[],solvable=True,complete=True,backend='rescue',nodes=0,depth=0,ms=0,previews={})
    queue=deque();seen=set()
    for d in DIRECTIONS:
        after,gain,_,_=slide(board,d)
        if tuple(after)==board or not remaining:continue
        child,rng=spawn(after,state);previews[d]=dict(board=list(child),gain=gain)
        queue.append((child,rng,(d,)));seen.add((child,rng,1))
    solution=None;complete=True
    while queue:
        current,rng,path=queue.popleft();nodes+=1
        if current.count(0)>=goal and can_move(current):solution=path;break
        if nodes%64==0 and perf_counter()>deadline:complete=False;break
        if len(path)>=remaining:continue
        for d in DIRECTIONS:
            after,_,_,_=slide(current,d)
            if tuple(after)==current:continue
            child,state2=spawn(after,rng);key=(child,state2,len(path)+1)
            if key in seen:continue
            seen.add(key);queue.append((child,state2,path+(d,)))
    return dict(direction=solution[0] if solution else None,solution=list(solution or []),solvable=bool(solution),complete=complete,
        backend='rescue',nodes=nodes,depth=len(solution) if solution else remaining,ms=round((perf_counter()-start)*1000),
        previews=previews,board=list(board),values=[],
        explanation=f'验证路线：{len(solution)} 步打开至少 {goal} 格空间' if solution else '余下步数内没有达标路线' if complete else '搜索预算用尽，尚未找到验证路线')

def origin_game(failed,state):
    g=Game(0,mode=failed.mode,challenge_date=failed.challenge_date);g.apply_snapshot(state)
    g.id=failed.id;g.elapsed=failed.elapsed;return g

def extract(data,budget=3.):
    failed=Game.restore(data)
    if failed.mode not in ('classic','daily','sprint') or can_move(failed.board):return dict(status='ineligible',challenge=None)
    start=perf_counter();frames=[*failed.history,failed.snapshot()];checked=0;incomplete=False
    for distance in range(1,min(10,len(failed.history))+1):
        if perf_counter()-start>=budget:incomplete=True;break
        origin=origin_game(failed,frames[-1-distance])
        if origin.board.count(0)>1:continue
        checked+=1
        result=solve(origin.board,origin.rng.getstate(),3,6,max(.05,budget-(perf_counter()-start)))
        if not result['complete']:incomplete=True;break
        if not result['solvable']:continue
        # Replay the witness through the production engine before publishing.
        witness=Game.restore(origin.serialize());witness.mode='classic'
        for direction in result['solution']:
            if witness.move(direction) is None:raise ValueError('Invalid rescue witness')
        if witness.board.count(0)<3 or not can_move(witness.board):raise ValueError('Rescue verification failed')
        oldframes=frames[-1-distance:];original=[]
        for current,following in zip(oldframes,oldframes[1:]):
            direction=None
            for d in DIRECTIONS:
                after,_,_,_=slide(current[0],d)
                if after==current[0]:continue
                child,_=spawn(after,current[4])
                if list(child)==following[0]:direction=d;break
            original.append(dict(board=following[0][:],direction=direction))
        origin.history=[];origin.future=[]
        challenge=dict(id=sha256(repr((origin.board,origin.rng.getstate())).encode()).hexdigest()[:20],
            origin=origin.serialize(),goal=3,limit=6,par=len(result['solution']),solution=result['solution'],
            original=original,source_score=failed.score,source_moves=origin.moves,rewind=distance,practice=False)
        return dict(status='found',challenge=challenge,checked=checked,ms=round((perf_counter()-start)*1000))
    return dict(status='timeout' if incomplete else 'not_found',challenge=None,checked=checked,ms=round((perf_counter()-start)*1000))

def valid_challenge(c):
    if not isinstance(c,dict):return False
    try:
        if not isinstance(c['id'],str) or len(c['id'])>80:return False
        if any(type(c.get(k)) is not int or not 0<=c[k]<=10**12 for k in ('source_score','source_moves','rewind')):return False
        if not 1<=c['rewind']<=10:return False
        if 'title' in c and (not isinstance(c['title'],str) or len(c['title'])>14):return False
        g=Game.restore(c['origin'])
        if g.mode not in ('classic','daily','sprint') or not can_move(g.board) or g.board.count(0)>=c['goal']:return False
        validate(dict(challenge=c['id'],goal=c['goal'],limit=c['limit'],par=c['par']))
        path=c['solution']
        if not isinstance(path,list) or len(path)!=c['par'] or any(d not in DIRECTIONS for d in path):return False
        g.mode='classic'
        for d in path:
            if g.move(d) is None:return False
        if g.board.count(0)<c['goal']:return False
        if not isinstance(c.get('original'),list) or len(c['original'])>10:return False
        return all(isinstance(f,dict) and valid_board(f.get('board')) and f.get('direction') in (*DIRECTIONS,None) for f in c['original'])
    except (ValueError,TypeError,KeyError,IndexError):return False

def make_rescue(c):
    if not valid_challenge(c):raise ValueError('Invalid rescue challenge')
    g=Game.restore(c['origin']);g.mode='rescue';g.moves=g.score=g.ai_moves=g.undos=0;g.assisted=False;g.elapsed=0.
    g.extra=validate(dict(challenge=c['id'],goal=c['goal'],limit=c['limit'],par=c['par']))
    g.history=[];g.future=[];return g

def practice_challenges():
    if not PRACTICE.exists():return []
    try:return [c for c in json.loads(PRACTICE.read_text(encoding='utf-8')) if valid_challenge(c)]
    except (ValueError,TypeError,OSError):return []
