import sys,os,argparse,time,json,statistics
from pathlib import Path
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy';os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier

def main():
 a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.sound=False;a.focused=True
 samples=[];builds=a.tile_builds
 try:
  a.draw()
  for n in range(20):
   a.animation=None;a.effects.clear();a.game.board=[0,0,0,2,0,0,0,4,0,0,0,8,0,0,0,16]
   a.move('left');anim=a.animation.copy()
   for f in range(42):
    a.animation=dict(anim,start=time.monotonic()-f/120)
    t=time.perf_counter();a.update(1/120);a.draw();samples.append((time.perf_counter()-t)*1000)
  report=dict(n=len(samples),mean_ms=round(statistics.mean(samples),2),p95_ms=round(sorted(samples)[int(len(samples)*.95)-1],2),max_ms=round(max(samples),2),over_16_ms=sum(t>16.67 for t in samples),material_builds_during_animation=a.tile_builds-builds,input_lock_ms=round(anim['duration']*1000))
  dest=root/'validation/v6';dest.mkdir(exist_ok=True)
  (dest/'before.json').write_text((Path(__file__).resolve().parent/'before.json').read_text())
  (dest/'after.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 finally:
  a.requests.put(None);a.process.join(timeout=1)
  if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
  pg.quit()
if __name__=='__main__':main()
