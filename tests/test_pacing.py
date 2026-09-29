import unittest
from unittest.mock import patch
from motion import FramePacer

class PacingTests(unittest.TestCase):
    def test_reported_vsync_that_does_not_wait_uses_fallback(self):
        pacer=FramePacer(75)
        for _ in range(8):pacer.observe(.005,.0004)
        self.assertTrue(pacer.fallback)
        for _ in range(4):pacer.observe(1/75,.008)
        self.assertFalse(pacer.fallback)

    def test_slow_work_does_not_misclassify_vsync(self):
        pacer=FramePacer(60)
        for _ in range(20):pacer.observe(.020,.0003)
        self.assertFalse(pacer.fallback)

    def test_native_frames_do_not_accumulate_future_sleep(self):
        # When native vsync stops waiting, the fallback must target one period
        # ahead, not a deadline accumulated over hundreds of unpaced frames.
        with patch('motion.time.perf_counter',return_value=100.):pacer=FramePacer(75)
        for i in range(1,100):
            now=100+i*.005
            with patch('motion.time.perf_counter',return_value=now):pacer.tick(wait=False)
        self.assertAlmostEqual(pacer.next-pacer.last,1/75)

if __name__=='__main__':unittest.main()
