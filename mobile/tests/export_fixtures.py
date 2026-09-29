"""Export public puzzle/practice data and deterministic desktop parity fixtures."""
import json,sys,random
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'work/2048-Atelier'))
from engine import Game,slide
from expedition import make_expedition,choose,reward
def state(r):
    s=r.getstate()[1]
    return dict(mt=list(s[:-1]),index=s[-1])
practice=json.loads((root.parent/'work/2048-Atelier/rescue_practice.json').read_text())
for c in practice:
    g=Game.restore(c['origin']);c['origin']=dict(board=g.board,rng=state(g.rng))
(root/'dist/rescue-practice.json').write_text(json.dumps(practice,ensure_ascii=False,separators=(',',':')))
r=random.Random(42)
fixtures={'random':[],'slides':[],'moves':[],'reward':[]}
for seed in [0,1,42,515882052,2**53+17,2**64-1]:
    rng=random.Random(seed)
    fixtures['random'].append(dict(seed=str(seed),floats=[rng.random() for _ in range(20)]))
for n in range(100):
    board=[r.choice([0,0,2,4,8,16,32,64,128,32768,65536]) for _ in range(16)]
    for d in ['left','up','right','down']:
        b,g,t,m=slide(board,d)
        fixtures['slides'].append(dict(board=board,direction=d,after=b,gain=g,merges=m,tracks=[vars(x) for x in t]))
for mode in ['classic','puzzle','sprint']:
    g=Game(42,mode=mode);initial=dict(board=g.board[:],rng=state(g.rng))
    rows=[]
    for i in range(100):
        d=r.choice(['left','up','right','down']);res=g.move(d)
        rows.append(dict(direction=d,changed=res is not None,board=g.board[:],score=g.score,moves=g.moves,rng=state(g.rng)))
    fixtures['moves'].append(dict(mode=mode,initial=initial,rows=rows))
e=make_expedition(42).extra
for n in range(100):
    e['perks']={k:r.randint(1,2) for k in ['combo','battery','gambit','corner','echo','flow'] if r.random()<.7}
    e.update(streak=r.randint(0,5),energy=r.randint(0,12),freeze=r.randint(0,4),cooldown=r.randint(0,6))
    b=[r.choice([0,2,4,8,16,32]) for _ in range(16)]
    after,gain,_,merges=slide(b,'left');points,skip,e2=reward(after,gain,merges,e)
    fixtures['reward'].append(dict(board=after,gain=gain,merges=merges,extra=e.copy(),points=points,skip=skip,after=e2))
(root/'tests/desktop-fixtures.json').write_text(json.dumps(fixtures,separators=(',',':')))
print('Exported 12 public puzzles, 3 rescue practices and desktop parity fixtures.')
