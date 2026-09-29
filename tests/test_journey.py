import os,argparse,unittest,itertools,time,json,tempfile
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame as pg
from engine import Game,Storage,DIRECTIONS
from puzzles import LEVELS,make_puzzle,solve
from modes import SessionBook
from game import Atelier

class PuzzleRulesTests(unittest.TestCase):
    def test_all_chapters_are_solvable_and_par_is_shortest(self):
        self.assertEqual(len(LEVELS),12)
        for index,level in enumerate(LEVELS):
            game=make_puzzle(index);result=solve(game.board,game.rng.getstate(),level['target'],level['limit'])
            self.assertEqual(len(result['solution']),level['par'])
            for direction in result['solution']:self.assertIsNotNone(game.move(direction))
            self.assertGreaterEqual(max(game.board),level['target'])
            self.assertIsNone(game.move('left'))
            # Independent exhaustive enumeration uses the real game rules, not
            # the solver's cached transitions or visited-state optimization.
            for path in itertools.product(DIRECTIONS,repeat=level['par']-1):
                trial=make_puzzle(index)
                for direction in path:
                    if trial.move(direction) is None:break
                    self.assertLess(max(trial.board),level['target'])

    def test_preview_is_the_actual_spawn_and_undo_restores_it(self):
        for index,level in enumerate(LEVELS):
            game=make_puzzle(index);before=game.serialize();result=solve(game.board,game.rng.getstate(),level['target'],level['limit'])
            for direction,preview in result['previews'].items():
                trial=Game.restore(before);trial.move(direction)
                self.assertEqual(trial.board,preview['board'])
                trial.undo();trial.move(direction);self.assertEqual(trial.board,preview['board'])

    def test_sprint_turn_limit_and_undo(self):
        game=Game(17,mode='sprint');game.moves=59;game.board=[2,2]+[0]*14
        self.assertIsNotNone(game.move('left'));self.assertEqual(game.moves,60)
        before=game.snapshot();self.assertIsNone(game.move('right'));self.assertEqual(before,game.snapshot())
        game.undo();self.assertEqual(game.moves,59);self.assertIsNotNone(game.move('right'))

    def test_four_modes_persist_independently(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Storage(Path(folder)/'save.json');book=SessionBook(store.data);game=Game(19)
            saved={}
            for mode in ('classic','daily','puzzle','sprint'):
                game=book.switch(game,mode);game.move('left');saved[mode]=game.snapshot()
            store.save(game,{})
            loaded=Storage(store.path);book=SessionBook(loaded.data);game=Game.restore(loaded.data['game'])
            for mode in saved:
                game=book.switch(game,mode);self.assertEqual(game.snapshot(),saved[mode])

    def test_new_modes_do_not_pollute_classic_records(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Storage(Path(folder)/'save.json')
            for game in (make_puzzle(),Game(1,mode='sprint')):
                game.move('left');game.score=20000;store.record(game);store.save(game,{})
                self.assertEqual(store.data['best'],0);self.assertFalse(store.data['records'])

class JourneyUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
    @classmethod
    def tearDownClass(cls):
        a=cls.app;a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()
    def setUp(self):
        a=self.app;a.motion=False;a.coach=False;a.modal=None;a.modal_progress=0;a.stop_auto();a.game=Game(3)
        a.sessions.sessions={};a.sessions.sync();a.progress={};a.store.data['puzzle_progress']={};a.episode_recorded=None

    def test_lobby_keeps_game_and_selects_each_mode(self):
        a=self.app;before=a.game.snapshot();a.act('lobby');a.act('tab_classic');a.draw()
        self.assertEqual(a.game.snapshot(),before)
        for key in ('mode_classic','mode_daily','puzzle_levels','mode_sprint'):
            self.assertTrue(any(k==key for k,_,_ in a.buttons))
        a.act('close');self.assertEqual(a.modal_progress,0)
        a.act('mode_sprint');self.assertEqual(a.game.mode,'sprint')
        a.act('puzzle_levels');a.draw();self.assertEqual(sum(k.startswith('level_') for k,_,_ in a.buttons),12)
        a.act('level_4');self.assertEqual(a.game.puzzle_id,4)
        a.act('mode_classic');self.assertEqual(a.game.snapshot(),before)

    def test_puzzle_completion_stars_retry_and_old_records(self):
        a=self.app;before_best=a.store.data['best'];a.act('level_0');initial=a.game.snapshot()
        for direction in LEVELS[0]['solution']:a.move(direction)
        a.update(.01);self.assertTrue(a.ended);self.assertEqual(a.progress['0']['stars'],3)
        self.assertEqual(a.store.data['best'],before_best)
        a.draw();self.assertTrue(any(k=='puzzle_next' for k,_,_ in a.buttons))
        a.act('puzzle_retry');self.assertEqual(a.game.snapshot(),initial);self.assertFalse(a.ended)
        a.act('level_1')
        for direction in LEVELS[1]['solution']:a.move(direction,True)
        a.update(.01);self.assertEqual(a.progress['1']['stars'],1)
        a.act('undo');self.assertFalse(a.ended)

    def test_sprint_stop_and_separate_best(self):
        a=self.app;a.store.data['sprint_best']={};a.act('mode_sprint');a.game.moves=59;a.game.board=[2,2]+[0]*14
        a.move('left');a.update(.01);self.assertTrue(a.ended);self.assertEqual(a.game.moves,60)
        self.assertEqual(a.store.data['sprint_best']['manual'],4)
        a.move('right');self.assertEqual(a.game.moves,60)
        a.act('undo');self.assertFalse(a.ended)

    def test_selecting_an_unfinished_chapter_resumes_it(self):
        a=self.app;a.act('level_6');a.move(LEVELS[6]['solution'][0]);before=a.game.snapshot()
        a.act('mode_classic');a.act('level_6')
        self.assertEqual(a.game.snapshot(),before)

    def test_lobby_cards_accept_clicks_in_their_whole_bounds(self):
        a=self.app;a.act('lobby');a.act('tab_classic');a.draw()
        a.pointer_down((700,310));a.pointer_up((700,310))
        self.assertEqual(a.modal,'levels')

    def test_worker_uses_exact_puzzle_solver(self):
        a=self.app;a.act('level_8');a.act('hint');before=a.game.snapshot()
        until=time.monotonic()+8
        while time.monotonic()<until:
            a.update(.01)
            if a.ai_result and a.ai_result.get('backend')=='exact':break
            time.sleep(.005)
        else:self.fail('Exact solver did not reply')
        self.assertTrue(a.ai_result['solvable']);self.assertEqual(a.game.snapshot(),before)
        a.act('intelligence');a.act('reveal_path');a.draw()
        self.assertTrue(a.path_revealed)

if __name__=='__main__':unittest.main()
