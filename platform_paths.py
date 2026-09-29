"""User-writable Windows data and a process lock; retain existing Mac paths."""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def user_root():
    if sys.platform == 'win32':
        local = os.environ.get('LOCALAPPDATA')
        return (Path(local) if local else Path.home() / 'AppData/Local') / '2048-Atelier'
    return ROOT

def save_path(demo=False):
    return (ROOT if demo else user_root()) / 'data' / ('demo.json' if demo else 'save.json')

def export_dir():
    return user_root() / 'exports'

def prepare_data():
    """Copy old source-package saves once, without replacing profile saves."""
    target = save_path().parent
    target.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'win32' and not any((target / n).exists() for n in ('save.json', 'save.bak')):
        for name in ('save.json', 'save.bak'):
            old = ROOT / 'data' / name
            if old.is_file(): shutil.copy2(old, target / name)

class AlreadyRunning(RuntimeError):
    pass

class InstanceLock:
    """OS releases the lock after a crash; a stale file never blocks a launch."""
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else user_root() / 'data/game.lock'
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open('a+b')
        if self.path.stat().st_size == 0:
            self.handle.write(b'0'); self.handle.flush()
        self.handle.seek(0)
        try:
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close(); self.handle = None
            raise AlreadyRunning('游戏已经打开，请回到现有窗口。') from exc
        return self

    def __exit__(self, *args):
        if self.handle:
            if sys.platform == 'win32':
                import msvcrt
                self.handle.seek(0); msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close(); self.handle = None
