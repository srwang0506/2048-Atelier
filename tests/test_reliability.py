import json,random,tempfile,unittest
from threading import Event
from pathlib import Path
from engine import Game,Storage,slide,DIRECTIONS
from persistence import SaveService

class ContinuationTests(unittest.TestCase):
    def test_restart_restores_undo_redo_and_randomness(self):
        game=Game(42);game.board=[2,2]+[0]*14
        game.move('left');first=game.board[:];game.move('down');second=game.board[:]
        restored=Game.restore(json.loads(json.dumps(game.serialize())))
        self.assertTrue(restored.undo());self.assertEqual(restored.board,first)
        restored=Game.restore(json.loads(json.dumps(restored.serialize())))
        self.assertTrue(restored.redo());self.assertEqual(restored.board,second)
        for direction in ('right','up','left','down'):
            game.move(direction);restored.move(direction)
            self.assertEqual(game.board,restored.board)
            self.assertEqual(game.score,restored.score)

    def test_branching_clears_redo_only_after_a_valid_move(self):
        game=Game(1);game.board=[2,2]+[0]*14;game.move('left');game.undo()
        self.assertIsNone(game.move('up'));self.assertTrue(game.future)
        game.move('right');self.assertFalse(game.future);self.assertFalse(game.redo())

    def test_history_cap_and_large_tile_save(self):
        game=Game(9)
        for _ in range(180):
            legal=[d for d in DIRECTIONS if slide(game.board,d)[0]!=game.board]
            if not legal:break
            game.move(random.Random(game.moves).choice(legal))
        self.assertLessEqual(len(game.history),100)
        restored=Game.restore(json.loads(json.dumps(game.serialize())))
        self.assertEqual(len(game.history),len(restored.history))
        game.board=[2**30,2**30]+[0]*14;game.move('left')
        self.assertEqual(max(Game.restore(game.serialize()).board),2**31)

    def test_bad_timeline_keeps_the_board(self):
        game=Game(5);data=game.serialize();data['continuation']='bad compressed data'
        restored=Game.restore(data)
        self.assertEqual(restored.board,game.board);self.assertTrue(restored.restore_warning)

    def test_corrupt_optional_rows_are_removed(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json';game=Game(1)
            p.write_text(json.dumps({'records':[{'score':'bad'},7],'achievements':[{},128,'bad'],'game':game.serialize()}))
            store=Storage(p)
            self.assertEqual(store.data['records'],[]);self.assertEqual(store.data['achievements'],[128])
            self.assertEqual(store.data['game']['board'],game.board);self.assertTrue(store.notice)
            game.move('left');store.record(game)

    def test_last_readable_save_survives_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json';store=Storage(p);game=Game(7)
            self.assertTrue(store.save(game,{}));saved=game.board[:]
            game.move('left');self.assertTrue(store.save(game,{}))
            p.write_text('{broken')
            recovered=Storage(p);self.assertFalse(recovered.error);self.assertTrue(recovered.notice)
            self.assertEqual(recovered.data['game']['board'],saved)
            self.assertTrue(recovered.save(Game.restore(recovered.data['game']),{}))
            self.assertEqual(Storage(p.with_suffix('.bak')).data['game']['board'],saved)
            corrupted=json.loads(p.read_text());corrupted['best']='bad';p.write_text(json.dumps(corrupted))
            recovered=Storage(p);self.assertTrue(recovered.notice)
            self.assertTrue(recovered.save(Game.restore(recovered.data['game']),{}))
            self.assertIsNone(Storage(p.with_suffix('.bak')).error)

    def test_background_save_freezes_and_coalesces_checkpoints(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json';store=Storage(p);game=Game(7)
            service=SaveService(p);entered=Event();release=Event();writes=[];real=service._write
            def blocked_write(frozen,settings,data):
                entered.set();release.wait(3);writes.append(frozen.board[:]);return real(frozen,settings,data)
            service._write=blocked_write
            first=game.board[:];service.submit(game,{},store.data);self.assertTrue(entered.wait(2))
            for direction in ['left','down','right']:
                game.move(direction);service.submit(game,{},store.data)
            expected=game.serialize();game.move('up')
            release.set();self.assertEqual(service.close(),[None,None])
            self.assertEqual(writes[0],first);self.assertEqual(len(writes),2)
            self.assertEqual(Storage(p).data['game'],expected)

if __name__=='__main__':unittest.main()
