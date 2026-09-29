import os,sys,argparse,time,tempfile,json,random,statistics
from pathlib import Path
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy';os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from game import Atelier
from engine import Game,Storage,DIRECTIONS,can_move
from modes import SessionBook
from expedition import make_expedition

def main():
    a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.sound=False;a.coach=False;a.quality=0;a.speed=3;a.motion=True
    frames=[];events=[];start=time.monotonic();lastdraw=0.
    def tick():
        nonlocal lastdraw
        a.update(.008)
        if time.monotonic()-lastdraw>.025:
            t=time.perf_counter();a.draw();frames.append((time.perf_counter()-t)*1000);lastdraw=time.monotonic()
        time.sleep(.002)
    try:
        with tempfile.TemporaryDirectory() as folder:
            a.store=Storage(Path(folder)/'save.json');a.store.data.update(sprint_best={},puzzle_progress={})
            a.sessions=SessionBook(a.store.data);a.args.demo=False;a.game=Game(19);a.sessions.stash(a.game)
            a.activate_game(make_expedition(13));until=time.monotonic()+90;priority=['combo','flow','echo','gambit','reserve','battery','corner','warp','ice']
            while time.monotonic()<until:
                if a.modal=='draft':
                    e=a.game.extra;key=min(e['offers'],key=priority.index);events.append(dict(stage=e['stage'],score=a.game.score,pick=key,moves=a.game.moves))
                    a.act('perk_'+key);a.act('auto')
                tick()
                if a.game.extra['phase'] in ('won','lost'):break
            else:raise AssertionError('Expedition did not finish')
            a.flush_save();saved=Game.restore(Storage(a.store.path).data['game']);assert saved.snapshot()==a.game.snapshot()
            expedition=dict(phase=a.game.extra['phase'],score=a.game.score,cleared=a.game.extra['cleared'],moves=a.game.moves,perks=a.game.extra['perks'],choices=events,save_restored=True)
            print('Expedition:',expedition,flush=True)
            a.sessions.stash(a.game)
            failed=Game(0);r=random.Random(2000)
            while can_move(failed.board):
                ds=list(DIRECTIONS);r.shuffle(ds)
                for d in ds:
                    if failed.move(d):break
            original=failed.snapshot();a.activate_game(failed);until=time.monotonic()+10
            while not a.rescue_archive and time.monotonic()<until:tick()
            assert a.rescue_archive,'Missing generated challenge';challenge=a.rescue_archive[0]
            a.act('rescue_play_'+challenge['id']);a.act('auto');until=time.monotonic()+10
            while not a.ended and time.monotonic()<until:tick()
            assert a.game.board.count(0)>=3;a.update(.01);a.act('rescue_review')
            for _ in range(6):a.act('review_next');tick()
            a.act('review_original');tick();a.act('close');a.act('mode_classic');assert a.game.snapshot()==original
            a.save();a.flush_save();loaded=Storage(a.store.path);sessions=SessionBook(loaded.data)
            assert 'expedition' in sessions.sessions and 'rescue' in sessions.sessions
            assert loaded.data['rescue_archive'][0]['id']==challenge['id']
            restored=Game.restore(sessions.sessions['rescue']);assert restored.board.count(0)>=3
            report=dict(expedition=expedition,rescue=dict(par=challenge['par'],generated_from_real_failure=True,original_preserved=True,archive_persisted=True,assisted_completion_persisted=True),
                seconds=round(time.monotonic()-start,2),draw_ms=dict(median=round(statistics.median(frames),2),p95=round(sorted(frames)[int(len(frames)*.95)],2),maximum=round(max(frames),2)),driver=pg.display.get_driver())
            (root/'validation/v12/full-flow.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    finally:
        a.flush_save();a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()
if __name__=='__main__':main()
