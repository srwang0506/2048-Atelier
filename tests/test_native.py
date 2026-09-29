import sys,random,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import slide,DIRECTIONS,Game
from search_native import NativeSearch,pack,move,transpose

class NativeSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ai=NativeSearch()

    def test_80_bit_rules_including_65536(self):
        rng=random.Random(71)
        for _ in range(2000):
            board=[rng.choice([0,2,4,8,16,128,1024,16384,32768,65536,1048576]) for _ in range(16)]
            a,b=pack(board)
            self.assertEqual(transpose(*transpose(a,b)),(a,b))
            for d,name in enumerate(DIRECTIONS):
                target=slide(board,name)[0]
                self.assertEqual(move(a,b,d,self.ai.left,self.ai.right),pack(target))

    def test_four_direction_values_and_high_rank_search(self):
        result=self.ai.choose([32768,32768,2,0]+[0]*12,.025)
        self.assertGreaterEqual(result['depth'],1)
        self.assertEqual(result['backend'],'native')
        self.assertGreater(result['nodes'],0)
        self.assertNotEqual(slide([32768,32768,2,0]+[0]*12,result['direction'])[0],[32768,32768,2,0]+[0]*12)

    def test_cached_search_retains_valid_directions(self):
        game=Game(73)
        hits=0
        for _ in range(25):
            result=self.ai.choose(game.board,.007)
            hits+=result['hits'];self.assertIsNotNone(game.move(result['direction']))
        self.assertGreater(hits,0)

if __name__=='__main__':unittest.main(verbosity=2)
