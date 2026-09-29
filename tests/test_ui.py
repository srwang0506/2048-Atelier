"""Integration smoke test: real rendering + worker + pygame input events."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import argparse
import json
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame as pg
from game import Atelier

class UITest(unittest.TestCase):
    def test_interaction_and_rendering(self):
        app=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
        def frame(seconds=.02):
            app.clock.tick(60);app.update(seconds);app.draw()
        def wait_for(predicate,timeout=8):
            until=time.monotonic()+timeout
            while time.monotonic()<until:
                frame()
                if predicate():return
            self.fail('UI condition timed out')
        try:
            app.new_game();app.game.board=[2,2,0,0]+[0]*12
            app.move('left');self.assertEqual(app.game.score,4)
            self.assertIsNotNone(app.animation)
            app.act('step') # A single-step request during animation must not disappear.
            wait_for(lambda:app.game.moves>=2 and not app.animation)
            self.assertEqual(app.game.ai_moves,1)
            app.act('undo');self.assertEqual(app.game.moves,1);self.assertEqual(app.game.ai_moves,0)
            app.act('hint');before=app.game.board[:]
            wait_for(lambda:app.ai_result is not None and app.pending is None)
            self.assertEqual(app.game.board,before)
            self.assertIn(app.ai_result['direction'],('left','right','up','down'))
            app.act('intelligence');frame()
            self.assertEqual(app.modal,'intelligence')
            app.act('close')
            app.act('auto');wait_for(lambda:app.game.moves>=4)
            app.act('auto');self.assertFalse(app.auto)
            paused=app.game.moves
            wait_for(lambda:app.pending is None and app.animation is None)
            for _ in range(4):frame()
            self.assertEqual(app.game.moves,paused)
            initial_theme=app.theme
            app.act('settings');frame();self.assertEqual(app.modal,'settings')
            app.act('theme');self.assertNotEqual(app.theme,initial_theme);frame()
            app.act('close')
            out=Path(__file__).resolve().parents[1]/'test-artifacts';out.mkdir(exist_ok=True)
            pg.image.save(app.capture_surface(),str(out/'light.png'))
            app.act('help');frame();pg.image.save(app.capture_surface(),str(out/'help.png'))
            app.act('motion');self.assertFalse(app.motion)
            app.act('close');app.act('records');frame();pg.image.save(app.capture_surface(),str(out/'records.png'))
            app.act('close');app.act('new');self.assertEqual(app.modal,'new');frame()
            app.act('cancel');self.assertEqual(app.game.moves,paused)
            app.act('new');app.act('confirm_new');self.assertEqual(app.game.moves,0)
            app.game.board=[2,2,0,0]+[0]*12
            pg.event.post(pg.event.Event(pg.KEYDOWN,key=pg.K_LEFT))
            app.events();self.assertEqual(app.game.score,4)
            frame()
            # Responsive letterboxing: 940×690 and wide/short windows.
            for dims in [(940,690),(1280,720)]:
                app.screen=pg.display.set_mode(dims,pg.RESIZABLE);frame()
                pos=app.screen_point((app.offset[0]+700*app.factor,app.offset[1]+570*app.factor))
                self.assertAlmostEqual(pos[0],700,delta=1);self.assertAlmostEqual(pos[1],570,delta=1)
            app.game.board=[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2];app.ended=True;app.animation=None
            frame();self.assertTrue(any(k=='new' for k,r,e in app.buttons))
            app.act('auto');self.assertFalse(app.auto)
            app.new_game();app.motion=True;app.game.board=[0]*12+[2,2,0,0]
            app.move('left');app.move('up')
            self.assertEqual(app.buffered_direction,'up')
            wait_for(lambda:app.game.moves==2 and app.animation is None)
            app.new_game();app.game.board=[2,2]+[0]*14;app.speed=3;app.auto=True
            app.move('left',by_ai=True)
            self.assertIsNone(app.animation);self.assertEqual(app.game.ai_moves,1)
            app.stop_auto()
            # Board dragging and toolbar clicks use the redesigned board bounds,
            # including letterboxed window coordinates.
            app.new_game();app.motion=False;app.game.board=[2,2]+[0]*14;frame()
            def screen_pos(x,y):
                return (round(app.offset[0]+x*app.factor),round(app.offset[1]+y*app.factor))
            pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN,button=1,pos=screen_pos(640,450)))
            pg.event.post(pg.event.Event(pg.MOUSEBUTTONUP,button=1,pos=screen_pos(500,450)))
            app.events();self.assertEqual(app.game.score,4);frame()
            setting=next(r for k,r,e in app.buttons if k=='settings')
            pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN,button=1,pos=screen_pos(*setting.center)))
            pg.event.post(pg.event.Event(pg.MOUSEBUTTONUP,button=1,pos=screen_pos(*setting.center)))
            app.events();self.assertEqual(app.modal,'settings');frame()
            pg.event.post(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE))
            app.events();self.assertIsNone(app.modal)
            # Settling is visual: the next turn is accepted at tile arrival.
            app.new_game();app.motion=True;app.game.board=[2,2]+[0]*14
            app.move('left');app.animation['start']-=app.animation['duration']+.005
            app.update(.01)
            self.assertIsNone(app.animation);self.assertTrue(app.effects)
            app.move('down');self.assertEqual(app.game.moves,2)
            # Preserve a short sequence of fast key presses, with no texture
            # construction inside the animated frames.
            app.new_game();app.game.board=[0]*12+[2,2,0,0]
            builds=app.tile_builds
            for direction in ['left','up','right','down']:app.move(direction)
            self.assertEqual(list(app.input_queue),['up','right','down'])
            for _ in range(4):
                app.animation['start']-=app.animation['duration']+.005
                app.update(.01);app.draw()
            self.assertEqual(app.game.moves,4);self.assertFalse(app.input_queue)
            self.assertEqual(app.tile_builds,builds)
            # AI can think while tiles move; pausing discards that prefetched move.
            wait_for(lambda:app.pending is None)
            app.new_game();app.game.board=[2,2]+[0]*14;app.auto=True;app.speed=1
            app.move('left',by_ai=True);app.animation['duration']=2
            app.update(.01);self.assertIsNotNone(app.pending)
            wait_for(lambda:app.queued_ai is not None)
            before=app.game.board[:];self.assertEqual(app.game.moves,1)
            app.stop_auto();self.assertIsNone(app.queued_ai)
            app.animation['start']-=3;app.update(.01);app.draw()
            self.assertEqual(app.game.board,before);self.assertEqual(app.game.moves,1)
        finally:
            app.requests.put(None);app.process.join(timeout=2)
            if app.process.is_alive():app.process.terminate();app.process.join(timeout=1)
            pg.quit()

if __name__=='__main__':unittest.main(verbosity=2)
