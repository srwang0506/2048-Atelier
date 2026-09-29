import argparse,json,os,statistics,sys,time
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier
from motion import FramePacer

def stats(data):
 return dict(n=len(data),mean_ms=round(statistics.mean(data),2),p95_ms=round(sorted(data)[int(len(data)*.95)-1],2),max_ms=round(max(data),2))

def main():
 autoplay='--auto' in sys.argv
 a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
 a.new_game();a.game.board=[2,4,8,0,2,8,0,0,4,0,0,0,0,0,0,0];a.sound=False;a.motion=True
 refresh=pg.display.get_current_refresh_rate() or 120
 meta=dict(driver=pg.display.get_driver(),reported_refresh=pg.display.get_current_refresh_rate(),desktop_refresh=pg.display.get_desktop_refresh_rates(),vsync=pg.display.is_vsync(),window=a.screen.get_size())
 print(json.dumps(meta),flush=True)
 intervals=[];render=[];deltas=[];compute=[];slow=[];move_intervals=[];last_move=None;last_moves=0;last=None;direction=0;flip_ms=[0.]
 if autoplay:a.auto=True;a.speed=1;a.quality=1
 real_flip=pg.display.flip
 def measured_flip():
  t=time.perf_counter();real_flip();flip_ms[0]=(time.perf_counter()-t)*1000
 pg.display.flip=measured_flip
 pacer=FramePacer(refresh);start=time.monotonic();next_move=start+.7
 try:
  a.draw()
  while time.monotonic()-start<9:
   dt=pacer.tick(wait=not pg.display.is_vsync());now=time.monotonic();a.events()
   if not autoplay and now>=next_move:
    if a.ended:a.new_game()
    a.move(['left','down','right','up'][direction%4]);direction+=1;next_move+=.23
   t=time.perf_counter();a.update(dt);a.draw();end=time.perf_counter()
   if a.game.moves!=last_moves:
    if last_move is not None:move_intervals.append((now-last_move)*1000)
    last_move=now;last_moves=a.game.moves
   if now-start>1:
    if last is not None:intervals.append((end-last)*1000)
    render.append((end-t)*1000);deltas.append(dt*1000);compute.append((end-t)*1000-flip_ms[0])
    if (end-t)*1000>25:slow.append(dict(at=round(now-start,3),frame_ms=round((end-t)*1000,2),flip_ms=round(flip_ms[0],2),focused=a.focused,active=pg.display.get_active()))
   last=end
  report=dict(**meta,autoplay=autoplay,present_intervals=stats(intervals),update_and_draw=stats(render),computation_without_flip=stats(compute),frame_start_intervals=stats(deltas),moves=a.game.moves,move_intervals=stats(move_intervals) if move_intervals else None,late_presentations=sum(v>1500/refresh for v in intervals),slow=slow)
  previous=root/'validation/v6'/('native-auto.json' if autoplay else 'native.json')
  if previous.exists():previous.rename(previous.with_name('native-previous-'+str(time.time_ns())+'.json'))
  previous.write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
 finally:
  a.requests.put(None);a.process.join(timeout=1)
  if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
  pg.quit()
if __name__=='__main__':main()
