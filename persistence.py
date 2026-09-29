"""Coalesced saves: capture a turn now, compress and sync it off the render thread."""
from concurrent.futures import ThreadPoolExecutor
import random
from copy import deepcopy
from engine import Game,Storage


class SaveService:
    def __init__(self,path):
        self.path=path;self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='2048-save')
        self.future=None;self.pending=None

    def submit(self,game,settings,metadata):
        # Past turns are immutable. Copy their container, and isolate the live
        # board and RNG so subsequent moves cannot alter the queued checkpoint.
        frozen=object.__new__(Game);frozen.__dict__=game.__dict__.copy()
        frozen.extra=deepcopy(getattr(game,'extra',{}))
        frozen.board=game.board[:];frozen.history=game.history[:];frozen.future=game.future[:]
        frozen.rng=random.Random();frozen.rng.setstate(game.rng.getstate())
        data=metadata.copy();data['records']=[row.copy() for row in data['records']]
        data['achievements']=data['achievements'][:]
        self.pending=(frozen,settings.copy(),data)
        self._dispatch()

    def _dispatch(self):
        if self.future is None and self.pending is not None:
            args=self.pending;self.pending=None
            self.future=self.executor.submit(self._write,*args)

    def _write(self,game,settings,data):
        writer=object.__new__(Storage);writer.path=self.path;writer.data=data;writer.error=None;writer.notice=None
        try:
            return None if writer.save(game,settings) else writer.error
        except (OSError,ValueError,TypeError):return '存档未能写入，请检查磁盘空间或权限'

    def poll(self):
        completed=[]
        if self.future is not None and self.future.done():
            completed.append(self.future.result());self.future=None
        self._dispatch();return completed

    def close(self):
        completed=[]
        while self.future is not None or self.pending is not None:
            self._dispatch()
            self.future.result();completed.extend(self.poll())
        self.executor.shutdown(wait=True)
        return completed
