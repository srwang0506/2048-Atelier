"""Time-based transitions and deadline-based frame pacing."""
import math
import time


def glide(t):
    t=max(0.,min(1.,t))
    return t*t*t*(t*(t*6-15)+10)


def effect(kind,age):
    """Return scale, opacity, and flash without locking the next move."""
    if kind=='spawn':
        t=max(0.,min(1.,age/.125));e=1-(1-t)**3
        return .90+.10*e,e,0.
    t=max(0.,min(1.,age/.18))
    return 1+.045*math.sin(math.pi*t)*math.exp(-2.6*t),1.,max(0.,1-t*2)*.5


def slide_time(tracks,fast=False):
    cells=max((abs(t.source%4-t.target%4)+abs(t.source//4-t.target//4) for t in tracks),default=1)
    return min(.21,.165+.02*(cells-1)) if not fast else min(.15,.115+.015*(cells-1))


class FramePacer:
    """Keep sub-millisecond deadlines instead of truncating 60/120 Hz to integer ms."""
    def __init__(self,hz=120):
        self.set_rate(hz);self.last=time.perf_counter();self.next=self.last
        self.fallback=False;self.fast_frames=0;self.blocking_frames=0;self.waited=None

    def set_rate(self,hz):
        self.hz=max(30,min(240,float(hz) or 120));self.period=1/self.hz

    def observe(self,frame_seconds,flip_seconds):
        # Some Cocoa surfaces report vsync even when flip returns immediately.
        # Detect that behavior from unpaced work, excluding our own waiting.
        fast=frame_seconds<self.period*.8 and flip_seconds<self.period*.1
        self.fast_frames=self.fast_frames+1 if fast else 0
        self.blocking_frames=self.blocking_frames+1 if flip_seconds>self.period*.2 else 0
        if self.fast_frames>=8:self.fallback=True
        elif self.blocking_frames>=4:self.fallback=False

    def tick(self,wait=True):
        now=time.perf_counter()
        if self.waited is not None and wait!=self.waited:self.next=self.last+self.period
        self.waited=wait
        if now-self.next>self.period*2:self.next=now
        remaining=self.next-now
        if wait:
            if remaining>.0006:time.sleep(remaining-.00035)
            while time.perf_counter()<self.next:pass
        now=time.perf_counter();dt=now-self.last;self.last=now
        self.next=self.next+self.period if wait else now+self.period
        return min(.05,max(.0001,dt))
