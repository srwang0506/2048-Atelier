import os,sys,json,statistics,time,argparse,tempfile
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier
from motion import FramePacer
from engine import Storage,Game
from modes import SessionBook,session_key

def stats(samples):
    values=sorted(samples)
    return dict(frames=len(values),mean_ms=round(statistics.mean(values),2),p95_ms=round(values[min(len(values)-1,int(len(values)*.95))],2),max_ms=round(max(values),2))

def main():
    a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
    a.new_game();a.sound=False;a.motion=True;a.auto=True;a.quality=3;a.speed=1;a.coach=False
    refresh=pg.display.get_current_refresh_rate() or 60;pacer=FramePacer(refresh)
    groups={};compute={};last=None;stages=set();checks={};snapshots={}
    flip=[0.];real_flip=pg.display.flip
    def measured_flip():
        t=time.perf_counter();real_flip();flip[0]=(time.perf_counter()-t)*1000
    pg.display.flip=measured_flip
    with tempfile.TemporaryDirectory(prefix='.2048-verify-',dir=root) as folder:
        a.store=Storage(Path(folder)/'save.json');a.sessions=SessionBook(a.store.data)
        a.args.demo=False;a.save();a.draw();start=time.monotonic()
        try:
            while time.monotonic()-start<20:
                dt=pacer.tick(wait=not pg.display.is_vsync() or pacer.fallback);now=time.monotonic();age=now-start
                a.events();a.focused=True;action=None;t=time.perf_counter()
                for stamp,key in [(4,'coach'),(6,'intelligence'),(7,'preview'),(8,'replay'),(9,'replay_play'),(10,'replay_check'),(11,'modes'),(12,'daily'),(15,'classic'),(16,'settings'),(17,'resume')]:
                    if age<stamp or stamp in stages:continue
                    stages.add(stamp);action=key
                    if key=='coach':
                        a.stop_auto();snapshots['coach_moves']=a.game.moves;a.act('coach')
                    elif key=='intelligence':
                        assert a.ai_result and a.ai_result['source']=='coach',a.ai_error
                        assert a.game.moves==snapshots['coach_moves'];checks['coach_readonly']=True
                        a.act(key)
                    elif key=='preview':
                        before=a.game.snapshot()
                        for direction in a.ai_result['choices']:a.act('preview_'+direction)
                        assert before==a.game.snapshot();checks['preview_readonly']=True
                    elif key=='replay':
                        a.act('close');snapshots['replay']=a.game.snapshot();a.act(key);a.act('replay_first')
                    elif key=='replay_check':
                        assert a.game.snapshot()==snapshots['replay'];checks['replay_readonly']=True
                    elif key=='modes':a.act('close');a.act(key)
                    elif key=='daily':
                        snapshots['classic']=a.game.snapshot();a.act('mode_daily');a.act('auto')
                    elif key=='classic':
                        a.stop_auto();snapshots['daily']=a.game.snapshot();snapshots['daily_key']=session_key(a.game)
                        assert a.game.moves>0;a.act('mode_classic')
                        assert a.game.snapshot()==snapshots['classic'];checks['mode_roundtrip']=True
                    elif key=='resume':a.act('close');a.act('auto')
                    else:a.act(key)
                    break
                a.update(dt);a.draw();end=time.perf_counter();pacer.observe(end-t,a.present_wait)
                group='panel_open' if action in ('intelligence','replay','modes','settings') else 'panel_motion' if 0<a.modal_progress<1 else 'panel_idle' if a.modal else 'play'
                if age>1:
                    if last is not None:groups.setdefault(group,[]).append((end-last)*1000)
                    compute.setdefault(group,[]).append((end-t)*1000-flip[0])
                last=end
            a.stop_auto();a.save();a.flush_save();saved=Storage(a.store.path)
            restored=Game.restore(saved.data['game'])
            assert restored.snapshot()==a.game.snapshot()
            daily=Game.restore(saved.data['sessions'][snapshots['daily_key']])
            assert daily.snapshot()==snapshots['daily'];checks['both_sessions_persisted']=True
            report=dict(driver=pg.display.get_driver(),refresh=refresh,vsync=pg.display.is_vsync(),pacing_fallback=pacer.fallback,
                present={k:stats(v) for k,v in groups.items()},compute={k:stats(v) for k,v in compute.items()},
                saved_steps=restored.moves,restored_history=len(restored.history),daily_steps=daily.moves,checks=checks)
            (root/'validation/v8/native.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
        finally:
            a.flush_save();a.requests.put(None);a.process.join(timeout=1)
            if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
            pg.quit()
if __name__=='__main__':main()
