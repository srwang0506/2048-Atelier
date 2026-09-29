"""2048 Atelier — a small, carefully animated Python desktop game."""
from __future__ import annotations
import argparse
from array import array
import math
import multiprocessing as mp
import os
from pathlib import Path
from queue import Empty
import random
import time
import webbrowser

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
from engine import Game, Storage, can_move
from ai import worker
from platform_paths import save_path,export_dir

ROOT = Path(__file__).resolve().parent
W, H, S = 1180, 870, 2
BX, BY, BS, GAP, PAD = 70, 247, 548, 12, 16
CELL = (BS - PAD*2 - GAP*3)/4
ARROWS = {'left':'←', 'up':'↑', 'right':'→', 'down':'↓'}
DARK = dict(bg='#101c25', panel='#192832', board='#21343e', slot='#2a3e47', line='#30434d', text='#edf2ed', muted='#849ba6', accent='#b2e8ce', ink='#173c34', soft='#243b43', gold='#e8c491', shadow='#0b151e')
LIGHT = dict(bg='#f4f2ea', panel='#fffdf6', board='#dfE5da', slot='#cfd8ce', line='#dedfd5', text='#263e38', muted='#7b8c81', accent='#337b60', ink='#ffffff', soft='#e9eee3', gold='#a17a37', shadow='#e3e4db')
PALETTE = {2:('#e1e8dd','#324d42'),4:('#c5dcca','#2f5344'),8:('#a6cfb7','#254c3b'),16:('#80bfa4','#204c3b'),32:('#61a98f','#effaf0'),64:('#438e78','#f6fcf0'),128:('#d9c49a','#574a31'),256:('#e9c18b','#694b2e'),512:('#e8a674','#fff8e8'),1024:('#d78865','#fff6e9'),2048:('#f1d795','#5b4827'),4096:('#c9b0db','#463351'),8192:('#a6c8e0','#24455b'),16384:('#8ba9d4','#f3f6ff'),32768:('#df9bac','#5b2b45')}


def rgb(color): return pg.Color(color)
def blend(a,b,t):
    a,b = rgb(a),rgb(b)
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
def rect(x,y,w,h): return pg.Rect(round(x*S),round(y*S),round(w*S),round(h*S))

def ease(t): return 1-(1-max(0,min(1,t)))**3


class Atelier:
    def __init__(self, args):
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.args = args
        desktop=pg.display.get_desktop_sizes()[0]
        fit=min(1,(desktop[0]-70)/W,(desktop[1]-120)/H)
        self.windowed_size=(round(W*fit),round(H*fit))
        self.screen = self.set_display(self.windowed_size,pg.RESIZABLE)
        pg.display.set_caption('2048 Atelier · 数字之间，自有美感')
        self.canvas = pg.Surface((W*S,H*S)).convert()
        self.clock = pg.time.Clock()
        self.fonts, self.texts, self.tiles = {}, {}, {}
        self.store = Storage(save_path(args.demo))
        settings = self.store.data['settings']
        self.theme = settings.get('theme','dark') if settings.get('theme') in ('dark','light') else 'dark'
        self.sound = bool(settings.get('sound',True))
        self.motion = bool(settings.get('motion',True))
        self.quality = settings.get('quality',3) if settings.get('quality',3) in (0,1,2,3) else 3
        self.speed = settings.get('speed',1) if settings.get('speed',1) in (0,1,2,3) else 1
        self.game = Game()
        if self.store.data.get('game') and not args.demo:
            try: self.game = Game.restore(self.store.data['game'])
            except (ValueError,KeyError,TypeError): self.store.error = '存档格式异常，已开启新游戏'
        self.auto = False
        self.pending = None
        self.queued_ai = None
        self.manual_request = None
        self.token = 0
        self.ai_result = None
        self.ai_error = None
        self.ai_ready = False
        self.requests = mp.Queue()
        self.results = mp.Queue()
        self.process = mp.Process(target=worker,args=(self.requests,self.results),daemon=True)
        self.process.start()
        self.animation = None
        self.particles = []
        self.toasts = []
        self.buttons = []
        self.mouse = (-100,-100)
        self.modal = None
        self.stats_tab = 'records'
        self.running = True
        self.fullscreen = False
        self.next_auto = 0
        self.last_save = time.monotonic()
        self.save_ok = True
        self.saver = None
        self.score_display = float(self.game.score)
        self.last_gain = None
        self.swipe_start = None
        self.played = self.game.moves > 0
        self.won = max(self.game.board) >= 2048
        self.focused = True
        self.ended = not can_move(self.game.board)
        self.sounds = self.make_sounds()
        self.known_achievements = set(self.store.data['achievements'])
        if self.store.error: self.toast(self.store.error)
        if args.demo:
            self.game.board = [2,4,8,16,4,16,32,64,8,64,128,256,0,2,512,1024]
            self.game.score,self.game.moves,self.game.elapsed = 14832,426,768
            self.store.data['best'] = 28640
            self.score_display = 14832
            self.ai_result = {'direction':'down','depth':4,'nodes':18246,'ms':121}
        icon = pg.Surface((64,64),pg.SRCALPHA)
        pg.draw.rect(icon, '#b2e8ce',(0,0,64,64),border_radius=16)
        f = self.font(19,'number')
        word = f.render('2048',True,'#173c34')
        word = pg.transform.smoothscale(word,(54,26))
        icon.blit(word,(5,19)); pg.display.set_icon(icon)

    @property
    def p(self): return DARK if self.theme == 'dark' else LIGHT

    def set_display(self,size,flags):
        if pg.display.get_driver()=='dummy':return pg.display.set_mode(size,flags)
        try:return pg.display.set_mode(size,flags,vsync=1)
        except pg.error:return pg.display.set_mode(size,flags)

    def font(self,size,kind='body'):
        key = (size,kind)
        if key not in self.fonts:
            candidates = {
                'body':['/System/Library/Fonts/Hiragino Sans GB.ttc','/System/Library/Fonts/PingFang.ttc','C:/Windows/Fonts/msyh.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'],
                'latin':['/System/Library/Fonts/Avenir Next.ttc','/System/Library/Fonts/Supplemental/Arial.ttf'],
                'number':['/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf']
            }[kind]
            path = next((x for x in candidates if Path(x).exists()),None)
            self.fonts[key] = pg.font.Font(path,round(size*S))
        return self.fonts[key]

    def text(self,value,x,y,size=16,color=None,kind=None,anchor='topleft',alpha=255):
        value = str(value)
        kind = kind or ('body' if any(ord(c)>127 for c in value) else 'latin')
        color = color or self.p['text']
        key = (value,size,color,kind)
        if key not in self.texts:
            if len(self.texts)>1800: self.texts.clear()
            self.texts[key] = self.font(size,kind).render(value,True,color)
        surf = self.texts[key]
        if alpha != 255: surf = surf.copy(); surf.set_alpha(alpha)
        r = surf.get_rect(**{anchor:(round(x*S),round(y*S))})
        self.canvas.blit(surf,r)

    def box(self,x,y,w,h,color,radius=16,border=None,width=1):
        pg.draw.rect(self.canvas,color,rect(x,y,w,h),border_radius=round(radius*S))
        if border: pg.draw.rect(self.canvas,border,rect(x,y,w,h),round(width*S),border_radius=round(radius*S))

    def line(self,a,b,color=None,width=1):
        pg.draw.line(self.canvas,color or self.p['line'],(a[0]*S,a[1]*S),(b[0]*S,b[1]*S),max(1,round(width*S)))

    def circle(self,x,y,r,color): pg.draw.circle(self.canvas,color,(round(x*S),round(y*S)),round(r*S))

    def icon(self,name,x,y,color=None,size=20):
        color = color or self.p['text']; k = size/20
        def ln(a,b): self.line((x+a[0]*k,y+a[1]*k),(x+b[0]*k,y+b[1]*k),color,1.6)
        if name in ('left','right','up','down'):
            pts = {'left':[(14,4),(8,10),(14,16)],'right':[(6,4),(12,10),(6,16)],'up':[(4,13),(10,7),(16,13)],'down':[(4,7),(10,13),(16,7)]}[name]
            ln(pts[0],pts[1]); ln(pts[1],pts[2])
        elif name=='play':
            pg.draw.polygon(self.canvas,color,[(int((x+a*k)*S),int((y+b*k)*S)) for a,b in [(6,3),(17,10),(6,17)]])
        elif name=='pause':
            for a in [5,12]: self.box(x+a*k,y+4*k,3*k,12*k,color,1)
        elif name=='undo':
            ln((8,3),(3,8));ln((3,8),(8,13));ln((3,8),(13,8));ln((13,8),(17,12));ln((17,12),(17,17));ln((17,17),(9,17))
        elif name=='plus': ln((10,3),(10,17));ln((3,10),(17,10))
        elif name=='spark':
            for a,b in [((10,0),(10,20)),((0,10),(20,10)),((3,3),(17,17)),((3,17),(17,3))]: ln(a,b)
        elif name=='sun':
            pg.draw.circle(self.canvas,color,(round((x+10*k)*S),round((y+10*k)*S)),round(4*k*S),2*S)
            for angle in range(0,360,45):
                a=math.radians(angle);ln((10+7*math.cos(a),10+7*math.sin(a)),(10+9*math.cos(a),10+9*math.sin(a)))
        elif name=='help': self.text('?',x+10*k,y+10*k,19,color,'number','center')
        elif name=='full':
            for a,b,c in [((1,7),(1,1),(7,1)),((13,1),(19,1),(19,7)),((1,13),(1,19),(7,19)),((13,19),(19,19),(19,13))]: ln(a,b);ln(b,c)
        elif name=='sound':
            for a,b in [((2,7),(6,7)),((6,7),(11,3)),((11,3),(11,17)),((11,17),(6,13)),((6,13),(2,13)),((2,13),(2,7)),((15,6),(18,10)),((18,10),(15,14))]: ln(a,b)
        elif name=='check': ln((3,10),(8,15));ln((8,15),(17,5))
        elif name=='trophy':
            for a,b in [((4,3),(16,3)),((4,3),(6,12)),((16,3),(14,12)),((6,12),(14,12)),((10,12),(10,17)),((6,18),(14,18))]:ln(a,b)
        elif name=='close':ln((5,5),(15,15));ln((15,5),(5,15))

    def button(self,key,x,y,w,h,label='',icon=None,primary=False,selected=False,enabled=True,small=False):
        r = pg.Rect(x,y,w,h)
        hover = r.collidepoint(self.mouse) and not self.modal
        p = self.p
        color = p['accent'] if primary else (p['soft'] if selected or hover else p['panel'])
        if hover and primary: color = blend(p['accent'],'#ffffff',.12)
        if not enabled: color = p['panel']
        self.box(x,y,w,h,color,12,p['line'] if not primary and not selected else None)
        fg = p['ink'] if primary else p['text'] if enabled else p['muted']
        if icon: self.icon(icon,x+(16 if label else (w-20)/2),y+(h-20)/2,fg)
        if label:
            if icon: self.text(label,x+45,y+h/2,14 if small else 15,fg,anchor='midleft')
            else: self.text(label,x+w/2,y+h/2,14 if small else 15,fg,anchor='center')
        self.buttons.append((key,r,enabled))

    def make_sounds(self):
        result = {}
        if not pg.mixer.get_init(): return result
        try:
            for name,freq,duration in [('move',330,.055),('merge',660,.14),('win',880,.4)]:
                samples = array('h')
                for i in range(int(44100*duration)):
                    t=i/44100;env=min(1,t/.008)*math.exp(-t/(duration*.3))
                    v=(math.sin(2*math.pi*freq*t)+.25*math.sin(2*math.pi*freq*2*t))*env*.13
                    samples.append(int(32767*v))
                result[name] = pg.mixer.Sound(buffer=samples)
        except pg.error: pass
        return result

    def play_sound(self,name):
        if self.sound and name in self.sounds: self.sounds[name].play()

    def toast(self,message): self.toasts.append((message,time.monotonic()))

    def invalidate_ai(self):
        self.token += 1
        self.ai_result = None
        self.queued_ai = None
        # An old result will be discarded by token; do not flood the worker queue.

    def ask_ai(self,kind):
        if self.pending is not None or self.ended: return
        if not self.process.is_alive():
            self.auto=False;self.ai_error='AI 进程已退出，请重新打开游戏';self.toast(self.ai_error);return
        self.pending = (self.token,kind,time.monotonic())
        self.game.assisted=True
        packet=(self.token,self.game.board[:],.045 if kind=='coach' else [.025,.10,.45,.12][self.quality])
        options=self.ai_options(kind)
        self.requests.put(packet+(options,) if options else packet)

    def ai_options(self,kind):
        adaptive=self.quality==3 or kind=='coach'
        return {'adaptive':adaptive,'refresh':kind=='inspect'} if adaptive or kind=='inspect' else {}

    def stop_auto(self): self.auto=False;self.manual_request=None;self.invalidate_ai()

    def move(self,direction,by_ai=False):
        if self.modal or self.animation or self.ended: return
        if not by_ai: self.stop_auto()
        data = self.game.move(direction,by_ai)
        if not data:
            self.toast('这个方向已没有空间') if not by_ai else None
            return
        self.played = True
        if data['gain']:self.last_gain=(data['gain'],time.monotonic())
        self.invalidate_ai()
        self.animation = dict(data,start=time.monotonic(),burst=False) if self.motion and not (self.auto and self.speed==3) else None
        if self.game.mode not in ('puzzle','sprint','expedition','rescue'):self.store.data['best'] = max(self.store.data['best'],self.game.score)
        self.play_sound('merge' if data['gain'] else 'move')
        self.next_auto = time.monotonic()+[.85,.34,.11,0][self.speed]
        self.ended = not can_move(self.game.board)
        self.check_achievements()
        if self.ended:
            self.auto=False;self.store.record(self.game);self.save()
        if max(self.game.board)>=2048 and not self.won:
            self.won=True;self.toast('目标达成，这个残局解开了。' if self.game.mode=='puzzle' else '2048 达成！继续，探索更大的数字。');self.play_sound('win')

    def check_achievements(self):
        for tile in [128,512,2048,8192,16384,32768]:
            if max(self.game.board)>=tile and tile not in self.known_achievements:
                self.known_achievements.add(tile)
                self.toast(f'里程碑解锁 · {tile:,}')
        self.store.data['achievements'] = sorted(self.known_achievements)

    def save(self):
        if self.args.demo: return
        if self.saver is None:
            from persistence import SaveService
            self.saver=SaveService(self.store.path)
        self.saver.submit(self.game,dict(theme=self.theme,sound=self.sound,motion=self.motion,quality=self.quality,speed=self.speed,coach=getattr(self,'coach',False)),self.store.data)
        self.last_save=time.monotonic()

    def flush_save(self):
        if self.saver:
            results=self.saver.close();self.saver=None
            if results:self.save_ok=results[-1] is None

    def new_game(self):
        self.stop_auto();self.store.record(self.game)
        self.game=self.make_new_game();self.score_display=0;self.animation=None;self.particles=[]
        self.won=self.ended=self.played=False;self.modal=None;self.save();self.toast('新的开始。让灵感流动。')

    def make_new_game(self):return Game()

    def act(self,key):
        if key=='auto':
            if self.ended: return
            self.auto=not self.auto;self.invalidate_ai()
            if self.auto: self.next_auto=0
        elif key in ('undo','redo'):
            self.stop_auto()
            if getattr(self.game,key)():
                self.animation=None;self.particles=[];self.ended=not can_move(self.game.board)
                self.won=max(self.game.board)>=2048;self.played=self.game.moves>0;self.last_gain=None
                self.score_display=float(self.game.score);self.save();self.toast('已撤销上一步' if key=='undo' else '已重做一步')
            else:self.toast('没有可撤销的步骤' if key=='undo' else '没有可重做的步骤')
        elif key=='hint':
            self.stop_auto();self.manual_request='hint'
        elif key=='step':
            self.stop_auto();self.manual_request='step'
        elif key=='new':
            self.stop_auto()
            if self.game.moves:self.modal='new'
            else:self.new_game()
        elif key=='confirm_new': self.new_game()
        elif key=='cancel' or key=='close':self.modal=None
        elif key=='theme':
            self.theme='light' if self.theme=='dark' else 'dark';self.tiles.clear();self.save()
        elif key=='sound':self.sound=not self.sound;self.save();self.toast('音效已开启' if self.sound else '音效已关闭')
        elif key=='motion':self.motion=not self.motion;self.animation=None;self.save()
        elif key=='full':
            if not self.fullscreen:self.windowed_size=self.screen.get_size()
            self.fullscreen=not self.fullscreen
            self.screen=self.set_display((0,0) if self.fullscreen else self.windowed_size,pg.FULLSCREEN if self.fullscreen else pg.RESIZABLE)
        elif key in ('help','records'):
            self.stop_auto();self.modal=key
        elif key.startswith('quality'):
            self.quality=int(key[-1]);self.invalidate_ai();self.save()
        elif key.startswith('speed'):
            self.speed=int(key[-1]);self.save()
        elif key=='export':
            try:
                out=export_dir();out.mkdir(parents=True,exist_ok=True)
                path=out/(time.strftime('2048-%Y%m%d-%H%M%S-')+str(time.time_ns()%1_000_000_000)+'.png')
                surface=self.capture_surface() if hasattr(self,'capture_surface') else self.canvas
                pg.image.save(surface,str(path));self.toast('截图已保存到 exports 文件夹')
            except (OSError,pg.error):self.toast('截图保存失败，请检查磁盘空间或文件夹权限')

    def tile(self,value,x,y,scale=1,glow=0):
        if not value:return
        size=round(CELL*S)
        key=(value,self.theme)
        if key not in self.tiles:
            base,fg=PALETTE.get(value,('#dbaed2','#54344f'))
            surf=pg.Surface((size+16*S,size+16*S),pg.SRCALPHA)
            rr=pg.Rect(8*S,8*S,size,size)
            pg.draw.rect(surf,(0,0,0,22),rr.move(0,4*S),border_radius=15*S)
            pg.draw.rect(surf,base,rr,border_radius=15*S)
            # Subtle inner edge and a satin highlight.
            pg.draw.rect(surf,blend(base,'#ffffff',.2),rr,1*S,border_radius=15*S)
            pg.draw.line(surf,blend(base,'#ffffff',.26),(rr.left+18*S,rr.top+2*S),(rr.right-18*S,rr.top+2*S),S)
            font_size=44 if value<100 else 40 if value<1000 else 34 if value<10000 else 28
            word=self.font(font_size,'number').render(str(value),True,fg)
            surf.blit(word,word.get_rect(center=rr.center))
            self.tiles[key]=surf
        surf=self.tiles[key]
        if abs(scale-1)>.002:
            surf=pg.transform.smoothscale(surf,(max(1,round(surf.get_width()*scale)),max(1,round(surf.get_height()*scale))))
        self.canvas.blit(surf,surf.get_rect(center=(round((x+CELL/2)*S),round((y+CELL/2)*S))))

    def cell_xy(self,index):return BX+PAD+(index%4)*(CELL+GAP),BY+PAD+(index//4)*(CELL+GAP)

    def burst(self,index,value):
        x,y=self.cell_xy(index);color=PALETTE.get(value,PALETTE[2048])[0]
        for _ in range(9):
            angle=random.random()*math.tau;speed=random.uniform(25,110)
            self.particles.append([x+CELL/2,y+CELL/2,math.cos(angle)*speed,math.sin(angle)*speed,random.uniform(.3,.6),color,random.uniform(1.5,3)])

    def draw_board(self,now):
        p=self.p
        self.box(BX,BY+8,BS,BS,p['shadow'],25)
        self.box(BX,BY,BS,BS,p['board'],24,p['line'])
        for i in range(16):
            x,y=self.cell_xy(i);self.box(x,y,CELL,CELL,p['slot'],15)
        anim=self.animation
        if anim:
            duration=.115 if self.auto and self.speed==2 else .16
            elapsed=now-anim['start'];t=elapsed/duration
            if t<1:
                for track in anim['tracks']:
                    x,y=self.cell_xy(track.source);tx,ty=self.cell_xy(track.target)
                    self.tile(track.value,x+(tx-x)*ease(t),y+(ty-y)*ease(t))
            else:
                u=(elapsed-duration)/(.09 if self.auto and self.speed==2 else .20)
                if not anim['burst']:
                    for i in anim['merges']:self.burst(i,self.game.board[i])
                    anim['burst']=True
                for i,v in enumerate(self.game.board):
                    scale=1
                    if i in anim['merges']:scale=1+.11*math.sin(min(1,u)*math.pi)*(1-min(1,u))
                    if i==anim['spawn']:scale=.25+.75*ease(min(1,u*1.5))
                    self.tile(v,*self.cell_xy(i),scale)
                if u>=1:self.animation=None
        else:
            for i,v in enumerate(self.game.board):self.tile(v,*self.cell_xy(i))
        for x,y,vx,vy,life,color,r in self.particles:
            self.circle(x,y,max(.3,r*min(1,life*3)),color)
        if self.ended and not self.animation:
            veil=pg.Surface((BS*S,BS*S),pg.SRCALPHA);veil.fill((12,26,30,170));self.canvas.blit(veil,(BX*S,BY*S))
            self.text('这一局，很精彩。',BX+BS/2,BY+BS/2-42,30,'#ffffff',anchor='center')
            self.text(f'{self.game.score:,} 分  ·  最大方块 {max(self.game.board):,}',BX+BS/2,BY+BS/2+2,17,'#d6e4da',anchor='center')
            self.button('new',BX+BS/2-88,BY+BS/2+42,176,48,'再来一局',icon='plus',primary=True)

    def draw(self):
        now=time.monotonic();p=self.p;self.buttons=[]
        self.canvas.fill(p['bg'])
        # Small editorial masthead.
        for i in range(2):
            for j in range(2):self.box(70+j*9,43+i*9,6,6,p['accent'],2)
        self.text('ATELIER  /  2048',100,39,17,p['text'],'latin')
        self.text('A LITTLE SPACE TO THINK',70,72,10,p['muted'],'latin')
        self.text('数字之间，自有美感。',666,48,13,p['muted'])
        for key,x in [('sound',932),('theme',980),('help',1028),('full',1076)]:
            self.button(key,x,34,36,36,icon={'theme':'sun',**{k:k for k in ['sound','help','full']}}[key],selected=key=='sound' and self.sound)
        self.line((70,101),(1110,101))
        self.text('2048',66,113,94,p['text'],'number')
        self.text('合并数字，让可能不断生长。',72,215,15,p['muted'])
        for x,label,value in [(333,'当前得分',round(self.score_display)),(480,'历史最佳',self.store.data['best'])]:
            self.box(x,141,138,66,p['panel'],13)
            self.text(label,x+16,150,11,p['muted'])
            size=28 if len(f'{value:,}')<8 else 23
            self.text(f'{value:,}',x+16,168,size,p['gold'] if x==480 else p['text'],'number')
        if self.last_gain and self.motion:
            gain,stamp=self.last_gain;age=now-stamp
            if age<.75:self.text(f'+{gain:,}',454,133-age*25,17,p['accent'],'number',anchor='topright',alpha=round(255*(1-age/.75)))
        self.text('慢慢来，也可以交给灵感。',666,140,23,p['text'])
        self.text('经典规则。无限可能。',666,183,14,p['muted'])
        self.draw_board(now)
        self.draw_ai(now)
        self.draw_stats()
        self.draw_achievements()
        self.text('方向键 / WASD 移动',70,820,13,p['muted'])
        self.text('空格 自动驾驶   ·   Z 撤销   ·   H 提示',618,820,12,p['muted'],anchor='topright')
        self.text('CRAFTED IN PYTHON',1110,820,10,p['muted'],'latin',anchor='topright')
        if self.modal:self.draw_modal()
        self.toasts=[t for t in self.toasts if now-t[1]<3.4]
        for index,(msg,start) in enumerate(self.toasts[-2:]):
            age=now-start;y=H-100-index*49
            width=min(780,self.font(14).size(msg)[0]/S+54)
            self.box((W-width)/2,y,width,40,p['accent'],12)
            self.text(msg,W/2,y+20,14,p['ink'],anchor='center')
        sw,sh=self.screen.get_size();factor=min(sw/W,sh/H)
        dw,dh=round(W*factor),round(H*factor);self.offset=((sw-dw)//2,(sh-dh)//2);self.factor=factor
        self.screen.fill(p['bg'])
        scaled=pg.transform.smoothscale(self.canvas,(dw,dh))
        self.screen.blit(scaled,self.offset)
        pg.display.flip()

    def draw_ai(self,now):
        p=self.p;x=666;y=247;w=444
        self.box(x,y,w,290,p['panel'],20,p['line'])
        self.box(x+22,y+23,36,36,p['soft'],11);self.icon('spark',x+30,y+31,p['accent'])
        self.text('自动驾驶',x+71,y+20,20)
        self.text('为每一步，多想几步',x+71,y+49,11,p['muted'])
        self.button('auto',x+309,y+23,111,39,'暂停' if self.auto else '启动',icon='pause' if self.auto else 'play',primary=True,enabled=not self.ended,small=True)
        self.line((x+24,y+84),(x+w-24,y+84))
        self.text('思考深度',x+24,y+105,12,p['muted'])
        for i,label in enumerate(['灵巧','均衡','深度']):self.button(f'quality{i}',x+116+i*99,y+97,92,34,label,selected=self.quality==i,small=True)
        self.text('播放速度',x+24,y+153,12,p['muted'])
        for i,label in enumerate(['舒缓','流畅','极速']):self.button(f'speed{i}',x+116+i*99,y+145,92,34,label,selected=self.speed==i,small=True)
        self.circle(x+28,y+211,3.5,p['accent'] if self.auto else p['muted'])
        if self.pending:
            dots='.'*(int(now*3)%4)
            status='正在寻找更好的下一步'+dots
        elif self.auto:status='自动驾驶中 · 随时按空格接管'
        elif self.ai_result and self.ai_result.get('direction'):status='建议方向：'+{'left':'向左','right':'向右','up':'向上','down':'向下'}[self.ai_result['direction']]
        else:status='随时开启，看看数字能走多远'
        self.text(status,x+42,y+201,12,p['muted'])
        if self.ai_result:
            r=self.ai_result
            self.text(f"{r.get('depth',0)} 层前瞻  /  {r.get('nodes',0):,} 个局面  /  {r.get('ms',0)} ms",x+24,y+234,11,p['muted'])
        else:self.text('概率搜索  ×  空间规划  ×  单调排列',x+24,y+234,11,p['muted'])
        self.icon('spark',x+w-40,y+239,p['muted'],12)

    def draw_stats(self):
        p=self.p;x=666
        for key,bx,w,label,icon in [('undo',x,140,'撤销','undo'),('hint',x+152,140,'提示','spark'),('new',x+304,140,'新一局','plus')]:
            self.button(key,bx,555,w,46,label,icon=icon,enabled=key!='undo' or bool(self.game.history))
        self.box(x,619,444,80,p['panel'],17)
        mins,secs=divmod(int(self.game.elapsed),60)
        for i,label,value in [(0,'移动步数',f'{self.game.moves:,}'),(1,'游戏时长',f'{mins:02}:{secs:02}'),(2,'最大方块',f'{max(self.game.board):,}')]:
            xx=x+24+i*148
            self.text(label,xx,633,11,p['muted']);self.text(value,xx,653,25,p['text'],'number')
            if i<2:self.line((xx+114,639),(xx+114,679))

    def draw_achievements(self):
        p=self.p;x=666
        self.text('下一个小目标',x,724,12,p['muted'])
        target=next((v for v in [128,512,2048,8192,16384,32768,65536,131072] if v>max(self.game.board)),max(self.game.board)*2)
        self.text(f'{target:,}',x,746,33,p['gold'],'number')
        ratio=min(1,math.log2(max(self.game.board))/math.log2(target))
        self.box(x+111,768,157,4,p['line'],2);self.box(x+111,768,max(4,157*ratio),4,p['accent'],2)
        self.text(f'{len(self.known_achievements)} / 6 里程碑',x+111,741,12,p['muted'])
        self.button('records',x+304,741,140,44,'战绩',icon='trophy')

    def draw_modal(self):
        p=self.p
        overlay=pg.Surface((W*S,H*S),pg.SRCALPHA);overlay.fill((3,13,20,175));self.canvas.blit(overlay,(0,0))
        self.buttons=[]
        x,y,w,h=285,170,610,536
        if self.modal=='new':h=290;y=285
        self.box(x,y,w,h,p['panel'],24,p['line'])
        self.button('close',x+w-60,y+20,36,36,icon='close')
        if self.modal=='new':
            self.text('新的开始？',x+35,y+35,28)
            self.text('本局战绩会被记录，棋盘将重新开始。',x+35,y+105,16,p['muted'])
            self.button('cancel',x+35,y+195,253,50,'继续这一局')
            self.button('confirm_new',x+306,y+195,269,50,'开始新游戏',primary=True)
        elif self.modal=='help':
            self.text('留一点空间给灵感。',x+35,y+33,27)
            self.text('相同数字相遇，就会合并。2048 之后，还可以继续。',x+35,y+83,14,p['muted'])
            entries=[('方向键 / WASD','移动方块，也支持鼠标拖动 / 触控滑动'),('Space / 空格','开始或暂停自动驾驶'),('Z / H / Enter','撤销一步 / 查看 AI 提示 / AI 走一步'),('N / T / M','新一局 / 切换主题 / 开关音效'),('F / P / Esc','全屏 / 保存截图 / 关闭弹窗或暂停')]
            for i,(key,value) in enumerate(entries):
                yy=y+135+i*49
                self.text(key,x+35,yy,14,p['accent']);self.text(value,x+219,yy,13,p['muted'])
                if i<4:self.line((x+35,yy+32),(x+w-35,yy+32))
            self.button('motion',x+35,y+403,253,42,'动画：开启' if self.motion else '动画：关闭',selected=self.motion)
            self.button('step',x+306,y+403,269,42,'AI 走一步',icon='spark')
            self.text('自动保存进度 · 本次会话可撤销 100 步 · AI 分数单独标记',x+35,y+475,12,p['muted'])
        elif self.modal=='records':
            self.text('每一次，都算数。',x+35,y+33,27)
            self.text('本机战绩  /  最佳 7 局',x+35,y+85,13,p['muted'])
            rows=list(self.store.data['records'])
            current={'id':self.game.id,'score':self.game.score,'tile':max(self.game.board),'moves':self.game.moves,'ai':bool(self.game.ai_moves),'date':'进行中'}
            if self.game.moves:rows=[r for r in rows if r.get('id')!=self.game.id]+[current]
            rows=sorted(rows,key=lambda r:r.get('score',0),reverse=True)[:7]
            if not rows:self.text('第一段旅程，从现在开始。',x+w/2,y+260,18,p['muted'],anchor='center')
            for i,row in enumerate(rows):
                yy=y+133+i*47
                self.text(f'{i+1:02}',x+35,yy,17,p['muted'],'number')
                self.text(f"{row['score']:,}",x+85,yy-3,23,p['gold'] if i==0 else p['text'],'number')
                self.text(f"最大 {row['tile']:,}",x+245,yy+2,12,p['muted'])
                self.text('含 AI' if row.get('ai') else '手动',x+365,yy+2,12,p['accent'])
                self.text(row.get('date',''),x+w-35,yy+2,11,p['muted'],anchor='topright')
                self.line((x+35,yy+35),(x+w-35,yy+35))
            self.text('随机落子让每局不同。自动驾驶也有发挥与运气。',x+35,y+h-44,12,p['muted'])

    def screen_point(self,pos):
        sw,sh=self.screen.get_size();factor=min(sw/W,sh/H)
        return ((pos[0]-(sw-W*factor)/2)/factor,(pos[1]-(sh-H*factor)/2)/factor)

    def events(self):
        self.mouse=self.screen_point(pg.mouse.get_pos())
        keys={pg.K_LEFT:'left',pg.K_a:'left',pg.K_UP:'up',pg.K_w:'up',pg.K_RIGHT:'right',pg.K_d:'right',pg.K_DOWN:'down',pg.K_s:'down'}
        shortcuts={pg.K_SPACE:'auto',pg.K_z:'undo',pg.K_h:'hint',pg.K_RETURN:'step',pg.K_n:'new',pg.K_t:'theme',pg.K_m:'sound',pg.K_f:'full',pg.K_p:'export',pg.K_F1:'help'}
        for event in pg.event.get():
            if event.type==pg.QUIT:self.running=False
            elif event.type==pg.WINDOWFOCUSLOST:self.focused=False
            elif event.type==pg.WINDOWFOCUSGAINED:self.focused=True
            elif event.type==pg.KEYDOWN:
                if event.key==pg.K_ESCAPE:
                    if self.modal:self.modal=None
                    elif self.fullscreen:self.act('full')
                    else:self.stop_auto()
                elif not self.modal:
                    if event.key in keys:self.move(keys[event.key])
                    elif event.key in shortcuts:self.act(shortcuts[event.key])
            elif event.type==pg.MOUSEBUTTONDOWN and event.button==1:
                pos=self.screen_point(event.pos)
                hit=False
                for key,r,enabled in reversed(self.buttons):
                    if r.collidepoint(pos) and enabled:
                        if key=='step' and self.modal:self.modal=None
                        self.act(key);hit=True;break
                if not hit and not self.modal and pg.Rect(BX,BY,BS,BS).collidepoint(pos):self.swipe_start=pos
            elif event.type==pg.MOUSEBUTTONUP and event.button==1:
                if self.swipe_start:
                    pos=self.screen_point(event.pos);dx,dy=pos[0]-self.swipe_start[0],pos[1]-self.swipe_start[1]
                    if max(abs(dx),abs(dy))>25:self.move(('right' if dx>0 else 'left') if abs(dx)>abs(dy) else ('down' if dy>0 else 'up'))
                    self.swipe_start=None
            elif event.type==pg.FINGERDOWN:self.swipe_start=self.screen_point((event.x*self.screen.get_width(),event.y*self.screen.get_height()))
            elif event.type==pg.FINGERUP and self.swipe_start:
                pos=self.screen_point((event.x*self.screen.get_width(),event.y*self.screen.get_height()))
                dx,dy=pos[0]-self.swipe_start[0],pos[1]-self.swipe_start[1]
                if max(abs(dx),abs(dy))>25:self.move(('right' if dx>0 else 'left') if abs(dx)>abs(dy) else ('down' if dy>0 else 'up'))
                self.swipe_start=None

    def update(self,dt):
        now=time.monotonic()
        if self.played and not self.ended and not self.modal and (self.focused or self.auto):self.game.elapsed+=dt
        self.score_display+=(self.game.score-self.score_display)*(1-math.exp(-dt*14))
        if not self.motion or abs(self.score_display-self.game.score)<.5:self.score_display=float(self.game.score)
        for particle in self.particles:
            particle[0]+=particle[2]*dt;particle[1]+=particle[3]*dt;particle[3]+=80*dt;particle[4]-=dt
        self.particles=[p for p in self.particles if p[4]>0]
        try:
            while True:
                token,result=self.results.get_nowait()
                if isinstance(token,str) and token.startswith('rescue:'):
                    self.receive_rescue(token,result);continue
                if token==-1:
                    self.ai_ready=result.get('ready',False)
                    if 'error' in result:
                        self.ai_error=result['error'];self.auto=False;self.pending=None;self.toast(self.ai_error)
                    continue
                pending=self.pending
                if not pending or token!=pending[0]:continue
                self.pending=None
                if token!=self.token:continue
                if 'error' in result:self.auto=False;self.toast('AI 暂时不可用：'+result['error']);continue
                self.ai_result=result
                if not result.get('direction'):self.auto=False
                kind=pending[1]
                result['source']=kind
                if kind in ('auto','step') and result['direction'] and not self.modal:
                    self.queued_ai=(token,result,kind)
        except Empty:pass
        if self.pending and (not self.process.is_alive() or now-self.pending[2]>20):
            self.auto=False;self.pending=None;self.toast('AI 进程未响应，请重新打开游戏')
        if self.queued_ai:
            token,result,kind=self.queued_ai
            if token!=self.token or (kind=='auto' and not self.auto):self.queued_ai=None
            elif not self.animation and not self.modal and (kind=='step' or now>=self.next_auto):
                self.queued_ai=None
                self.move(result['direction'],True)
                result['applied']=True;self.ai_result=result
        prefetch=getattr(self,'ai_prefetch',False)
        if self.manual_request and not self.pending and not self.queued_ai and (prefetch or not self.animation) and (not self.modal or self.manual_request in ('hint','inspect')):
            kind=self.manual_request;self.manual_request=None;self.ask_ai(kind)
        if self.auto and not self.pending and not self.queued_ai and not self.modal and (prefetch or (not self.animation and now>=self.next_auto)):self.ask_ai('auto')
        if self.saver:
            for error in self.saver.poll():
                self.save_ok=error is None
                if error:self.toast(error)
        if now-self.last_save>5:self.save()

    def run(self):
        start=time.monotonic()
        try:
            while self.running:
                dt=min(.05,self.clock.tick(60)/1000)
                self.events();self.update(dt);self.draw()
                if self.args.screenshot and time.monotonic()-start>.6:
                    pg.image.save(self.canvas,self.args.screenshot);break
                if self.args.smoke_seconds and time.monotonic()-start>self.args.smoke_seconds:break
        finally:
            self.save();self.flush_save()
            self.requests.put(None)
            self.process.join(timeout=.8)
            if self.process.is_alive():self.process.terminate();self.process.join(timeout=1)
            pg.quit()


def main():
    parser=argparse.ArgumentParser(description='2048 Atelier — Python desktop game')
    parser.add_argument('--demo',action='store_true',help='Preview with a sample board, without touching your save')
    parser.add_argument('--screenshot',help='Render one frame to a PNG and exit')
    parser.add_argument('--smoke-seconds',type=float,default=0)
    args=parser.parse_args()
    Atelier(args).run()


if __name__=='__main__':
    mp.freeze_support()
    main()
