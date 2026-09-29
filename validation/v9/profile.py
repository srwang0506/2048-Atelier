import os,sys,json,statistics,time,argparse,tempfile
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier
from motion import FramePacer
from engine import Game,Storage
from modes import SessionBook

def stats(v):return dict(frames=len(v),mean_ms=round(statistics.mean(v),2),p95_ms=round(sorted(v)[int(len(v)*.95)],2),max_ms=round(max(v),2))
def main():
    a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.new_game();a.sound=False;a.coach=False
    a.motion=True;a.quality=0;a.speed=1;groups={};compute={};stages=set();checks={}
    refresh=pg.display.get_current_refresh_rate() or 60;pacer=FramePacer(refresh)
    with tempfile.TemporaryDirectory(prefix='.verify-v9-',dir=root) as folder:
        a.store=Storage(Path(folder)/'save.json');a.sessions=SessionBook(a.store.data)
        a.progress={};a.store.data.update(puzzle_progress={},sprint_best={});a.args.demo=False
        classic=a.game.snapshot();a.act('lobby');a.draw();start=time.monotonic();last=None
        try:
            while time.monotonic()-start<17:
                dt=pacer.tick(wait=not pg.display.is_vsync() or pacer.fallback);t=time.perf_counter();age=time.monotonic()-start
                a.events();a.focused=True;action=None
                for stamp,key in [(2,'chapters'),(3,'puzzle'),(6,'puzzle_check'),(7,'lobby'),(8,'sprint'),(14,'sprint_check'),(15,'settings'),(16,'close')]:
                    if age<stamp or stamp in stages:continue
                    stages.add(stamp);action=key
                    if key=='chapters':a.act('puzzle_levels')
                    elif key=='puzzle':a.act('level_11');a.act('auto')
                    elif key=='puzzle_check':
                        assert a.ended and a.game.moves==5 and max(a.game.board)>=2048
                        assert a.progress['11']['stars']==1;checks['exact_solver_autoplay']=True
                    elif key=='sprint':a.act('mode_sprint');a.speed=3;a.act('auto')
                    elif key=='sprint_check':
                        assert a.ended and a.game.moves==60,(a.game.moves,a.ai_error)
                        assert a.store.data['sprint_best']['assisted']==a.game.score;checks['sprint_60_moves']=True
                        a.act('mode_classic');assert a.game.snapshot()==classic;checks['classic_unchanged']=True
                    else:a.act(key)
                    break
                a.update(dt);a.draw();end=time.perf_counter();pacer.observe(end-t,a.present_wait)
                group='transition' if action else 'lobby' if a.modal=='lobby' else 'panel' if a.modal else a.game.mode
                if age>1:
                    if last is not None:groups.setdefault(group,[]).append((end-last)*1000)
                    compute.setdefault(group,[]).append((end-t-a.present_wait)*1000)
                last=end
            a.save();a.flush_save();saved=Storage(a.store.path)
            assert Game.restore(saved.data['game']).snapshot()==classic
            assert saved.data['puzzle_progress']['11']['stars']==1
            assert Game.restore(saved.data['sessions']['sprint']).moves==60
            checks['progress_restored']=True
            report=dict(driver=pg.display.get_driver(),refresh=refresh,vsync_reported=pg.display.is_vsync(),fallback=pacer.fallback,
                present={k:stats(v) for k,v in groups.items()},compute={k:stats(v) for k,v in compute.items()},checks=checks)
            name='headless.json' if pg.display.get_driver()=='dummy' else 'native.json'
            (root/'validation/v9'/name).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
        finally:
            a.flush_save();a.requests.put(None);a.process.join(timeout=2)
            if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
            pg.quit()
if __name__=='__main__':main()
