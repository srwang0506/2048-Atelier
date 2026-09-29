import os,sys,json,statistics,time,argparse,tempfile
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier
from motion import FramePacer
from engine import Storage,Game

def stats(samples):
 return {'frames':len(samples),'mean_ms':round(statistics.mean(samples),2),'p95_ms':round(sorted(samples)[int(len(samples)*.95)-1],2),'max_ms':round(max(samples),2)}

def main():
 a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.new_game();a.sound=False;a.motion=True;a.auto=True;a.quality=1;a.speed=1
 refresh=pg.display.get_current_refresh_rate() or 120;pacer=FramePacer(refresh);groups={};compute={};last=None;stages=set();flip=[0.];real_flip=pg.display.flip
 def measured_flip():
  t=time.perf_counter();real_flip();flip[0]=(time.perf_counter()-t)*1000
 pg.display.flip=measured_flip
 with tempfile.TemporaryDirectory(prefix='.2048-verify-',dir='/Volumes/sirui/2048-Atelier') as d:
  a.store=Storage(Path(d)/'save.json');a.args.demo=False;a.save();a.draw();start=time.monotonic()
  try:
   while time.monotonic()-start<11:
    dt=pacer.tick(wait=not pg.display.is_vsync());now=time.monotonic();age=now-start;a.events()
    action=None
    for stamp,key in [(4,'settings'),(5,'close'),(6,'intelligence'),(6.4,'inspect_hint'),(7.4,'close'),(8,'auto')]:
     if age>=stamp and stamp not in stages:stages.add(stamp);action=key;break
    t=time.perf_counter()
    if action:a.act(action)
    a.update(dt);a.draw();end=time.perf_counter()
    group='panel_open' if action in ('settings','intelligence') else 'panel_motion' if 0<a.modal_progress<1 else 'panel_idle' if a.modal else 'play'
    if age>1:
     if last is not None:groups.setdefault(group,[]).append((end-last)*1000)
     compute.setdefault(group,[]).append((end-t)*1000-flip[0])
    last=end
   a.stop_auto();a.save();a.flush_save();restored=Game.restore(Storage(a.store.path).data['game'])
   assert restored.board==a.game.board and restored.rng.getstate()==a.game.rng.getstate()
   report={'driver':pg.display.get_driver(),'refresh':refresh,'vsync':pg.display.is_vsync(),'present':{k:stats(v) for k,v in groups.items()},'compute':{k:stats(v) for k,v in compute.items()},'saved_steps':restored.moves,'restored_history':len(restored.history),'restored_rng':True}
   (root/'validation/v7/native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
  finally:
   a.flush_save();a.requests.put(None);a.process.join(timeout=1)
   if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
   pg.quit()
if __name__=='__main__':main()
