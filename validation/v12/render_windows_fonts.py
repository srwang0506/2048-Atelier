import os,sys,argparse,time,json,statistics
from pathlib import Path
os.environ['ATELIER_FONT_SOURCE']='bundled';os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy';os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
import pygame as pg
from typography import Face
from game import Atelier
from expedition import make_expedition,choose,search,ABILITIES
original=Face.render;samples=set();clipped=[];missing=[]
def checked(self,text,antialias,color):
    key=(str(text),self.pixels,self.path,self.index)
    if key not in samples:
        samples.add(key);glyph,bounds=self.native.render(str(text),color);area=glyph.get_bounding_rect().move(max(0,bounds.x),self.baseline-bounds.y)
        if not pg.Rect((0,0),self.size(text)).contains(area):clipped.append(str(text))
        for char,metric in zip(str(text),self.native.get_metrics(str(text))):
            if metric is None and not char.isspace():missing.append(char)
    return original(self,text,antialias,color)
Face.render=checked

def main():
    previews=root/'validation/v12/previews';previews.mkdir(parents=True,exist_ok=True)
    a=Atelier(argparse.Namespace(demo=True,screenshot=None,smoke_seconds=0));a.motion=False;a.sound=False;a.coach=False;shots=[]
    def shot(name):
        a.mouse=(-100,-100);a.hover_values.clear();a.toasts=[];a.score_display=float(a.game.score);a.modal_progress=float(bool(a.modal));a.draw()
        pg.image.save(a.capture_surface(),str(previews/('2048-v12-windows-font-'+name+'.png')));shots.append(name)
    try:
        a.act('lobby');shot('classic-lobby');a.act('tab_featured');shot('featured')
        a.act('expedition_intro');shot('expedition-intro');a.act('expedition_new');shot('draft');a.act('perk_combo')
        # A real seeded run supplies a developed build for the visual preview.
        g=make_expedition(13);choose(g,'combo');priority=['combo','flow','echo','gambit','reserve','battery','corner','warp','ice']
        for _ in range(500):
            if g.extra['phase']=='clear':
                if g.extra['stage']==2:break
                choose(g,min(g.extra['offers'],key=priority.index))
            if g.extra['phase'] in ('won','lost'):break
            r=search(g.board,g.extra,.015)
            if not r['direction']:break
            g.move(r['direction'],True)
        a.activate_game(g);shot('upgrade')
        if g.extra['phase']=='clear':a.act('perk_'+g.extra['offers'][0])
        a.act('close');shot('expedition-game')
        a.act('swap');filled=[i for i,v in enumerate(a.game.board) if v]
        if filled:a.act('swapcell_'+str(filled[0]))
        shot('swap');a.act('close');a.act('expedition_rules');shot('abilities');a.act('close')
        a.act('expedition_intro');a.act('expedition_new');shot('restart');a.act('close')
        a.act('rescue_library');shot('rescue-empty');a.act('rescue_practice');shot('rescue-library')
        c=a.practice[1];a.act('rescue_play_'+c['id']);shot('rescue-game')
        for d in c['solution']:a.move(d)
        a.update(.01);shot('rescue-win');a.act('rescue_review');a.act('review_original')
        for _ in range(c['par']):a.act('review_next')
        shot('rescue-review')
        a.act('close');a.act('theme');a.act('lobby');a.act('tab_featured');shot('dark')
        a.act('mode_expedition');a.act('expedition_rules');shot('dark-abilities')
        # Render both tiers of every offer to check actual Chinese and symbols.
        a.game=make_expedition(0);a.modal='draft'
        keys=list(ABILITIES)
        for rank in (1,2):
            a.game.extra['perks']={k:1 for k in keys} if rank==2 else {}
            for start in range(0,len(keys),3):a.game.extra['offers']=keys[start:start+3];a.draw()
        assert not clipped and not missing,(clipped,missing)
        # Stable CPU render cost only; this is not a display/vsync measurement.
        a.game=make_expedition(0);choose(a.game,'combo');a.modal=None;a.modal_progress=0.;a.draw();timings=[]
        for _ in range(45):
            t=time.perf_counter();a.draw();timings.append((time.perf_counter()-t)*1000)
        report=dict(views=shots,font_samples=len(samples),clipped=clipped,missing=missing,driver=pg.display.get_driver(),steady_draw_ms=dict(median=round(statistics.median(timings),2),p95=round(sorted(timings)[42],2)))
        (root/'validation/v12/windows-font-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    finally:
        a.requests.put(None);a.process.join(timeout=2)
        if a.process.is_alive():a.process.terminate();a.process.join(timeout=1)
        pg.quit()
if __name__=='__main__':main()
