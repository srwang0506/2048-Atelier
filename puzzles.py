"""Finite, deterministic 2048 puzzles with an exact shortest-path solver."""
from collections import deque
from functools import lru_cache
from pathlib import Path
from time import perf_counter
import json,random
from engine import Game,DIRECTIONS,slide

LEVEL_PATH=Path(__file__).with_name('puzzle_levels.json')
LEVELS=json.loads(LEVEL_PATH.read_text(encoding='utf-8')) if LEVEL_PATH.exists() else []

def make_puzzle(index=0):
    level=LEVELS[index];game=Game(level['seed'],mode='puzzle')
    game.puzzle_id=index;game.board=level['board'][:];game.rng.seed(level['seed'])
    game.highest=max(game.board);return game

def spawn_draws(state,count):
    rng=random.Random();rng.setstate(state)
    return [(rng.random(),2 if rng.random()<.9 else 4) for _ in range(count)]

def place(board,draw):
    board=list(board);empty=[i for i,value in enumerate(board) if not value]
    if empty:board[empty[min(len(empty)-1,int(draw[0]*len(empty)))]]=draw[1]
    return tuple(board)

@lru_cache(maxsize=32768)
def shifted(board,direction):
    after,gain,_,_=slide(list(board),direction)
    return tuple(after),gain

def solve(board,state,target,remaining):
    """Exhaust all legal paths up to remaining turns; no heuristic or timeout.

    Puzzle spawns consume exactly two random draws per valid move, so every
    branch at the same depth shares the same draw pair. Board+depth is a safe
    visited key; the search cannot merge states with different future draws.
    """
    start=perf_counter();remaining=max(0,min(7,int(remaining)));board=tuple(board)
    draws=spawn_draws(state,remaining);nodes=0;routes={};previews={}
    if max(board)>=target:return dict(direction=None,solution=[],solvable=True,complete=True,values=[],nodes=0,depth=0,ms=0,backend='exact')
    for direction in DIRECTIONS:
        after,gain=shifted(board,direction)
        if after==board or not remaining:continue
        child=place(after,draws[0]);previews[direction]=dict(board=list(child),gain=gain)
        queue=deque([(child,(direction,),1)]);seen={(child,1)};route=None
        while queue:
            current,path,depth=queue.popleft();nodes+=1
            if max(current)>=target:route=path;break
            if depth>=remaining:continue
            for move in DIRECTIONS:
                moved,_=shifted(current,move)
                if moved==current:continue
                spawned=place(moved,draws[depth]);key=(spawned,depth+1)
                if key in seen:continue
                seen.add(key);queue.append((spawned,path+(move,),depth+1))
        routes[direction]=route
    possible=[path for path in routes.values() if path]
    solution=min(possible,key=len) if possible else None
    direction=solution[0] if solution else None
    return dict(direction=direction,solution=list(solution) if solution else [],solvable=solution is not None,
        complete=True,values=[(key,-len(path) if path else -100) for key,path in routes.items()],
        distances={key:len(path) if path else None for key,path in routes.items()},previews=previews,
        board=list(board),nodes=nodes,depth=len(solution) if solution else remaining,
        ms=round((perf_counter()-start)*1000),backend='exact',
        explanation=f'已验证：最快再走 {len(solution)} 步完成' if solution else '剩余步数内没有解法，可以撤销或重试')
