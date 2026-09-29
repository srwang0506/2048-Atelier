import unittest,json,tempfile,random
from queue import Queue
from unittest.mock import patch,Mock
from pathlib import Path
from engine import Game,Storage,slide,can_move,DIRECTIONS
from insight import immediate_loss,analyze_moves,enrich
from modes import daily_game,SessionBook,timeline
from search_native import NativeSearch

class ModeTests(unittest.TestCase):
    def test_daily_reproducibility(self):
        a=daily_game('2026-09-28');b=daily_game('2026-09-28')
        for direction in ['left','down','right','up']*12:
            self.assertEqual(a.board,b.board);self.assertEqual(a.score,b.score)
            a.move(direction);b.move(direction)
        self.assertNotEqual(a.rng.getstate(),daily_game('2026-09-29').rng.getstate())
        self.assertEqual(Game.restore(json.loads(json.dumps(a.serialize()))).challenge_date,'2026-09-28')

    def test_switch_preserves_both_sessions_across_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Storage(Path(folder)/'save.json');book=SessionBook(store.data)
            classic=Game(7);classic.move('left');before=classic.serialize()
            daily=book.switch(classic,'daily','2026-09-28');daily.move('right');daily_before=daily.serialize()
            classic=book.switch(daily,'classic');self.assertEqual(classic.serialize(),before)
            store.save(classic,{})
            restored=Storage(store.path);book=SessionBook(restored.data)
            daily=book.switch(Game.restore(restored.data['game']),'daily','2026-09-28')
            self.assertEqual(daily.serialize(),daily_before)
            self.assertTrue(daily.undo())

    def test_replay_snapshot_does_not_mutate_the_game(self):
        game=Game(12)
        for d in ['left','down','right']*8:game.move(d)
        before=game.serialize();frames=timeline(game)
        self.assertEqual(frames[-1]['board'],game.board)
        frames[-1]['board'][0]=2**20
        self.assertEqual(game.serialize(),before)
        self.assertTrue(all(a['moves']+1==b['moves'] for a,b in zip(frames,frames[1:])))

    def test_assistance_cannot_be_erased_by_undo(self):
        game=daily_game('2026-09-28');game.move('left',True);game.undo()
        self.assertTrue(game.assisted)
        self.assertTrue(Game.restore(game.serialize()).assisted)

    def test_bad_inactive_session_does_not_destroy_classic(self):
        data={'sessions':{'daily:bad':{'board':None},'classic':Game(1).serialize()}}
        book=SessionBook(data);self.assertEqual(list(book.sessions),['classic'])
        with self.assertRaises(ValueError):daily_game('2026-99-01')

class InsightTests(unittest.TestCase):
    def test_exact_spawn_risk(self):
        board=[0,2,8,16,2,8,16,32,8,16,32,64,16,32,64,128]
        self.assertAlmostEqual(immediate_loss(board),.1)
        board[1]=4;board[4]=4
        self.assertAlmostEqual(immediate_loss(board),.9)
        board=[0,8,16,32,8,16,32,64,16,32,64,128,32,64,128,256]
        self.assertEqual(immediate_loss(board),1.)
        board[15]=0;self.assertEqual(immediate_loss(board),0.)

    def test_direction_facts_match_reference_rules(self):
        rng=random.Random(3)
        for _ in range(100):
            board=[rng.choice([0,2,4,8,16]) for _ in range(16)]
            choices=analyze_moves(board)
            for d,item in choices.items():
                moved,gain,_,merges=slide(board,d)
                self.assertEqual(item['board'],moved);self.assertEqual(item['gain'],gain)
                self.assertEqual(item['merges'],len(merges));self.assertEqual(item['empty'],moved.count(0)-1)
                empty=[i for i,v in enumerate(moved) if not v];expected=0.
                for index in empty:
                    for value,weight in [(2,.9),(4,.1)]:
                        spawned=moved[:];spawned[index]=value
                        if not can_move(spawned):expected+=weight/len(empty)
                self.assertAlmostEqual(item['loss'],expected)
        self.assertFalse(can_move([0]*16))

    def test_safe_guard_ignores_certain_defeat(self):
        rng=random.Random(814)
        for _ in range(5000):
            board=[rng.choice([2,4,8,16,32,64]) for _ in range(16)];choices=analyze_moves(board)
            dead=[d for d,v in choices.items() if v['loss']==1];safe=[d for d,v in choices.items() if v['loss']<1]
            if dead and safe:break
        else:self.fail('No guard fixture found')
        result=enrich(board,{'direction':dead[0],'values':[(dead[0],10),(safe[0],-10)]})
        self.assertEqual(result['direction'],safe[0]);self.assertTrue(result['survival_guard'])

class AdaptiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ai=NativeSearch()

    def test_budget_adapts_and_returns_a_complete_root(self):
        open_board=[2,2]+[0]*14
        tight=[32768,16384,8192,4096,256,512,1024,2048,128,64,32,16,0,2,4,8]
        a=self.ai.choose(open_board,.012,adaptive=True);b=self.ai.choose(tight,.012,adaptive=True)
        self.assertLess(a['budget_ms'],b['budget_ms'])
        for board,result in [(open_board,a),(tight,b)]:
            legal={d for d in DIRECTIONS if slide(board,d)[0]!=board}
            self.assertEqual({d for d,_ in result['values']},legal)
            self.assertIn(result['direction'],legal);self.assertTrue(result['adaptive'])
            self.assertGreaterEqual(result['depth'],0)

    def test_worker_cache_respects_budget_and_explicit_refresh(self):
        from ai import worker
        requests=Queue();results=Queue();board=[2,2]+[0]*14
        for token,budget,options in [(0,.02,{}),(1,.02,{}),(2,.03,{}),(3,.02,{'refresh':True})]:
            requests.put((token,board,budget,options))
        requests.put(None)
        solver=Mock();solver.choose.side_effect=lambda *args,**kwargs:dict(direction='left',values=[('left',1)])
        with patch('ai.Expectimax',return_value=solver):worker(requests,results)
        self.assertEqual(results.get_nowait()[0],-1)
        received=[results.get_nowait()[1] for _ in range(4)]
        self.assertFalse(received[0].get('cached',False));self.assertTrue(received[1]['cached'])
        self.assertFalse(received[2].get('cached',False));self.assertFalse(received[3].get('cached',False))
        self.assertEqual(solver.choose.call_count,3)

if __name__=='__main__':unittest.main()
