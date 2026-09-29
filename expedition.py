"""Six-stage ability runs and a rules-aware, bounded expectimax player."""
from copy import deepcopy
from functools import lru_cache
from math import log2
from random import Random,SystemRandom
from time import perf_counter
from engine import Game,Track,DIRECTIONS,slide,can_move

STAGES=[('启程',100,26),('蓄势',260,34),('回响',520,42),('临界',900,46),('跃迁',1400,52),('终章',2200,60)]
ABILITIES={
 'combo':('连击引擎','连续合并，每连击加 25% / 40% 分，最多叠四层。','连续合并'),
 'battery':('蓄能核心','每组合并额外获得 1 / 2 点能量，更频繁使用主动能力。','能量循环'),
 'gambit':('豪赌协议','得分 ×2 / ×2.5；新方块为 4 的概率升至 30% / 40%。','高分 · 高风险'),
 'corner':('角落增幅','在四角完成的合并，额外获得该方块 50% / 100% 的分数。','角落经营'),
 'echo':('共鸣回路','一步合并至少两组时，本步基础分额外增加 50% / 100%。','多组合并'),
 'flow':('空间回流','一步合并至少 3 / 2 组时，本步不生成新方块。','保留空间'),
 'reserve':('从容节拍','每关增加 4 / 8 步。选择后本关立即生效。','延长回合'),
 'warp':('折跃透镜','交换方块的能量消耗从 6 降至 4 / 3。','低耗交换'),
 'ice':('凝时晶体','凝时多阻止 1 / 2 次落子，冷却时间保持六步。','控制落子'),
}

def description(key,rank):
    return {
        'combo':f'连续合并，从第二次起每次加成 {25 if rank==1 else 40}%，最多累计 {100 if rank==1 else 160}%。',
        'battery':f'每组合并额外充能 {rank} 点。用更多能量驱动交换与凝时。',
        'gambit':f'全部得分乘以 {2 if rank==1 else 2.5}；新方块为 4 的概率升至 {30 if rank==1 else 40}%。',
        'corner':f'四角位置完成合并时，额外得到该方块 {50*rank}% 的分数。',
        'echo':f'一步合并至少两组时，基础得分再增加 {50*rank}%。',
        'flow':f'一步合并至少 {4-rank} 组时，本步不生成新方块。',
        'reserve':f'每关增加 {4*rank} 步。本关立刻生效，后续每关持续生效。',
        'warp':f'交换任意两枚不同数字只消耗 {4 if rank==1 else 3} 点能量。',
        'ice':f'凝时阻止接下来 {2+rank} 次落子，冷却时间仍为六步。',
    }[key]

def make_expedition(seed=None):
    seed=SystemRandom().randrange(2**53) if seed is None else seed
    g=Game(seed,mode='expedition')
    g.extra=dict(seed=seed,stage=0,phase='draft',perks={},offers=['combo','battery','gambit'],
        stage_score=0,stage_start=0,energy=0,streak=0,freeze=0,cooldown=0,cleared=0)
    return g

def validate(extra):
    if not isinstance(extra,dict):raise ValueError('Invalid expedition state')
    e=deepcopy(extra)
    limits={'seed':2**53,'stage':5,'stage_score':10**18,'stage_start':10**9,'energy':12,'streak':1000000,'freeze':4,'cooldown':6,'cleared':6}
    for key,maximum in limits.items():
        if type(e.get(key)) is not int or not 0<=e[key]<=maximum:raise ValueError('Invalid expedition '+key)
    if e.get('phase') not in ('draft','play','clear','won','lost'):raise ValueError('Invalid expedition phase')
    perks=e.get('perks')
    if not isinstance(perks,dict) or any(k not in ABILITIES or type(v) is not int or not 1<=v<=2 for k,v in perks.items()):raise ValueError('Invalid abilities')
    offers=e.get('offers')
    if not isinstance(offers,list) or len(offers)>3 or len(set(offers))!=len(offers) or any(k not in ABILITIES or perks.get(k,0)>=2 for k in offers):raise ValueError('Invalid draft')
    if e['phase'] in ('draft','clear') and len(offers)!=3:raise ValueError('Incomplete draft')
    return e

def limit(e):return STAGES[e['stage']][2]+4*e['perks'].get('reserve',0)
def remaining(g):return max(0,limit(g.extra)-(g.moves-g.extra['stage_start']))
def spawn_four(e):return .2+.1*e['perks']['gambit'] if 'gambit' in e['perks'] else .1
def swap_cost(e):return (6,4,3)[e['perks'].get('warp',0)]

def reward(board,gain,merges,e):
    e=deepcopy(e);p=e['perks'];e['streak']=e['streak']+1 if gain else 0
    multiplier=1+min(4,max(0,e['streak']-1))*(.4 if p.get('combo')==2 else .25) if p.get('combo') else 1
    extra=sum(board[i] for i in merges if i in (0,3,12,15))*.5*p.get('corner',0)
    extra+=gain*.5*p.get('echo',0) if len(merges)>=2 else 0
    points=round((gain+extra)*multiplier*((2 if p['gambit']==1 else 2.5) if p.get('gambit') else 1))
    e['energy']=min(12,e['energy']+len(merges)*(1+p.get('battery',0)))
    skip=e['freeze']>0 or (p.get('flow',0)>0 and len(merges)>=4-p['flow'])
    e['freeze']=max(0,e['freeze']-1);e['cooldown']=max(0,e['cooldown']-1)
    return points,skip,e

def refresh(g):
    e=g.extra
    if e['phase']!='play':return
    if g.score-e['stage_score']>=STAGES[e['stage']][1]:
        e['cleared']=e['stage']+1;e['phase']='won' if e['stage']==5 else 'clear'
        if e['phase']=='clear':
            pool=[k for k in ABILITIES if e['perks'].get(k,0)<2]
            Random(f"2048-expedition-1/{e['seed']}/{e['stage']}").shuffle(pool);e['offers']=pool[:3]
    elif remaining(g)==0 or (not can_move(g.board) and not powers(g)):
        e['phase']='lost'

def choose(g,key):
    e=deepcopy(g.extra)
    if e['phase'] not in ('draft','clear') or key not in e['offers']:return False
    advancing=e['phase']=='clear';e['perks'][key]=e['perks'].get(key,0)+1
    if advancing:
        e['stage']+=1;e['stage_score']=g.score;e['stage_start']=g.moves
        # One tactical refresh at a checkpoint: remove the smallest tile. The
        # inherited board and all larger values remain part of the run.
        occupied=[i for i,v in enumerate(g.board) if v]
        if len(occupied)>1:g.board[min(occupied,key=lambda i:g.board[i])]=0
    e['phase']='play';e['offers']=[];e['freeze']=0;e['cooldown']=0;e['streak']=0
    g.extra=e;g.history=[];g.future=[]
    refresh(g);return True

def powers(g):
    e=g.extra
    if e['phase']!='play':return []
    result=[]
    if e['energy']>=5 and not e['cooldown'] and not e['freeze'] and can_move(g.board):result.append('freeze')
    if e['energy']>=swap_cost(e):
        for i in range(16):
            for j in range(i+1,16):
                if g.board[i] and g.board[j] and g.board[i]!=g.board[j]:result.append(f'swap:{i}:{j}')
    return result

def power(g,action,ai=False):
    if action not in powers(g):return None
    g.history.append(g.snapshot());g.history=g.history[-100:];g.future=[]
    e=deepcopy(g.extra);old=g.board[:];mapping={}
    if action=='freeze':e['energy']-=5;e['freeze']=2+e['perks'].get('ice',0);e['cooldown']=6
    else:
        _,i,j=action.split(':');i,j=int(i),int(j)
        g.board[i],g.board[j]=g.board[j],g.board[i];mapping={i:j,j:i};e['energy']-=swap_cost(e)
    g.extra=e;g.ai_moves+=int(ai);g.assisted=g.assisted or ai;refresh(g)
    return dict(tracks=[Track(i,mapping.get(i,i),v) for i,v in enumerate(old) if v],merges=[],spawn=None,gain=0,power=action)

@lru_cache(maxsize=24000)
def shifted(board,d):
    b,g,_,m=slide(board,d);return tuple(b),g,tuple(m)

def evaluate(board):
    logs=[log2(v) if v else 0 for v in board];empty=board.count(0)
    smooth=sum(abs(logs[i]-logs[j]) for i in range(16) for j in (i+1,i+4) if j<16 and (j!=i+1 or i//4==j//4) and board[i] and board[j])
    monotone=0
    for rows in (True,False):
        for r in range(4):
            line=[logs[r*4+c if rows else c*4+r] for c in range(4)]
            monotone+=min(sum(max(0,a-b) for a,b in zip(line,line[1:])),sum(max(0,b-a) for a,b in zip(line,line[1:])))
    corner=max(board[i] for i in (0,3,12,15))==max(board)
    return empty*170-monotone*35-smooth*5+(log2(max(board))**2)*(3 if corner else -2)

def search(board,extra,budget=.12):
    """Expectimax uses the acquired rules, weighted spawns, and energy powers.

    Each completed depth evaluates every legal direction. A deadline discards
    an incomplete iteration. Large chance nodes use a fixed spatial sample;
    this is a heuristic player, never a claimed proof or win probability.
    """
    start=perf_counter();deadline=start+max(.015,min(.5,budget));nodes=0;cache={};board=tuple(board)
    def chance(b,e,depth):
        nonlocal nodes
        nodes+=1
        if nodes%32==0 and perf_counter()>deadline:raise TimeoutError
        empty=[i for i,v in enumerate(b) if not v]
        if not empty:return player(b,e,depth)
        positions=empty if len(empty)<=5 else [empty[round(k*(len(empty)-1)/4)] for k in range(5)]
        probability=spawn_four(e);value=0.
        for i in positions:
            for tile,weight in ((2,1-probability),(4,probability)):
                child=list(b);child[i]=tile;value+=weight*player(tuple(child),e,depth)/len(positions)
        return value
    def player(b,e,depth):
        key=(b,e['streak'],e['energy'],e['freeze'],e['cooldown'],depth)
        if key in cache:return cache[key]
        if not can_move(b):return -9000+(1000 if e['energy']>=swap_cost(e) else 0)
        if depth<=0:return evaluate(b)+e['energy']*12
        best=-1e20
        for d in DIRECTIONS:
            after,gain,merges=shifted(b,d)
            if after==b:continue
            points,skip,state=reward(after,gain,merges,e)
            value=points*.7+(player(after,state,depth-1) if skip else chance(after,state,depth-1))
            best=max(best,value)
        cache[key]=best;return best
    choices={};fallback={}
    for d in DIRECTIONS:
        after,gain,merges=shifted(board,d)
        if after==board:continue
        points,skip,e=reward(after,gain,merges,extra)
        choices[d]=dict(board=list(after),gain=points,merges=len(merges),empty=max(0,after.count(0)-(not skip)),skip=skip)
        fallback[d]=evaluate(after)+points*.7+e['energy']*12
    best=fallback;depth_done=0
    try:
        for depth in range(1,5):
            values={}
            for d in choices:
                after,gain,merges=shifted(board,d);points,skip,e=reward(after,gain,merges,extra)
                values[d]=points*.7+(player(after,e,depth-1) if skip else chance(after,e,depth-1))
            best=values;depth_done=depth
            if perf_counter()>deadline:break
    except TimeoutError:pass
    needed=extra.get('_needed',float('inf'));turns=extra.get('_remaining',999)
    can_finish=any(v['gain']>=needed for v in choices.values())
    for d in best:
        if choices[d]['gain']>=needed:best[d]+=20000
        elif turns==1:best[d]-=20000
    # Powers are considered as tactical actions, with an energy opportunity
    # cost. They cannot create an infinite loop: each spends finite energy.
    g=Game(0,mode='expedition');g.board=list(board);g.extra=deepcopy(extra)
    candidates=powers(g);base=evaluate(board)
    if candidates and not can_finish:
        ranked=[]
        for action in candidates:
            if action=='freeze':continue
            _,i,j=action.split(':');b=list(board);i,j=int(i),int(j);b[i],b[j]=b[j],b[i]
            improvement=evaluate(tuple(b))-base
            if not can_move(board) or improvement>220:ranked.append((improvement,action,tuple(b)))
        if ranked:
            improvement,action,b=max(ranked)
            best[action]=max(best.values(),default=-9000)+max(1,improvement-180)
            choices[action]=dict(board=list(b),gain=0,empty=b.count(0),merges=0)
        elif 'freeze' in candidates and board.count(0)<=3:
            best['freeze']=max(best.values(),default=-9000)+1;choices['freeze']=dict(board=list(board),gain=0,empty=board.count(0),merges=0)
    # A blocked board must always be allowed to spend its remaining energy.
    if not best and candidates:
        action=candidates[0];best[action]=0;choices[action]=dict(board=list(board),gain=0,empty=0,merges=0)
    direction=max(best,key=best.get) if best else None
    explanation='按照已选能力、能量和落子概率进行搜索'
    if direction=='freeze':explanation='先暂停落子，为拥挤的棋盘争取合并空间'
    elif direction and direction.startswith('swap:'):explanation='消耗能量交换数字，改善排列后再继续合并'
    return dict(direction=direction,values=list(best.items()),choices=choices,board=list(board),nodes=nodes,depth=depth_done,
        ms=round((perf_counter()-start)*1000),backend='expedition',explanation=explanation)
