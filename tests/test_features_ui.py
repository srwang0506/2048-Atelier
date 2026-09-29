import os,argparse,time,unittest
from queue import Queue
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame as pg
from game import Atelier
from engine import Game
from insight import enrich,analyze_moves

class FeatureUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))
    @classmethod
    def tearDownClass(cls):
        a=cls.app;a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()
    def setUp(self):
        a=self.app;a.game=Game(17);a.coach=False;a.new_game();a.game.board=[2,2]+[0]*14
        a.cancel_input();a.modal_progress=0;a.motion=False;a.pending=None;a.coach_token=None
        a.sessions.sessions={};a.sessions.sync();a.draw();pg.event.clear()

    def test_switching_modes_restores_live_state(self):
        a=self.app;a.move('left');classic=a.game.serialize();token=a.token
        a.act('mode_daily');self.assertEqual(a.game.mode,'daily');self.assertGreater(a.token,token)
        a.move('down');daily=a.game.serialize()
        a.act('mode_classic');self.assertEqual(a.game.serialize(),classic)
        a.act('mode_daily');self.assertEqual(a.game.serialize(),daily)
        a.act('new');a.act('confirm_new');self.assertEqual(a.game.mode,'daily');self.assertEqual(a.game.moves,0)
        a.act('mode_classic');self.assertEqual(a.game.serialize(),classic)

    def test_coach_does_not_move_or_reuse_stale_advice(self):
        a=self.app;a.coach=True;a.ai_ready=True;a.focused=True;a.coach_seen=a.token;a.coach_due=0
        with patch.object(a,'requests',Queue()) as requests,patch.object(a,'results',Queue()) as results:
            a.update(.01);packet=requests.get_nowait();self.assertEqual(a.pending[1],'coach')
            self.assertTrue(packet[3]['adaptive']);self.assertEqual(a.game.moves,0)
            result=enrich(a.game.board,{'direction':'left','values':[('left',1),('right',0)]})
            results.put((packet[0],result));a.update(.01)
            self.assertEqual(a.game.moves,0);self.assertTrue(requests.empty());self.assertTrue(a.game.assisted)
            a.act('coach');self.assertFalse(a.coach);self.assertIsNone(a.ai_result)
            a.act('coach');a.coach_due=0;a.update(.01);packet=requests.get_nowait()
            a.move('right');a.coach=False;results.put((packet[0],result));a.update(.01)
            self.assertIsNone(a.ai_result);self.assertEqual(a.game.moves,1)

    def test_replay_and_seek_are_read_only(self):
        a=self.app
        for d in ['left','down','right','up']*6:a.move(d)
        before=a.game.serialize();a.act('replay');a.draw()
        self.assertEqual(a.review_index,len(a.review_frames)-1)
        a.act('replay_first');self.assertEqual(a.review_index,0)
        a.act('replay_play');a.review_tick=0;a.update(.01)
        self.assertEqual(a.review_index,1)
        a.mouse=(808,550);a.act('replay_seek');self.assertEqual(a.review_index,len(a.review_frames)-1)
        self.assertEqual(a.game.serialize(),before);a.act('close');self.assertFalse(a.review_playing)

    def test_direction_previews_do_not_execute_moves(self):
        a=self.app;choices=analyze_moves(a.game.board)
        a.ai_result=enrich(a.game.board,{'direction':'left','values':[(d,float(i)) for i,d in enumerate(choices)]})
        a.act('intelligence');a.modal_progress=1
        before=a.game.serialize()
        for direction in choices:
            a.act('preview_'+direction);a.draw()
            self.assertEqual(a.preview_direction,direction)
        self.assertEqual(a.game.serialize(),before)
        self.assertTrue(any(k=='inspect_hint' for k,_,_ in a.buttons))

if __name__=='__main__':unittest.main()
