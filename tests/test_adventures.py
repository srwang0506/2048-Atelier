"""New-mode rules, witness verification, persistence and actual UI events."""
import os,argparse,itertools,random,tempfile,time,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame as pg
from engine import Game,Storage,DIRECTIONS,can_move,slide
from expedition import make_expedition,choose,remaining,powers,search
from rescue import extract,solve,make_rescue,practice_challenges,spawn,valid_challenge
from modes import SessionBook,timeline
from persistence import SaveService
from game import Atelier

def failed_game(seed=0):
    g=Game(seed);r=random.Random(seed+2000)
    while can_move(g.board):
        ds=list(DIRECTIONS);r.shuffle(ds)
        for d in ds:
            if g.move(d):break
    return g

def expedition(perk='battery'):
    g=make_expedition(17);choose(g,perk);return g

class ExpeditionTests(unittest.TestCase):
    def test_draft_saved_checkpoint_and_undo_boundary(self):
        g=make_expedition(8);offers=g.extra['offers'][:]
        self.assertIsNone(g.move('left'));self.assertEqual(Game.restore(g.serialize()).extra['offers'],offers)
        self.assertTrue(choose(g,'combo'));self.assertFalse(choose(g,'battery'))
        g.board=[64,64]+[0]*14;g.move('left');self.assertEqual(g.extra['phase'],'clear')
        self.assertEqual(Game.restore(g.serialize()).extra['offers'],g.extra['offers'])
        self.assertTrue(choose(g,g.extra['offers'][0]));self.assertFalse(g.history);self.assertEqual(g.extra['stage'],1)
        self.assertEqual(g.extra['stage_score'],g.score);self.assertEqual(g.extra['stage_start'],g.moves)
        self.assertEqual(g.board.count(0),15)
    def test_checkpoint_keeps_the_last_tile(self):
        g=expedition();g.board=[64,64]+[0]*14;g.extra['freeze']=1
        g.move('left');self.assertEqual(g.board.count(0),15)
        choose(g,g.extra['offers'][0]);self.assertTrue(any(g.board));self.assertEqual(g.extra['phase'],'play')
    def test_ai_prioritizes_a_clear_on_the_last_turn(self):
        g=expedition('combo');g.board=[64,64]+[0]*14
        e=g.extra.copy();e['_needed']=100;e['_remaining']=1
        r=search(g.board,e,.025);self.assertGreaterEqual(r['choices'][r['direction']]['gain'],100)
    def test_scoring_combinations(self):
        g=expedition();g.extra['perks']={'combo':2,'echo':1,'corner':1,'gambit':2};g.extra['streak']=3
        g.board=[2,2,4,4]+[0]*12;data=g.move('left')
        # Base 12 + two-merge bonus 6 + corner bonus 2, then x2.2 and x2.5.
        self.assertEqual(data['gain'],110);self.assertEqual(g.score,110);self.assertEqual(g.extra['energy'],2)
    def test_flow_and_energy_cap(self):
        g=expedition();g.extra['perks']={'flow':2,'battery':2};g.extra['energy']=11
        g.board=[2,2,4,4]+[0]*12;state=g.rng.getstate();g.move('left')
        self.assertEqual(g.board[:4],[4,8,0,0]);self.assertEqual(g.rng.getstate(),state);self.assertEqual(g.extra['energy'],12)
    def test_risky_spawn(self):
        class Fixed:
            def choice(self,values):return values[0]
            def random(self):return .75
        g=expedition('gambit');g.rng=Fixed();g.board=[0]*16;g.spawn();self.assertEqual(g.board[0],4)
        g.extra['perks']={};g.board=[0]*16;g.spawn();self.assertEqual(g.board[0],2)
    def test_freeze_cooldown_invalid_moves_and_undo(self):
        g=expedition();g.board=[2,2]+[0]*14;g.extra['energy']=12;before=g.snapshot()
        self.assertIsNotNone(g.move('freeze'));self.assertEqual(g.moves,0);self.assertEqual(g.extra['energy'],7)
        self.assertIsNone(g.move('freeze'));g.move('left');self.assertEqual(g.board.count(0),15)
        cooldown=g.extra['cooldown'];self.assertIsNone(g.move('left'));self.assertEqual(g.extra['cooldown'],cooldown)
        g.move('right');self.assertEqual(g.board.count(0),15);self.assertEqual(g.extra['freeze'],0)
        g.undo();g.undo();g.undo();self.assertEqual(g.snapshot(),before)
    def test_swaps_preserve_values_and_history(self):
        g=expedition();g.board=[2,4,2]+[0]*13;g.extra['energy']=12;before=g.snapshot()
        for invalid in ('swap:0:2','swap:0:3','swap:9:1'):self.assertIsNone(g.move(invalid))
        self.assertEqual(g.snapshot(),before)
        result=g.move('swap:0:1');self.assertEqual(g.board[:3],[4,2,2]);self.assertEqual(g.moves,0)
        self.assertEqual(len(result['tracks']),3);self.assertEqual(g.extra['energy'],6)
        after=g.snapshot();g.undo();self.assertEqual(g.snapshot(),before);g.redo();self.assertEqual(g.snapshot(),after)
    def test_final_turn_win_and_loss_undo(self):
        g=expedition();g.moves=remaining(g)-1;g.board=[64,64]+[0]*14
        g.move('left');self.assertEqual(g.extra['phase'],'clear');g.undo();self.assertEqual(g.extra['phase'],'play')
        g.board=[2]+[0]*15;g.move('right');self.assertEqual(g.extra['phase'],'lost');g.undo();self.assertEqual(g.extra['phase'],'play')
    def test_corrupt_variant_rejected(self):
        raw=expedition().serialize();raw['extra']['energy']=-1
        with self.assertRaises(ValueError):Game.restore(raw)
        raw=expedition().serialize();raw['extra']['perks']['unknown']=1
        with self.assertRaises(ValueError):Game.restore(raw)
    def test_save_undo_redo_and_frozen_background_write(self):
        g=expedition();g.board=[2,2,4]+[0]*13;g.move('left');after=g.snapshot();g.undo()
        restored=Game.restore(g.serialize());self.assertFalse(restored.restore_warning);restored.redo()
        self.assertEqual(restored.snapshot(),after);self.assertEqual(len(timeline(restored)),2)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'save.json';service=SaveService(path);metadata=Storage(path).data
            service.submit(restored,{},metadata);restored.extra['energy']=0;restored.extra['perks']['gambit']=2
            self.assertEqual(service.close(),[None]);self.assertEqual(Game.restore(Storage(path).data['game']).snapshot(),after)
    def test_variant_sessions_and_classic_best(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Storage(Path(folder)/'save.json');book=SessionBook(store.data);classic=Game(3);before=classic.snapshot()
            g=book.switch(classic,'expedition');choose(g,'gambit');g.move('left');g.score=10000
            store.record(g);store.save(g,{});self.assertEqual(store.data['best'],0);self.assertFalse(store.data['records'])
            self.assertEqual(book.switch(g,'classic').snapshot(),before)
    def test_ai_uses_energy_when_blocked(self):
        g=expedition();g.board=[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2];g.extra['energy']=12
        r=search(g.board,g.extra,.015);self.assertEqual(r['backend'],'expedition')
        self.assertIn(r['direction'],powers(g));self.assertIsNotNone(g.move(r['direction'],True));self.assertTrue(g.assisted)

class RescueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.practice=practice_challenges()
    def test_spawn_matches_real_engine(self):
        for seed in range(20):
            g=Game(seed)
            for _ in range(8):g.move(DIRECTIONS[seed%4]);seed+=1
            for d in DIRECTIONS:
                b,_,_,_=slide(g.board,d)
                if b==g.board:continue
                expected,rng=spawn(b,g.rng.getstate());actual=Game.restore(g.serialize());actual.move(d)
                self.assertEqual(list(expected),actual.board);self.assertEqual(rng,actual.rng.getstate())
    def test_witnesses_and_shortest_paths_independent_enumeration(self):
        self.assertEqual(len(self.practice),3)
        for c in self.practice:
            self.assertTrue(valid_challenge(c));g=make_rescue(c);initial=g.serialize()
            for path in itertools.product(DIRECTIONS,repeat=c['par']-1):
                trial=Game.restore(initial)
                for d in path:
                    if trial.move(d) is None:break
                    self.assertLess(trial.board.count(0),c['goal'])
            for d in c['solution']:self.assertIsNotNone(g.move(d))
            self.assertGreaterEqual(g.board.count(0),3);self.assertIsNone(g.move('left'))
    def test_extract_replays_both_original_failure_and_rescue(self):
        failed=failed_game();before=failed.serialize();r=extract(before)
        self.assertEqual(r['status'],'found');self.assertEqual(failed.serialize(),before)
        c=r['challenge'];original=Game.restore(c['origin'])
        for frame in c['original']:
            self.assertIsNotNone(original.move(frame['direction']));self.assertEqual(original.board,frame['board'])
        self.assertFalse(can_move(original.board));self.assertEqual(original.board,failed.board)
        g=make_rescue(c)
        for d in c['solution']:g.move(d)
        self.assertGreaterEqual(g.board.count(0),3)
    def test_live_games_and_no_history(self):
        self.assertEqual(extract(Game(3).serialize())['status'],'ineligible')
        g=Game(0);g.board=[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2];g.history=[]
        self.assertEqual(extract(g.serialize())['status'],'not_found')
    def test_timeout_is_not_proof_of_impossibility(self):
        g=make_rescue(self.practice[1]);r=solve(g.board,g.rng.getstate(),5,7,-1.)
        if not r['solvable']:self.assertFalse(r['complete'])
    def test_save_and_undo_keep_exact_future(self):
        c=self.practice[1];g=make_rescue(c);g.move(c['solution'][0]);before=g.snapshot();g.undo()
        restored=Game.restore(g.serialize());self.assertFalse(restored.restore_warning);restored.redo();self.assertEqual(restored.snapshot(),before)
        for d in c['solution'][1:]:restored.move(d)
        self.assertGreaterEqual(restored.board.count(0),3)

class AdventureUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
    @classmethod
    def tearDownClass(cls):
        a=cls.app;a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()
    def setUp(self):
        a=self.app;a.motion=False;a.coach=False;a.game=Game(3);a.modal=None;a.modal_progress=0;a.animation=None
        a.ended=False;a.stop_auto();a.sessions.sessions={};a.sessions.sync();a.rescue_archive=[];a.rescue_checked=[];a.rescue_job=None;a.adventure_stamp=None
        a.lobby_tab='featured';a.rescue_results={};a.expedition_records=[]
    def click(self,key):
        a=self.app;a.modal_progress=float(bool(a.modal));a.draw()
        rect=next(r for k,r,e in a.buttons if k==key and e);a.pointer_down(rect.center);a.pointer_up(rect.center)
    def wait(self,predicate):
        until=time.monotonic()+10
        while time.monotonic()<until:
            self.app.update(.01)
            if predicate():return
            time.sleep(.005)
        self.fail('Worker did not return')
    def test_pointer_entry_draft_swap_and_resume(self):
        a=self.app;original=a.game.snapshot();a.act('lobby');self.click('expedition_intro');self.click('expedition_new')
        offers=a.game.extra['offers'][:];self.click('close');self.assertEqual(a.modal,'lobby')
        self.click('expedition_intro');self.click('mode_expedition');self.assertEqual(a.game.extra['offers'],offers)
        self.click('perk_battery');self.assertFalse(a.ended);self.assertIsNone(a.modal)
        a.game.board=[2,4,2]+[0]*13;a.game.extra['energy']=12
        self.click('swap');self.click('swapcell_0');self.click('swapcell_1');self.click('swap_confirm')
        self.assertEqual(a.game.board[:3],[4,2,2]);a.act('undo');self.assertEqual(a.game.board[:3],[2,4,2])
        a.act('mode_classic');self.assertEqual(a.game.snapshot(),original)
    def test_new_run_requires_confirmation_if_one_is_active(self):
        a=self.app;a.activate_game(expedition());a.game.move('left');before=a.game.snapshot()
        a.act('expedition_intro');a.act('expedition_new');self.assertEqual(a.modal,'expedition_reset')
        self.assertEqual(a.game.snapshot(),before);self.click('expedition_intro');self.assertEqual(a.game.snapshot(),before)
    def test_auto_can_use_energy_after_board_is_blocked(self):
        a=self.app;c=a.practice[0];g=expedition();g.board=c['origin']['board'][:]
        origin=Game.restore(c['origin']);g.rng.setstate(origin.rng.getstate());g.extra['energy']=12
        a.activate_game(g);a.auto=True;a.move(c['original'][0]['direction'],True)
        self.assertFalse(can_move(a.game.board));self.assertFalse(a.ended);self.assertTrue(a.auto)
    def test_worker_both_modes(self):
        a=self.app;a.activate_game(expedition());a.act('hint');self.wait(lambda:a.ai_result and a.ai_result.get('backend')=='expedition')
        a.act('rescue_play_'+a.practice[1]['id']);a.act('auto');self.wait(lambda:a.ended)
        self.assertGreaterEqual(a.game.board.count(0),3);self.assertFalse(a.auto)
        self.assertIn('assisted',a.rescue_results[a.game.extra['challenge']])
        a.act('rescue_review');a.draw();a.act('review_next');a.draw()
    def test_background_extraction_survives_mode_switch(self):
        a=self.app;a.activate_game(failed_game());a.update(.01);self.assertIsNotNone(a.rescue_job)
        a.act('mode_daily');before=a.game.snapshot();self.wait(lambda:bool(a.rescue_archive))
        self.assertEqual(a.game.snapshot(),before);self.assertEqual(a.game.mode,'daily')
        a.act('rescue_play_'+a.rescue_archive[0]['id']);self.assertEqual(a.game.mode,'rescue')
    def test_stage_waits_for_player_choice(self):
        a=self.app;a.activate_game(expedition());a.game.board=[64,64]+[0]*14;a.auto=True
        a.move('left',True);a.update(.01);self.assertEqual(a.modal,'draft');self.assertFalse(a.auto);self.assertTrue(a.ended)
        self.click('perk_'+a.game.extra['offers'][0]);self.assertEqual(a.game.extra['stage'],1)
        self.assertFalse(a.ended);self.assertFalse(a.game.history)
    def test_reveal_assistance_and_retry_records(self):
        a=self.app;a.act('rescue_play_'+a.practice[0]['id']);a.act('rescue_review');self.assertTrue(a.game.assisted)
        a.act('close');a.act('rescue_retry');self.assertFalse(a.game.assisted)
        for d in a.practice[0]['solution']:a.move(d)
        a.update(.01);self.assertIn('manual',a.rescue_results[a.game.extra['challenge']])
        best=a.store.data['best'];a.act('rescue_retry');self.assertEqual(a.store.data['best'],best)

if __name__=='__main__':unittest.main()
