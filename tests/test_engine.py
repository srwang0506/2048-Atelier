import random
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import Game, Storage, slide, can_move, DIRECTIONS
from ai import Expectimax, init_tables, pack, successors, transpose

class RulesTest(unittest.TestCase):
    def test_single_merge_per_move(self):
        cases=[([2,2,2,2],[4,4,0,0],8),([4,4,8,0],[8,8,0,0],8),([2,0,2,4],[4,4,0,0],4),([4,4,4,0],[8,4,0,0],8)]
        for line,expected,points in cases:
            board,gain,tracks,merges=slide(line+[0]*12,'left')
            self.assertEqual(board[:4],expected);self.assertEqual(gain,points)
            self.assertEqual(sum(t.value for t in tracks),sum(line))

    def test_large_tiles_do_not_saturate(self):
        b,g,_,_=slide([32768,32768]+[0]*14,'left')
        self.assertEqual(b[0],65536);self.assertEqual(g,65536)

    def test_invalid_move_never_spawns(self):
        g=Game(1);g.board=[2,0,0,0]+[0]*12
        before=g.rng.getstate()
        self.assertIsNone(g.move('left'));self.assertEqual(g.moves,0)
        self.assertEqual(g.rng.getstate(),before)

    def test_undo_restores_random_sequence(self):
        g=Game(1);g.board=[2,2,0,0]+[0]*12
        before=g.board[:];g.move('left');after=g.board[:]
        self.assertTrue(g.undo());self.assertEqual(g.board,before);self.assertEqual(g.score,0)
        g.move('left');self.assertEqual(g.board,after)

    def test_game_over(self):
        full=[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2]
        self.assertFalse(can_move(full))
        full[0]=4;self.assertTrue(can_move(full))
        full[0]=0;self.assertTrue(can_move(full))

    def test_mass_and_tracks(self):
        rng=random.Random(4)
        for _ in range(1000):
            b=[rng.choice([0,2,4,8,16,32]) for _ in range(16)]
            for d in DIRECTIONS:
                out,gain,tracks,merged=slide(b,d)
                self.assertEqual(sum(out),sum(b))
                reconstructed=[0]*16
                for t in tracks:reconstructed[t.target]+=t.value
                self.assertEqual(out,reconstructed)

    def test_restore(self):
        g=Game(12);g.move('left');g.elapsed=42.4
        restored=Game.restore(g.serialize())
        self.assertEqual(g.serialize(),restored.serialize())
        with self.assertRaises(ValueError):Game.restore({'board':[3]*16})

    def test_atomic_save_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'save.json';s=Storage(path);g=Game(1);g.move('left')
            self.assertTrue(s.save(g,{'theme':'dark'}))
            self.assertEqual(Storage(path).data['game'],g.serialize())
            path.write_text('broken');self.assertIsNotNone(Storage(path).error)

class AITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):init_tables()

    def test_bitboard_matches_reference(self):
        rng=random.Random(45)
        for _ in range(3000):
            b=[rng.choice([0,2,4,8,16,32,64,128,256,1024,16384]) for _ in range(16)]
            p=pack(b);self.assertEqual(transpose(transpose(p)),p)
            for direction,fast in zip(DIRECTIONS,successors(p)):
                expected=slide(b,direction)[0]
                self.assertEqual(fast,pack(expected),(b,direction))

    def test_ai_chooses_valid_moves(self):
        ai=Expectimax();g=Game(4)
        for _ in range(35):
            result=ai.choose(g.board,.004)
            self.assertIsNotNone(g.move(result['direction'],True))

    def test_full_board_and_high_tile(self):
        ai=Expectimax()
        b=[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2]
        self.assertIsNone(ai.choose(b)['direction'])
        b=[32768,32768]+[0]*14
        result=ai.choose(b)
        self.assertNotEqual(slide(b,result['direction'])[0],b)

if __name__=='__main__':unittest.main(verbosity=2)
