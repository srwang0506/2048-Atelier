"""Record real desktop v12 actions using an isolated, temporary player profile.
SDL dummy captures the desktop renderer; this is not Windows device footage.
Pass DESKTOP_SOURCE to the desktop source folder, optionally CAPTURE_OUT.
"""
import os,sys,argparse,time,tempfile,json,shutil
from pathlib import Path
os.environ.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYGAME_HIDE_SUPPORT_PROMPT='1',NUMBA_CACHE_DIR='/private/tmp/lumina-docs-numba',PYTHONDONTWRITEBYTECODE='1')
root=Path(os.environ.get('DESKTOP_SOURCE',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(root))
import pygame as pg
from PIL import Image
from game import Atelier
from engine import Game,Storage,DIRECTIONS
from modes import SessionBook,daily_game
from puzzles import make_puzzle,LEVELS
from expedition import make_expedition
from rescue import make_rescue
out=Path(os.environ.get('CAPTURE_OUT',Path(__file__).resolve().parents[1]/'captures'));out.mkdir(parents=True,exist_ok=True)

def main():
 a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.sound=False;a.coach=False;a.motion=True;a.quality=0;a.speed=1
 with tempfile.TemporaryDirectory(prefix='lumina-doc-profile-') as profile:
  a.store=Storage(Path(profile)/'save.json');a.store.data.update(sprint_best={},puzzle_progress={});a.sessions=SessionBook(a.store.data)
  a.progress={};a.rescue_results={};a.expedition_records=[];a.args.demo=False
  a.activate_game(Game(42));a.sessions.stash(a.game);a.toasts=[]
  name='';frame=0;events=[]
  def start(n):
   nonlocal name,frame,events
   a.stop_auto();a.cancel_input();a.toasts=[];name=n;frame=0;events=[];shutil.rmtree(out/name,ignore_errors=True);(out/name).mkdir(exist_ok=True)
  def hold(seconds):
   nonlocal frame
   for _ in range(round(seconds*12)):
    now=time.monotonic();pg.event.pump();a.update(1/12);a.draw()
    surf=pg.transform.smoothscale(a.capture_surface(),(1080,820))
    im=Image.frombytes('RGB',surf.get_size(),pg.image.tobytes(surf,'RGB'))
    im.save(out/name/f'{frame:05}.jpg',quality=92,subsampling=0)
    if frame==0:im.save(out/(name+'-poster.png'))
    frame+=1;time.sleep(max(0,1/12-(time.monotonic()-now)))
  def action(k,seconds=.9):
   a.act(k);events.append(dict(frame=frame,action=k,mode=a.game.mode,moves=a.game.moves,score=a.game.score));hold(seconds)
  def move(d,seconds=.8):
   before=a.game.moves;a.move(d);events.append(dict(frame=frame,action=d,mode=a.game.mode,moves=a.game.moves,score=a.game.score,changed=a.game.moves!=before));hold(seconds)
  def finish():
   meta=dict(name=name,fps=12,frames=frame,duration=frame/12,source='Python desktop v12 / macOS / SDL dummy renderer',events=events,final=dict(mode=a.game.mode,moves=a.game.moves,score=a.game.score,assisted=a.game.assisted))
   (out/(name+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(name,frame,meta['final'],flush=True)
  try:
   # Warm up the real background AI, without creating a substituted result.
   until=time.monotonic()+60
   while not a.ai_ready and time.monotonic()<until:a.update(.02);time.sleep(.02)
   assert a.ai_ready,'AI initialization timeout'
   start('10-desktop-lobby');action('lobby',1.5);action('tab_featured',2);action('tab_classic',1.5);action('mode_classic',1);finish()
   a.activate_game(Game(42));start('11-desktop-classic');hold(1)
   for d in ['left','down','left','up','right']:move(d)
   action('undo');action('redo');finish()
   start('12-desktop-ai-replay');action('intelligence',2);assert a.ai_result and a.ai_result.get('choices'),'No real AI analysis';action('preview_left',1);action('close',.5);action('step',1.5);action('replay',1);action('replay_first',.5);action('replay_play',2);finish();a.act('close')
   a.activate_game(make_puzzle(0));start('13-desktop-puzzle');hold(1.5)
   for d in LEVELS[0]['solution']:move(d,1.2)
   assert max(a.game.board)>=LEVELS[0]['target'];hold(1.5);finish()
   a.activate_game(make_expedition(13));start('14-desktop-expedition');hold(1.5);action('perk_battery',1)
   for d in ['left','down','left','up','right','down']:move(d,.7)
   action('expedition_rules',1.5);finish();a.act('close')
   c=a.practice[0];a.activate_game(make_rescue(c));start('15-desktop-rescue');hold(1.5)
   for d in c['solution']:move(d,1)
   assert a.game.board.count(0)>=3;action('rescue_review',1);action('review_next',.7);action('review_next',.7);finish();a.act('close')
   a.activate_game(daily_game('2026-09-29'));start('16-desktop-daily');hold(1.5)
   for d in ['left','down','left','up']:move(d)
   action('undo');action('redo');finish()
   a.activate_game(Game(42,mode='sprint'));start('17-desktop-sprint');hold(1.5)
   for d in ['left','down','left','up','right']:move(d)
   action('undo');action('redo');finish()
  finally:
   a.flush_save();a.requests.put(None);a.process.join(timeout=2)
   if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
   pg.quit()
if __name__=='__main__':main()
