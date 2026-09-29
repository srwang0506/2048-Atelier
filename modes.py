"""Independent classic/daily sessions and a read-only timeline of recent turns."""
from datetime import date
from hashlib import sha256
from engine import Game

def today():return date.today().isoformat()

def daily_game(day=None):
    day=day or today()
    if date.fromisoformat(day).isoformat()!=day:raise ValueError('Invalid date')
    seed=int.from_bytes(sha256(('2048-Atelier/daily/v1/'+day).encode()).digest()[:8],'big')
    return Game(seed,mode='daily',challenge_date=day)

def session_key(game):return 'daily:'+game.challenge_date if game.mode=='daily' else game.mode

class SessionBook:
    def __init__(self,data):
        self.data=data;raw=data.get('sessions',{});self.sessions={}
        if isinstance(raw,dict):
            fixed=('classic','puzzle','sprint','expedition','rescue')
            keys=[key for key in fixed if key in raw]+sorted((key for key in raw if key not in fixed),reverse=True)
            for key in keys:
                if len(self.sessions)>=12:break
                try:
                    game=Game.restore(raw[key])
                    if key==session_key(game):self.sessions[key]=raw[key]
                except (ValueError,TypeError,KeyError):continue
        self.sync()

    def sync(self):
        daily=sorted((key for key in self.sessions if key.startswith('daily:')),reverse=True)[:7]
        self.sessions={key:value for key,value in self.sessions.items() if key in ('classic','puzzle','sprint','expedition','rescue') or key in daily}
        self.data['sessions']=self.sessions.copy()

    def stash(self,game):self.sessions[session_key(game)]=game.serialize();self.sync()

    def switch(self,current,mode,day=None):
        if mode not in ('classic','daily','puzzle','sprint','expedition','rescue'):raise ValueError('Invalid mode')
        self.stash(current);day=day or today();key='daily:'+day if mode=='daily' else mode
        if key in self.sessions:return Game.restore(self.sessions[key])
        if mode=='expedition':
            from expedition import make_expedition
            return make_expedition()
        if mode=='rescue':raise ValueError('Choose a rescue challenge first')
        if mode=='puzzle':
            from puzzles import make_puzzle
            return make_puzzle()
        return daily_game(day) if mode=='daily' else Game(mode=mode)

def timeline(game):
    frames=[]
    for state in [*game.history,game.snapshot()]:
        board,score,moves,ai_moves,_,highest=state[:6]
        frames.append(dict(board=board[:],score=score,moves=moves,ai_moves=ai_moves,highest=highest))
    return frames
