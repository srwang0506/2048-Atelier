"""LUMINA search service: native compiled Python, isolated from the renderer."""
from time import perf_counter
import argparse,json
from collections import OrderedDict
from ai_legacy import init_tables, pack, successors, transpose

class Expectimax:
    def __init__(self):
        from search_native import NativeSearch
        self.solver=NativeSearch()
    def choose(self,board,budget=.12,max_depth=10,adaptive=False):
        from insight import enrich
        return enrich(board,self.solver.choose(board,budget,max_depth,adaptive))


def worker(requests,results):
    try:
        solver=Expectimax()
        results.put((-1,{'ready':True,'backend':'native'}))
    except Exception as exc:
        results.put((-1,{'error':f'搜索核心初始化失败：{exc}'}));return
    cache=OrderedDict()
    while True:
        task=requests.get()
        if task is None:return
        token,board,budget=task[:3];options=task[3] if len(task)>3 else {}
        try:
            if 'extract_rescue' in options:
                from rescue import extract
                results.put((token,extract(options['extract_rescue'])));continue
            if 'expedition' in options:
                from expedition import search
                results.put((token,search(board,options['expedition'],budget)));continue
            if 'rescue' in options:
                from rescue import solve
                spec=options['rescue']
                results.put((token,solve(board,spec['rng'],spec['goal'],spec['remaining'])));continue
            adaptive=options.get('adaptive',False);puzzle=options.get('puzzle')
            key=('puzzle',tuple(board),puzzle['rng'],puzzle['target'],puzzle['remaining']) if puzzle else (tuple(board),budget,adaptive)
            if key in cache and not options.get('refresh'):
                result=dict(cache.pop(key));result['cached']=True
            elif puzzle:
                from puzzles import solve
                result=solve(board,puzzle['rng'],puzzle['target'],puzzle['remaining'])
            else:result=solver.choose(board,budget,adaptive=adaptive)
            cache[key]=dict(result)
            if len(cache)>32:cache.popitem(last=False)
            results.put((token,result))
        except Exception as exc:results.put((token,{'error':str(exc)}))


def benchmark(seed,budget,limit=20000):
    from engine import Game,can_move
    solver,game=Expectimax(),Game(seed)
    start=perf_counter();depths=[];nodes=0
    while game.moves<limit and can_move(game.board):
        result=solver.choose(game.board,budget)
        if not result['direction']:break
        game.move(result['direction'],True);depths.append(result['depth']);nodes+=result['nodes']
        if game.moves%500==0:
            print(json.dumps(dict(seed=seed,moves=game.moves,score=game.score,tile=max(game.board),seconds=round(perf_counter()-start,1),depth=result['depth'])),flush=True)
    return dict(seed=seed,moves=game.moves,score=game.score,tile=max(game.board),seconds=round(perf_counter()-start,1),budget=budget,
                complete=not can_move(game.board),mean_depth=round(sum(depths)/max(1,len(depths)),2),nodes=nodes,backend='native')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=42);p.add_argument('--budget',type=float,default=.04);p.add_argument('--limit',type=int,default=20000)
    a=p.parse_args();print(json.dumps(benchmark(a.seed,a.budget,a.limit)),flush=True)
