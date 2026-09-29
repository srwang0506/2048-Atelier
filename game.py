"""2048 desktop entry point."""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
if __name__=='__main__':
    from desktop_start import run
    raise SystemExit(run())
else:
    from air_ui import Atelier,main,W,H,S,BX,BY,BS,CELL
