"""Probability-weighted expectimax. No look-ahead into the game's RNG."""
from __future__ import annotations
from array import array
from time import perf_counter
import argparse
import json

LEFT = RIGHT = HEUR = None
MASK = 0xFFFF


def init_tables():
    global LEFT, RIGHT, HEUR
    if LEFT is not None: return
    LEFT, RIGHT, HEUR = array('H', [0])*65536, array('H', [0])*65536, array('d', [0])*65536
    for row in range(65536):
        line = [(row >> (4*i)) & 15 for i in range(4)]
        packed = [v for v in line if v]
        merged, i, merges = [], 0, 0
        while i < len(packed):
            v = packed[i]
            if i+1 < len(packed) and packed[i+1] == v:
                v = min(v+1, 15); i += 1; merges += 1
            merged.append(v); i += 1
        value = sum(v << (i*4) for i,v in enumerate(merged))
        LEFT[row] = value
        reverse = sum(v << ((3-i)*4) for i,v in enumerate(line))
        RIGHT[reverse] = sum(((value >> (i*4)) & 15) << ((3-i)*4) for i in range(4))
        ascending = descending = 0.0
        for a,b in zip(line, line[1:]):
            delta = a**4 - b**4
            if delta > 0: descending += delta
            else: ascending -= delta
        # Prefer open lanes, adjacent pairs and monotone rows/columns.
        HEUR[row] = 200000 + 270*line.count(0) + 700*merges - 47*min(ascending, descending) - 11*sum(v**3.5 for v in line)


def pack(board):
    return sum(min(v.bit_length()-1, 15) << (i*4) for i,v in enumerate(board) if v)


def transpose(b):
    a = b & 0xF0F00F0FF0F00F0F
    c = b & 0x0000F0F00000F0F0
    d = b & 0x0F0F00000F0F0000
    x = a | (c << 12) | (d >> 12)
    return (x & 0xFF00FF0000FF00FF) | ((x & 0x00FF00FF00000000) >> 24) | ((x & 0x00000000FF00FF00) << 24)


def horizontal(b, table):
    return table[b & MASK] | (table[(b >> 16) & MASK] << 16) | (table[(b >> 32) & MASK] << 32) | (table[(b >> 48) & MASK] << 48)


def successors(b):
    t = transpose(b)
    return (horizontal(b, LEFT), transpose(horizontal(t, LEFT)), horizontal(b, RIGHT), transpose(horizontal(t, RIGHT)))


def evaluate(b):
    t = transpose(b)
    h = HEUR
    return h[b & MASK]+h[(b>>16)&MASK]+h[(b>>32)&MASK]+h[(b>>48)&MASK]+h[t&MASK]+h[(t>>16)&MASK]+h[(t>>32)&MASK]+h[(t>>48)&MASK]


class SearchExpired(Exception): pass


class Expectimax:
    def __init__(self):
        init_tables()
        self.nodes = 0
        self.cache = {}

    def chance(self, b, depth, probability):
        self.nodes += 1
        if self.nodes & 255 == 0 and perf_counter() > self.deadline: raise SearchExpired()
        if depth <= 0 or probability < self.cutoff: return evaluate(b)
        key = (b, depth, round(probability, 9))
        cached = self.cache.get(key)
        if cached is not None: return cached
        empty = [shift for shift in range(0,64,4) if not (b >> shift) & 15]
        if not empty: return self.player(b, depth, probability)
        p = probability / len(empty)
        result = 0.0
        for shift in empty:
            result += .9*self.player(b | (1 << shift), depth, p*.9)
            result += .1*self.player(b | (2 << shift), depth, p*.1)
        result /= len(empty)
        self.cache[key] = result
        return result

    def player(self, b, depth, probability):
        best = -1e12
        for new in successors(b):
            if new != b:
                value = self.chance(new, depth-1, probability)
                if value > best: best = value
        return best

    def choose(self, board, budget=.12, max_depth=7):
        from engine import DIRECTIONS, slide
        # Bitboard uses four-bit ranks. Preserve correct unlimited game rules beyond 32768.
        if max(board) >= 32768:
            rows = [(d, slide(board,d)[0]) for d in DIRECTIONS]
            rows = [(d,b) for d,b in rows if b != board]
            if not rows: return {'direction': None, 'depth': 0, 'nodes': 0, 'ms': 0, 'values': []}
            d,b = max(rows, key=lambda r: self.fallback(r[1]))
            return {'direction':d, 'depth':1, 'nodes':len(rows), 'ms':0, 'values':[]}
        started = perf_counter()
        self.deadline = started + budget
        self.nodes, self.cache, self.cutoff = 0, {}, .0005
        b = pack(board)
        legal = [(i,n) for i,n in enumerate(successors(b)) if n != b]
        if not legal: return {'direction': None, 'depth':0, 'nodes':0, 'ms':0, 'values':[]}
        values = [(i,evaluate(n)) for i,n in legal]
        completed = 0
        for depth in range(1, max_depth+1):
            try:
                current = [(i,self.chance(n,depth,1.0)) for i,n in legal]
            except SearchExpired: break
            values, completed = current, depth
            if perf_counter() >= self.deadline: break
        best = max(values, key=lambda row: row[1])[0]
        return {'direction':DIRECTIONS[best], 'depth':completed, 'nodes':self.nodes,
                'ms':round((perf_counter()-started)*1000), 'values':[(DIRECTIONS[i],v) for i,v in values]}

    @staticmethod
    def fallback(board):
        ranks = [v.bit_length()-1 if v else 0 for v in board]
        mono = 0
        for line in [ranks[i:i+4] for i in range(0,16,4)]+[ranks[i::4] for i in range(4)]:
            mono += min(sum(max(0,a**4-b**4) for a,b in zip(line,line[1:])),sum(max(0,b**4-a**4) for a,b in zip(line,line[1:])))
        return 540*ranks.count(0)-47*mono


def worker(requests, results):
    solver = Expectimax()
    while True:
        task = requests.get()
        if task is None: return
        token, board, budget = task
        try: results.put((token, solver.choose(board,budget)))
        except Exception as exc: results.put((token, {'error':str(exc)}))


def benchmark(seed, budget, limit=20000):
    from engine import Game, can_move
    solver, game = Expectimax(), Game(seed)
    start = perf_counter()
    while game.moves < limit and can_move(game.board):
        result = solver.choose(game.board,budget)
        if not result['direction']: break
        game.move(result['direction'],True)
        if game.moves % 250 == 0:
            print(json.dumps({'seed':seed,'moves':game.moves,'score':game.score,'tile':max(game.board),'seconds':round(perf_counter()-start,1)}),flush=True)
    return {'seed':seed,'moves':game.moves,'score':game.score,'tile':max(game.board),'seconds':round(perf_counter()-start,1),'budget':budget,'complete':not can_move(game.board)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=2048)
    parser.add_argument('--budget',type=float,default=.06)
    parser.add_argument('--limit',type=int,default=20000)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.seed,args.budget,args.limit)),flush=True)
