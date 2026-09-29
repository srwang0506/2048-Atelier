import os,argparse,time,unittest
from queue import Queue
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame as pg
from game import Atelier

class InteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0))

    @classmethod
    def tearDownClass(cls):
        a=cls.app;a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()

    def setUp(self):
        a=self.app;a.new_game();a.cancel_input();a.motion=True;a.modal_progress=0
        a.game.board=[2,2]+[0]*14;a.toasts=[];a.draw();pg.event.clear()

    def test_hint_replaces_inflight_request(self):
        a=self.app;old=a.token;a.pending=(old,'auto',time.monotonic())
        with patch.object(a,'requests',Queue()) as requests,patch.object(a,'results',Queue()) as results:
            a.act('hint');self.assertEqual(a.manual_request,'hint')
            results.put((old,{'direction':'left'}));a.update(.01)
            token,board,budget=requests.get_nowait()[:3];self.assertEqual(token,a.token)
            self.assertEqual(a.pending[1],'hint');self.assertEqual(a.game.moves,0)
            # An old response cannot clear the new pending request.
            results.put((old,{'direction':'left'}));a.update(.01);self.assertIsNotNone(a.pending)
            results.put((token,{'direction':'right'}));a.update(.01)
            self.assertEqual(a.ai_result['direction'],'right');self.assertEqual(a.game.moves,0)

    def test_reanalysis_is_queued_inside_the_panel(self):
        a=self.app;a.pending=None
        with patch.object(a,'requests',Queue()) as requests,patch.object(a,'results',Queue()):
            a.act('intelligence');a.act('inspect_hint');a.update(.01)
            self.assertEqual(a.pending[1],'inspect');self.assertEqual(requests.get_nowait()[0],a.token)
        a.pending=None

    def test_escape_cancels_queued_directions(self):
        a=self.app;a.move('left');a.move('down');self.assertTrue(a.input_queue)
        pg.event.post(pg.event.Event(pg.KEYDOWN,key=pg.K_ESCAPE));a.events()
        self.assertFalse(a.input_queue);a.animation['start']-=1;a.update(.01)
        self.assertEqual(a.game.moves,1)

    def test_focus_loss_cancels_swipe_and_keys(self):
        a=self.app;a.move('left');a.move('down');a.swipe_start=(500,400);a.pointer_id='mouse'
        pg.event.post(pg.event.Event(pg.WINDOWFOCUSLOST));a.events()
        self.assertFalse(a.input_queue);self.assertIsNone(a.swipe_start);self.assertIsNone(a.pointer_id)
        a.pointer_up((300,400));self.assertEqual(a.game.moves,1)

    def test_buttons_activate_on_release_and_drag_out_cancels(self):
        a=self.app;r=next(r for k,r,e in a.buttons if k=='settings')
        a.pointer_down(r.center);self.assertIsNone(a.modal)
        a.pointer_up((20,20));self.assertIsNone(a.modal)
        a.pointer_down(r.center);a.pointer_up(r.center);self.assertEqual(a.modal,'settings')
        for _ in range(12):a.update(.02);a.draw()
        self.assertTrue(any(k=='close' for k,_,_ in a.buttons))
        a.act('close');a.pointer_down((600,450));a.pointer_up((400,450))
        self.assertEqual(a.game.moves,0)
        for _ in range(12):a.update(.02);a.draw()
        self.assertEqual(a.modal_progress,0)

    def test_touch_mouse_duplicates_do_not_move_twice(self):
        a=self.app;a.motion=False
        def point(x,y):return (round(a.offset[0]+x*a.factor),round(a.offset[1]+y*a.factor))
        sw,sh=a.screen.get_size();start=point(650,450);end=point(500,450)
        pg.event.post(pg.event.Event(pg.FINGERDOWN,x=start[0]/sw,y=start[1]/sh,finger_id=7))
        pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN,button=1,pos=start,touch=True))
        pg.event.post(pg.event.Event(pg.FINGERUP,x=end[0]/sw,y=end[1]/sh,finger_id=7))
        pg.event.post(pg.event.Event(pg.MOUSEBUTTONUP,button=1,pos=end,touch=True))
        a.events();self.assertEqual(a.game.moves,1)

    def test_redo_button_and_shortcut(self):
        a=self.app;a.motion=False;a.move('left');board=a.game.board[:];a.act('undo');a.draw()
        self.assertTrue(any(k=='redo' and enabled for k,_,enabled in a.buttons))
        pg.event.post(pg.event.Event(pg.KEYDOWN,key=pg.K_z,mod=pg.KMOD_SHIFT));a.events()
        self.assertEqual(a.game.board,board);self.assertEqual(a.game.moves,1)

    def test_fullscreen_remembers_the_resized_window(self):
        a=self.app;a.screen=pg.display.set_mode((940,690),pg.RESIZABLE)
        try:
            with patch.object(a,'set_display',side_effect=lambda size,flags:pg.Surface((1280,800) if size==(0,0) else size)):
                a.act('full');self.assertEqual(a.windowed_size,(940,690))
                a.act('full');self.assertEqual(a.screen.get_size(),(940,690))
        finally:a.screen=pg.display.set_mode((1080,820),pg.RESIZABLE)

if __name__=='__main__':unittest.main()
