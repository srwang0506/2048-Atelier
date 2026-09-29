"""Deterministic 2048 rules, animation tracks and durable local saves."""
from __future__ import annotations
import json
import random
import time
import uuid
import base64
import zlib
import os
from copy import deepcopy
from pathlib import Path
from dataclasses import dataclass

DIRECTIONS = ('left', 'up', 'right', 'down')

@dataclass
class Track:
    source: int
    target: int
    value: int


def slide(board, direction):
    """Return (new board, merge points, tracks, merged positions), without spawn."""
    if direction not in DIRECTIONS:
        raise ValueError(direction)
    out, tracks, merged, score = [0] * 16, [], [], 0
    for line in range(4):
        if direction == 'left': ids = [line * 4 + c for c in range(4)]
        elif direction == 'right': ids = [line * 4 + c for c in range(3, -1, -1)]
        elif direction == 'up': ids = [r * 4 + line for r in range(4)]
        else: ids = [r * 4 + line for r in range(3, -1, -1)]
        vals = [(i, board[i]) for i in ids if board[i]]
        i = dest = 0
        while i < len(vals):
            src, value = vals[i]
            target = ids[dest]
            tracks.append(Track(src, target, value))
            if i + 1 < len(vals) and vals[i + 1][1] == value:
                tracks.append(Track(vals[i + 1][0], target, value))
                value *= 2
                score += value
                merged.append(target)
                i += 1
            out[target] = value
            dest += 1
            i += 1
    return out, score, tracks, merged


def can_move(board):
    return bool(any(board)) and (0 in board or any(board[r*4+c] == board[r*4+c+1] for r in range(4) for c in range(3)) or any(board[r*4+c] == board[(r+1)*4+c] for r in range(3) for c in range(4)))


def valid_board(board):
    return isinstance(board, list) and len(board) == 16 and all(type(v) is int and (v == 0 or v >= 2 and not v & (v-1)) for v in board)


class Game:
    def __init__(self, seed=None,mode='classic',challenge_date=None):
        self.rng = random.Random(seed)
        self.board = [0]*16
        self.score = self.moves = self.undos = self.ai_moves = 0
        self.elapsed = 0.0
        self.id = uuid.uuid4().hex
        self.history = []
        self.future = []
        self.restore_warning = None
        self.mode=mode;self.challenge_date=challenge_date;self.assisted=False;self.puzzle_id=None
        self.extra = {}
        self.highest = 2
        self.spawn(); self.spawn()
        self.highest=max(self.board)

    def spawn(self):
        empty = [i for i, v in enumerate(self.board) if not v]
        if not empty: return None
        index = empty[min(len(empty)-1,int(self.rng.random()*len(empty)))] if self.mode=='puzzle' else self.rng.choice(empty)
        probability=.1
        if self.mode=='expedition' and self.extra:
            from expedition import spawn_four
            probability=spawn_four(self.extra)
        self.board[index] = 2 if self.rng.random() < 1-probability else 4
        return index

    def move(self, direction, ai=False):
        if self.mode=='expedition':
            from expedition import power
            if self.extra['phase']!='play':return None
            if direction=='freeze' or direction.startswith('swap:'):return power(self,direction,ai)
        if self.mode=='rescue':
            if self.moves>=self.extra['limit'] or self.board.count(0)>=self.extra['goal']:return None
        if self.mode=='sprint' and self.moves>=60:return None
        if self.mode=='puzzle' and self.puzzle_id is not None:
            from puzzles import LEVELS
            level=LEVELS[self.puzzle_id]
            if self.moves>=level['limit'] or max(self.board)>=level['target']:return None
        new, gain, tracks, merges = slide(self.board, direction)
        if new == self.board: return None
        self.history.append(self.snapshot())
        self.history = self.history[-100:]
        self.future.clear()
        self.board = new
        skip=False
        if self.mode=='expedition':
            from expedition import reward
            gain,skip,self.extra=reward(self.board,gain,merges,self.extra)
        self.score += gain
        self.moves += 1
        self.ai_moves += int(ai)
        self.assisted=self.assisted or ai
        born = None if skip else self.spawn()
        self.highest = max(self.highest, max(new))
        if self.mode=='expedition':
            from expedition import refresh
            refresh(self)
        return {'tracks': tracks, 'merges': merges, 'spawn': born, 'gain': gain}

    def undo(self):
        if not self.history: return False
        self.future.append(self.snapshot())
        self.apply_snapshot(self.history.pop())
        self.undos += 1
        return True

    def redo(self):
        if not self.future:return False
        self.history.append(self.snapshot())
        self.apply_snapshot(self.future.pop())
        return True

    def snapshot(self):
        return (self.board[:],self.score,self.moves,self.ai_moves,self.rng.getstate(),self.highest)+((deepcopy(self.extra),) if self.mode in ('expedition','rescue') else ())

    def apply_snapshot(self,state):
        board,self.score,self.moves,self.ai_moves,rng,self.highest=state[:6]
        if len(state)==7:self.extra=deepcopy(state[6])
        self.board=board[:];self.rng.setstate(rng)

    def serialize(self):
        data={k: getattr(self, k) for k in ['board', 'score', 'moves', 'undos', 'ai_moves', 'elapsed', 'id', 'highest','mode','challenge_date','assisted','puzzle_id']}
        if self.mode in ('expedition','rescue'):data['extra']=deepcopy(self.extra)
        continuation=dict(rng=self.rng.getstate(),history=self.history,future=self.future)
        data['continuation']=base64.b64encode(zlib.compress(json.dumps(continuation,separators=(',',':')).encode(),1)).decode('ascii')
        return data

    @classmethod
    def restore(cls, data):
        if not isinstance(data, dict) or not valid_board(data.get('board')): raise ValueError('Invalid saved board')
        game = cls()
        game.board = data['board'][:]
        for key in ('score', 'moves', 'undos', 'ai_moves', 'highest'):
            value = data.get(key, 0)
            if type(value) is not int or value < 0: raise ValueError('Invalid saved statistic')
            setattr(game, key, value)
        elapsed = data.get('elapsed', 0)
        if not isinstance(elapsed, (int, float)) or not 0 <= elapsed < 10**9: raise ValueError('Invalid timer')
        game.elapsed = elapsed
        if isinstance(data.get('id'), str): game.id = data['id']
        game.highest=max(game.highest,max(game.board))
        game.mode=data.get('mode','classic')
        if game.mode not in ('classic','daily','puzzle','sprint','expedition','rescue'):raise ValueError('Invalid game mode')
        if game.mode=='puzzle':
            from puzzles import LEVELS
            index=data.get('puzzle_id')
            if type(index) is not int or not 0<=index<len(LEVELS):raise ValueError('Invalid puzzle')
            game.puzzle_id=index
        if game.mode=='daily':
            from datetime import date
            day=data.get('challenge_date')
            if not isinstance(day,str) or date.fromisoformat(day).isoformat()!=day:raise ValueError('Invalid challenge date')
            game.challenge_date=day
        if game.mode=='expedition':
            from expedition import validate
            game.extra=validate(data.get('extra'))
        elif game.mode=='rescue':
            from rescue import validate
            game.extra=validate(data.get('extra'))
        game.assisted=bool(data.get('assisted',game.ai_moves>0))
        if 'continuation' in data:
            try:
                encoded=data['continuation']
                if not isinstance(encoded,str) or len(encoded)>4_000_000:raise ValueError('Invalid history')
                decoder=zlib.decompressobj()
                raw=decoder.decompress(base64.b64decode(encoded,validate=True),4_000_001)
                if len(raw)>4_000_000 or not decoder.eof:raise ValueError('History too large')
                extra=json.loads(raw)
                def rng_state(value):
                    result=(value[0],tuple(value[1]),value[2]);random.Random().setstate(result);return result
                def history(items):
                    if not isinstance(items,list) or len(items)>100:raise ValueError('Invalid history')
                    result=[]
                    for row in items:
                        if len(row)!=(7 if game.mode in ('expedition','rescue') else 6) or not valid_board(row[0]) or any(type(row[i]) is not int or row[i]<0 for i in (1,2,3,5)):raise ValueError('Invalid step')
                        extra=(validate(row[6]),) if len(row)==7 else ()
                        result.append((row[0],row[1],row[2],row[3],rng_state(row[4]),row[5])+extra)
                    return result
                state=rng_state(extra['rng']);past=history(extra['history']);future=history(extra['future'])
                if len(past)+len(future)>100:raise ValueError('History too long')
                game.rng.setstate(state);game.history=past;game.future=future
            except (ValueError,TypeError,KeyError,IndexError,OverflowError,zlib.error):
                game.restore_warning='已恢复棋盘，撤销记录无法读取'
        return game


class Storage:
    def __init__(self, path):
        self.path = Path(path)
        self.error = None
        self.notice = None
        self.data = {'best': 0, 'records': [], 'achievements': [], 'settings': {}}
        try:
            loaded = json.loads(self.path.read_text('utf-8'))
            if not isinstance(loaded, dict): raise ValueError('Invalid save')
            self.data.update(loaded)
            if type(self.data['best']) is not int or self.data['best'] < 0: raise ValueError('Invalid best')
            if not isinstance(self.data['records'], list): raise ValueError('Invalid records')
            if not isinstance(self.data['achievements'], list): raise ValueError('Invalid achievements')
            if not isinstance(self.data['settings'], dict): raise ValueError('Invalid settings')
            if 'game' in self.data:Game.restore(self.data['game'])
            rows=self.data['records'];achievements=self.data['achievements']
            self.data['records']=[r for r in rows if isinstance(r,dict) and isinstance(r.get('id'),str) and all(type(r.get(k)) is int and r[k]>=0 for k in ('score','tile','moves')) and isinstance(r.get('date',''),str)]
            self.data['achievements']=sorted(set(v for v in achievements if type(v) is int and v>=2 and not v&(v-1)))
            if len(rows)!=len(self.data['records']) or len(achievements)!=len(self.data['achievements']):self.notice='已修复异常战绩，当前棋盘不受影响'
        except FileNotFoundError:
            backup=self.path.with_suffix('.bak')
            if self.path.suffix!='.bak' and backup.exists():
                recovered=Storage(backup)
                if not recovered.error:
                    self.data=recovered.data;self.notice='主存档缺失，已从备份恢复进度'
        except (OSError, ValueError, TypeError):
            self.data = {'best': 0, 'records': [], 'achievements': [], 'settings': {}}
            self.error = '存档无法读取，已开启新游戏'
            backup=self.path.with_suffix('.bak')
            if self.path.suffix!='.bak' and backup.exists():
                recovered=Storage(backup)
                if not recovered.error:
                    self.data=recovered.data;self.error=None;self.notice='已从上一次备份恢复进度'

    def save(self, game, settings):
        self.data['game'] = game.serialize()
        self.data['settings'] = settings
        if game.mode not in ('puzzle','sprint','expedition','rescue'):self.data['best'] = max(self.data['best'], game.score)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix('.tmp')
            # Retain the last readable save. A damaged original must never replace
            # a useful backup before recovery has completed.
            if self.path.exists():
                previous=self.path.read_bytes()
                try:
                    decoded=json.loads(previous)
                    if not isinstance(decoded,dict) or ('game' in decoded and not valid_board(decoded['game'].get('board'))):raise ValueError('Invalid game')
                    if type(decoded.get('best',0)) is not int or decoded.get('best',0)<0:raise ValueError('Invalid best')
                    if not isinstance(decoded.get('settings',{}),dict) or not isinstance(decoded.get('records',[]),list) or not isinstance(decoded.get('achievements',[]),list):raise ValueError('Invalid metadata')
                    if 'game' in decoded:Game.restore(decoded['game'])
                except (ValueError,TypeError,AttributeError):pass
                else:
                    bak_tmp=self.path.with_suffix('.bak.tmp');bak_tmp.write_bytes(previous);bak_tmp.replace(self.path.with_suffix('.bak'))
            with tmp.open('w',encoding='utf-8') as handle:
                handle.write(json.dumps(self.data,ensure_ascii=False,indent=2));handle.flush();os.fsync(handle.fileno())
            tmp.replace(self.path)
            self.error=None
            return True
        except OSError:
            self.error = '存档未能写入，请检查磁盘空间或权限'
            return False

    def record(self, game):
        if not game.moves or game.mode in ('puzzle','sprint','expedition','rescue'): return
        rows = [r for r in self.data['records'] if isinstance(r, dict) and r.get('id') != game.id]
        rows.append({'id': game.id, 'score': game.score, 'tile': max(game.board), 'moves': game.moves,
                     'ai': game.ai_moves > 0, 'assisted':game.assisted,'mode':game.mode,'challenge_date':game.challenge_date,
                     'undos': game.undos, 'date': time.strftime('%m.%d %H:%M')})
        self.data['records'] = sorted(rows, key=lambda r: r.get('score', 0), reverse=True)[:20]
