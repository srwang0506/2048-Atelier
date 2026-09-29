"""Native-compiled Python expectimax with 80-bit boards and exact-key TT."""
import math
from time import perf_counter
import numpy as np
from numba import njit, objmode

U=np.uint64
RM=U((1<<20)-1)

@njit(cache=True)
def build_tables():
    left=np.zeros(1<<20,np.uint32)
    right=np.zeros(1<<20,np.uint32)
    heur=np.zeros(1<<20,np.float64)
    for row in range(1<<20):
        line=np.empty(4,np.int64)
        packed=np.zeros(4,np.int64)
        count=0
        for i in range(4):
            line[i]=(row>>(i*5))&31
            if line[i]:packed[count]=line[i];count+=1
        i=0;j=0;result=0;merges=0
        while i<count:
            rank=packed[i]
            if i+1<count and packed[i+1]==rank:
                rank=min(31,rank+1);i+=1;merges+=2
            result|=rank<<(j*5);i+=1;j+=1
        left[row]=result
        reverse=0;reverse_result=0
        for i in range(4):
            reverse|=line[i]<<((3-i)*5)
            reverse_result|=((result>>(5*i))&31)<<((3-i)*5)
        right[reverse]=reverse_result
        increasing=0.;decreasing=0.;power_sum=0.
        for i in range(4):power_sum+=line[i]**3.5
        for i in range(3):
            delta=float(line[i]**4-line[i+1]**4)
            increasing+=max(0.,delta);decreasing+=max(0.,-delta)
        heur[row]=200000.+270.*(4-count)+700.*merges-47.*min(increasing,decreasing)-11.*power_sum
    return left,right,heur

@njit(inline='always')
def transpose(lo,hi):
    lo=U(lo);hi=U(hi)
    a=U(0);b=U(0)
    for r in range(4):
        for c in range(4):
            i=r*4+c
            v=((lo if i<8 else hi)>>U((i%8)*5))&U(31)
            j=c*4+r
            if j<8:a|=v<<U(j*5)
            else:b|=v<<U((j-8)*5)
    return a,b

@njit(inline='always')
def move(lo,hi,d,left,right):
    lo=U(lo);hi=U(hi)
    if d==1 or d==3:lo,hi=transpose(lo,hi)
    table=left if d<2 else right
    a=U(table[int(lo&RM)])|(U(table[int((lo>>U(20))&RM)])<<U(20))
    b=U(table[int(hi&RM)])|(U(table[int((hi>>U(20))&RM)])<<U(20))
    if d==1 or d==3:a,b=transpose(a,b)
    return a,b

@njit(inline='always')
def evaluate(lo,hi,heur):
    lo=U(lo);hi=U(hi)
    a,b=transpose(lo,hi)
    return (heur[int(lo&RM)]+heur[int((lo>>U(20))&RM)]+heur[int(hi&RM)]+heur[int((hi>>U(20))&RM)]
            +heur[int(a&RM)]+heur[int((a>>U(20))&RM)]+heur[int(b&RM)]+heur[int((b>>U(20))&RM)])

# Recursive functions intentionally compile once per worker, without disk caching.
# LLVM recursion symbols must not be reused from another process's cache.
@njit
def search(lo,hi,depth,prob,cutoff,left,right,heur,keys,depths,probs,values,ages,generation,stats,deadline):
    stats[0]+=1
    if stats[0]%4096==0:
        with objmode(now='float64'):
            now=perf_counter()
        if now>deadline:
            stats[3]=1
            return 0.
    if stats[3]:return 0.
    if depth<=0 or prob<cutoff:return evaluate(lo,hi,heur)
    hashed=lo^(hi*U(0x9E3779B97F4A7C15))^(U(depth)*U(0xD6E8FEB86659FD93))
    hashed^=hashed>>U(32)
    slot=int(hashed&U(len(ages)-1))
    if ages[slot]==generation and keys[slot,0]==lo and keys[slot,1]==hi and depths[slot]==depth and probs[slot]==prob:
        stats[1]+=1
        return values[slot]
    empties=np.empty(16,np.int64);count=0
    for i in range(16):
        if (((lo if i<8 else hi)>>U((i%8)*5))&U(31))==0:
            empties[count]=i;count+=1
    if count==0:return evaluate(lo,hi,heur)
    total=0.;next_prob=prob/count
    for e in range(count):
        pos=empties[e];shift=U((pos%8)*5)
        for rank in range(1,3):
            weight=.9 if rank==1 else .1
            a=lo|(U(rank)<<shift) if pos<8 else lo
            b=hi|(U(rank)<<shift) if pos>=8 else hi
            # Terminal value zero, relative to the positive living-board baseline.
            # Keeps the loss penalty finite instead of swamping tiny-probability branches.
            best=0.
            valid=False
            for d in range(4):
                aa,bb=move(a,b,d,left,right)
                if aa!=a or bb!=b:
                    value=search(aa,bb,depth-1,next_prob*weight,cutoff,left,right,heur,keys,depths,probs,values,ages,generation,stats,deadline)
                    if stats[3]:return 0.
                    if not valid or value>best:best=value
                    valid=True
            total+=weight*best
    result=total/count
    keys[slot,0]=lo;keys[slot,1]=hi;depths[slot]=depth;probs[slot]=prob
    values[slot]=result;ages[slot]=generation
    return result

@njit
def root_search(lo,hi,depth,cutoff,left,right,heur,keys,depths,probs,values,ages,generation,stats,deadline,order):
    scores=np.full(4,-np.inf)
    for index in range(4):
        d=order[index]
        a,b=move(lo,hi,d,left,right)
        if a!=lo or b!=hi:
            scores[d]=search(a,b,depth,1.,cutoff,left,right,heur,keys,depths,probs,values,ages,generation,stats,deadline)
            if stats[3]:break
    return scores


def pack(board):
    ranks=[v.bit_length()-1 if v else 0 for v in board]
    if any(v>30 for v in ranks):raise ValueError('Maximum supported rank is 30')
    return U(sum(v<<(5*i) for i,v in enumerate(ranks[:8]))),U(sum(v<<(5*i) for i,v in enumerate(ranks[8:])))


class NativeSearch:
    def __init__(self):
        self.left,self.right,self.heur=build_tables()
        n=1<<19
        self.keys=np.zeros((n,2),np.uint64)
        self.depths=np.zeros(n,np.int16)
        self.probs=np.zeros(n,np.float64)
        self.values=np.zeros(n,np.float64)
        self.ages=np.zeros(n,np.uint32)
        self.generation=0
        self.stats=np.zeros(4,np.int64)
        self.choose([2,2]+[0]*14,.01,max_depth=1)

    def choose(self,board,budget=.12,max_depth=10,adaptive=False):
        from engine import DIRECTIONS
        lo,hi=pack(board)
        self.generation+=1
        self.stats[:]=0
        started=perf_counter()
        empty=board.count(0)
        soft=budget*(.35 if empty>=8 else .65 if empty>=5 else 1.) if adaptive else budget
        hard=budget*(.75 if empty>=8 else 1.25 if empty>=5 else 2. if empty>=3 else 2.5) if adaptive else budget
        hard=min(.35,hard) if adaptive else hard
        deadline=started+hard
        # Search rare branches more carefully in tight endgames.
        cutoff=.00015 if board.count(0)>=5 else .000035
        completed=0
        scores=None;order=np.arange(4,dtype=np.int64);last_best=-1;stable=0
        for depth in range(1,max_depth+1):
            candidate=root_search(lo,hi,depth,cutoff,self.left,self.right,self.heur,self.keys,self.depths,self.probs,self.values,self.ages,self.generation,self.stats,deadline,order)
            if self.stats[3]:break
            scores=candidate;completed=depth
            winner=int(np.argmax(scores));stable=stable+1 if winner==last_best else 1;last_best=winner
            order=np.argsort(-scores,kind='stable').astype(np.int64)
            finite=scores[np.isfinite(scores)]
            # Require agreement across complete depths. Every displayed direction
            # still comes from a fully evaluated root, never a partial iteration.
            if adaptive and stable>=2 and perf_counter()-started>=soft:break
            if len(finite)==0 or (adaptive and len(finite)==1):break
            if perf_counter()>=deadline:break
        if scores is None:
            scores=np.full(4,-np.inf)
            for d in range(4):
                a,b=move(lo,hi,d,self.left,self.right)
                if a!=lo or b!=hi:scores[d]=evaluate(a,b,self.heur)
        legal=[(DIRECTIONS[i],float(scores[i])) for i in range(4) if np.isfinite(scores[i])]
        direction=max(legal,key=lambda item:item[1])[0] if legal else None
        return dict(direction=direction,depth=completed,nodes=int(self.stats[0]),hits=int(self.stats[1]),
                    ms=round((perf_counter()-started)*1000),values=legal,backend='native',cutoff=cutoff,
                    adaptive=adaptive,stable_depths=stable,budget_ms=round(hard*1000))
