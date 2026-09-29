"""Portable desktop launcher: writable cache, one instance, useful crash logs."""
import multiprocessing
import os
import sys
import traceback
from contextlib import nullcontext
from platform_paths import user_root, prepare_data, InstanceLock, AlreadyRunning

def message(text):
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, '2048', 0x40)
    elif sys.stderr is not None:
        print(text, file=sys.stderr)

def configure_runtime():
    if sys.platform == 'win32':
        os.environ.setdefault('NUMBA_CACHE_DIR', str(user_root() / 'cache/numba'))
        os.environ.setdefault('NUMBA_THREADING_LAYER', 'workqueue')
        os.environ.setdefault('SDL_WINDOWS_DPI_AWARENESS', 'permonitorv2')
        # Set before SDL creates a window. Older APIs remain a fallback.
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError, OSError):
            try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (AttributeError, OSError): pass

def run():
    multiprocessing.freeze_support()
    configure_runtime()
    demo = '--demo' in sys.argv
    log = None
    try:
        with nullcontext() if demo else InstanceLock():
            if not demo: prepare_data()
            if sys.platform == 'win32' and not demo:
                folder = user_root() / 'logs'; folder.mkdir(parents=True, exist_ok=True)
                log = (folder / 'latest.log').open('w', encoding='utf-8', buffering=1)
                if sys.stdout is None: sys.stdout = log
                if sys.stderr is None: sys.stderr = log
            from air_ui import main
            main()
        return 0
    except AlreadyRunning as exc:
        message(str(exc)); return 0
    except Exception:
        details = traceback.format_exc()
        if log is not None: log.write(details); log.flush()
        elif sys.stderr is not None: print(details, file=sys.stderr)
        message('游戏未能启动或运行中发生错误。\n' + ('详细记录：' + str(user_root() / 'logs/latest.log') if log else '请查看启动窗口中的错误信息。'))
        return 1
    finally:
        if log is not None:
            if sys.stdout is log: sys.stdout = None
            if sys.stderr is log: sys.stderr = None
            log.close()

if __name__ == '__main__':
    raise SystemExit(run())
