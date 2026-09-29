"""A focused, spatial 2048 interface: one board and two floating control islands."""
from __future__ import annotations
import argparse,math,multiprocessing as mp,time
from pathlib import Path
from collections import deque
from engine import slide
from features import Features
from journey import Journey
from adventures import Adventures
from typography import Face
import interface_base as controller
from motion import glide,effect,slide_time,FramePacer
import pygame as pg
import ui_core as core
from clear_material import environment,panel as clear_panel
from prism import soft_shadow,glass_light

W,H,S=1080,820,2
BX,BY,STEP,CELL=294,164,125,112
BS=STEP*3+CELL
LIGHT=dict(bg='#f1f3f8',panel='#fafbfd',board='#e9edf5',slot='#e5e9f2',line='#dde0e8',text='#272c36',muted='#697381',accent='#333e50',ink='#ffffff',soft='#e8ecf3',gold='#737d9c',shadow='#cfd3e1')
DARK=dict(bg='#242831',panel='#343a47',board='#2d3443',slot='#303745',line='#4a5060',text='#f0f2fa',muted='#a0a8bb',accent='#e7ebf5',ink='#303644',soft='#465065',gold='#b3b2d2',shadow='#171e2c')
TINTS={2:('#ffffff',.0,'#565d6c'),4:('#c9d7ff',.12,'#58627c'),8:('#bdccfa',.20,'#56637f'),16:('#acc6f5',.29,'#4c6287'),32:('#92b5e7',.39,'#405c80'),64:('#b1b0ef',.39,'#5c5988'),128:('#c7a9e4',.42,'#775d94'),256:('#e2aedb',.42,'#896481'),512:('#edb8c4',.47,'#986474'),1024:('#efc5a0',.49,'#926849'),2048:('#e8c182',.50,'#8b6942')}
TINTS.update({4096:('#9bd4c9',.47,'#416f66'),8192:('#9cc4eb',.52,'#496882'),16384:('#c0afe8',.52,'#6a588a'),32768:('#e0acca',.52,'#8a5774'),65536:('#e9cba0',.56,'#85653f')})

class Atelier(Adventures,Journey,Features,core.Atelier):
    ai_prefetch=True

    def __init__(self,args):
        self.surfaces={};self.shadows={};self.world={};self.tip=None
        super().__init__(args)
        if self.store.data.get('appearance_version')!=5:
            self.theme='light';self.store.data['appearance_version']=5
        self.toasts=[];self.tiles.clear();self.hover_values={}
        self.hover_glow=glass_light(CELL*S*2)
        self.hover_mask=pg.Surface((CELL*S,CELL*S),pg.SRCALPHA)
        pg.draw.rect(self.hover_mask,'white',self.hover_mask.get_rect(),border_radius=27*S)
        pg.display.set_caption('2048')
        self.input_queue=deque();self.effects={};self.ui_dt=1/120
        self.tile_builds=0;self.present_surface=None;self.modal_composite=None
        self.pressed=None;self.press_values={};self.pointer_id=None;self.button_context=None
        self.modal_progress=0.;self.modal_layer=pg.Surface((W*S,H*S),pg.SRCALPHA)
        self.modal_blurred=None;self.modal_render_key=None;self.modal_bounds=None
        self.hint_alpha=0.;self.tip_key=None;self.tip_since=0.;self.cursor_hand=False
        self.warm_tiles()
        self.warm_modal_text()
        self.warm_journey();self.warm_adventures()
        self.draw_lobby(time.monotonic());self.buttons=[]
        for message in (self.store.error,self.store.notice,self.game.restore_warning):
            if message:self.toast(message)
        if not args.demo:self.act('lobby')

    @property
    def p(self):return LIGHT if self.theme=='light' else DARK

    def font(self,size,kind='body'):
        key=(size,kind)
        if key not in self.fonts:
            self.fonts[key]=Face(size,kind)
        return self.fonts[key]

    def set_app_icon(self):
        icon=pg.Surface((128,128),pg.SRCALPHA)
        pg.draw.rect(icon,'#edf1f8',(0,0,128,128),border_radius=28)
        for i,c in enumerate(['#d9e2f5','#e5e5f4','#ccd9ef','#e4d5ec']):pg.draw.rect(icon,c,(22+i%2*46,22+i//2*46,39,39),border_radius=11)
        pg.display.set_icon(icon)

    def backdrop(self):
        if self.theme not in self.world:self.world[self.theme]=environment(W*S,H*S,self.theme=='dark')
        return self.world[self.theme]

    def float_panel(self,x,y,w,h,r=24,strength=.0,tint='#ffffff',shadow=True):
        key=(self.theme,x,y,w,h,r,strength,tint)
        if key not in self.surfaces:
            bg,_=self.backdrop()
            self.surfaces[key]=clear_panel(bg,round(x*S),round(y*S),round(w*S),round(h*S),r*S,tint,strength,self.theme=='dark')
        if shadow:
            skey=(w,h,r,self.theme)
            if skey not in self.shadows:self.shadows[skey]=soft_shadow(round(w*S),round(h*S),r*S,13*S,18 if self.theme=='light' else 46)
            sh,pad=self.shadows[skey];self.canvas.blit(sh,(round(x*S)-pad,round((y+8)*S)-pad))
        self.canvas.blit(self.surfaces[key],(round(x*S),round(y*S)))

    def button(self,key,x,y,w,h,label='',icon=None,primary=False,selected=False,enabled=True,small=False):
        rect=pg.Rect(x,y,w,h);hover=rect.collidepoint(self.mouse) and enabled and (self.modal in (None,'lobby') or getattr(self,'drawing_modal',False))
        t=self.hover_values.get(key,0)+(float(hover)-self.hover_values.get(key,0))*(1-math.exp(-self.ui_dt/.07));self.hover_values[key]=t
        if not self.motion:t=float(hover)
        pressed=bool(self.pressed and self.pressed[0]==key and hover)
        p=self.press_values.get(key,0)+(float(pressed)-self.press_values.get(key,0))*(1-math.exp(-self.ui_dt/.035))
        self.press_values[key]=p
        if not self.motion:p=float(pressed)
        x+=w*.017*p;y+=h*.017*p;w*=1-.034*p;h*=1-.034*p
        if primary:
            colour=core.mix(self.p['accent'],self.p['muted'],t*.08+p*.15)
            if not enabled:colour=core.mix(colour,self.p['bg'],.6)
            self.box(x,y,w,h,colour,h/2)
        elif selected or p>.01:self.box(x,y,w,h,core.mix(self.p['soft'],self.p['line'],p*.4),min(h/2,13))
        elif t>.01:self.box(x,y,w,h,core.mix(self.p['panel'],self.p['soft'],1-t*.7),h/2)
        fg=self.p['ink'] if primary else self.p['text'] if enabled else core.mix(self.p['muted'],self.p['bg'],.45)
        if icon and label:
            width=self.font(13 if small else 14,'body_medium').size(label)[0]/S
            left=x+(w-18-10-width)/2;self.icon(icon,left,y+(h-18)/2,fg,18)
            self.text(label,left+28,y+h/2,13 if small else 14,fg,'body_medium',anchor='midleft')
        elif icon:self.icon(icon,x+(w-18)/2,y+(h-18)/2,fg,18)
        elif label:self.text(label,x+w/2,y+h/2,13 if small else 14,fg,'body_medium',anchor='center')
        self.buttons.append((key,rect,enabled))
        labels={'undo':'撤销 · Z','redo':'重做 · ⇧Z','hint':'提示 · H','new':'新游戏 · N','settings':'设置','sound':'音效','theme':'切换外观 · T'}
        if hover and not label and key in labels:self.tip=(labels[key],x+w/2,y)

    def icon(self,name,x,y,color=None,size=20):
        if name!='redo':return super().icon(name,x,y,color,size)
        k=size/20
        for a,b in [((12,3),(17,8)),((17,8),(12,13)),((17,8),(7,8)),((7,8),(3,12)),((3,12),(3,17)),((3,17),(11,17))]:
            self.line((x+a[0]*k,y+a[1]*k),(x+b[0]*k,y+b[1]*k),color or self.p['text'],1.6)

    def cell_xy(self,i):return BX+(i%4)*STEP,BY+(i//4)*STEP

    def tile_surface(self,value):
        key=(self.theme,value)
        if key in self.tiles:return self.tiles[key]
        tint,strength,fg=TINTS.get(value,('#ccb6de',.5,'#685078'))
        if self.theme=='dark':fg=core.mix(fg,'#ffffff',.85)
        bg,_=self.backdrop();surface=pg.Surface(((CELL+48)*S,(CELL+48)*S),pg.SRCALPHA)
        skey=('tile',self.theme)
        if skey not in self.shadows:self.shadows[skey]=soft_shadow(CELL*S,CELL*S,27*S,9*S,18 if self.theme=='light' else 52)
        sh,pad=self.shadows[skey];surface.blit(sh,(24*S-pad,30*S-pad))
        # One continuous material travels with each tile. Crossing cell boundaries
        # must never rebuild its texture or change its tint mid-flight.
        face=clear_panel(bg,round((BX+(BS-CELL)/2)*S),round((BY+(BS-CELL)/2)*S),CELL*S,CELL*S,27*S,tint,strength,self.theme=='dark')
        surface.blit(face,(24*S,24*S))
        size=43 if value<100 else 35 if value<1000 else 29
        word=self.font(size,'number').render(str(value),True,fg)
        while word.get_width()>CELL*S*.82 and size>12:
            size-=1;word=self.font(size,'number').render(str(value),True,fg)
        surface.blit(word,word.get_rect(center=(80*S,80*S)))
        self.tiles[key]=surface;self.tile_builds+=1
        return surface

    def warm_tiles(self):
        for power in range(1,31):self.tile_surface(1<<power)
        for h in (570,510,254):
            skey=('sheet',600,h,self.theme)
            if skey not in self.shadows:self.shadows[skey]=soft_shadow(600*S,h*S,28*S,14*S,30 if self.theme=='light' else 75)
            facekey=('sheetface',h,self.theme)
            if facekey not in self.surfaces:
                bg,_=self.backdrop()
                self.surfaces[facekey]=clear_panel(bg,round((W-600)/2*S),round((H-h)/2*S),600*S,h*S,28*S,'#ffffff',.035,self.theme=='dark')

    def tile(self,value,x,y,scale=1,flash=0,opacity=1):
        if not value or opacity<=0:return
        surf=self.tile_surface(value)
        if abs(scale-1)>.001:surf=pg.transform.smoothscale(surf,(max(1,round(surf.get_width()*scale)),max(1,round(surf.get_height()*scale))))
        if opacity<.999:surf=surf.copy();surf.set_alpha(round(opacity*255))
        self.canvas.blit(surf,surf.get_rect(center=(round((x+CELL/2)*S),round((y+CELL/2)*S))))
        if flash>0:
            overlay=pg.Surface((CELL*S,CELL*S),pg.SRCALPHA)
            pg.draw.rect(overlay,(255,255,255,int(flash*32)),overlay.get_rect(),border_radius=27*S)
            self.canvas.blit(overlay,(round(x*S),round(y*S)))
        if self.motion and not self.animation and not self.modal and not self.auto and pg.Rect(x,y,CELL,CELL).collidepoint(self.mouse):
            light=pg.Surface((CELL*S,CELL*S),pg.SRCALPHA)
            light.blit(self.hover_glow,((self.mouse[0]-x-CELL)*S,(self.mouse[1]-y-CELL)*S))
            light.blit(self.hover_mask,(0,0),special_flags=pg.BLEND_RGBA_MULT)
            self.canvas.blit(light,(round(x*S),round(y*S)))

    def warm_modal_text(self):
        previous=self.modal;buttons=self.buttons;bounds=self.modal_bounds
        # Populate font glyphs and labels before the first opening transition.
        try:
            for modal in ('settings','help','intelligence','records','new','modes','replay','levels'):
                self.modal=modal;self._modal_face=None
                super().draw_modal()
        finally:self.modal=previous;self.buttons=buttons;self.modal_bounds=bounds;self._modal_face=None

    def tile_effect(self,index,now,source=None):
        item=(self.effects if source is None else source).get(index)
        return effect(item[0],now-item[1]) if item else (1.,1.,0.)

    def finish_slide(self,now):
        anim=self.animation
        if not anim or now<anim['start']+anim['duration']:return
        arrival=anim['start']+anim['duration'];following={}
        for tr in anim['tracks']:
            if tr.target not in anim['merges'] and tr.source in anim['effects']:
                following[tr.target]=anim['effects'][tr.source]
        for i in anim['merges']:following[i]=('merge',arrival)
        if anim['spawn'] is not None:following[anim['spawn']]=('spawn',arrival)
        self.effects=following;self.animation=None

    def move(self,direction,by_ai=False):
        if self.modal or self.ended:return
        if not by_ai:
            self.stop_auto()
            if self.animation:
                if len(self.input_queue)<4:self.input_queue.append(direction)
                self.buffered_direction=self.input_queue[0] if self.input_queue else None
                return
        previous=dict(self.effects)
        super().move(direction,by_ai)
        if self.animation:
            self.animation['duration']=slide_time(self.animation['tracks'],self.auto and self.speed==2)
            self.animation['effects']=previous
        else:self.effects.clear()
        self.next_auto=time.monotonic()+[.75,.25,.15,0][self.speed]

    def update(self,dt):
        self.ui_dt=max(.001,min(.05,dt));now=time.monotonic()
        target=float(bool(self.modal))
        self.modal_progress=max(0.,min(1.,self.modal_progress+(1 if target else -1)*self.ui_dt/.18)) if self.motion else target
        self.finish_slide(now)
        self.effects={i:e for i,e in self.effects.items() if now-e[1]<.20}
        # Retire the input lock as soon as tiles arrive. Settling is purely visual.
        controller.Atelier.update(self,dt)
        self.update_features(dt)
        while self.input_queue and not self.animation and not self.modal and not self.ended:
            direction=self.input_queue.popleft()
            self.buffered_direction=self.input_queue[0] if self.input_queue else None
            self.move(direction)

    def new_game(self):
        super().new_game();self.input_queue.clear();self.effects.clear()
        self.last_gain=None
        if not self.motion:self.modal_progress=0.

    def cancel_input(self):
        self.input_queue.clear();self.buffered_direction=None;self.swipe_start=None
        self.pressed=None;self.pointer_id=None

    def act(self,key):
        old_modal=self.modal
        if key in ('auto','undo','redo','new','confirm_new','settings','intelligence','help','records','motion','step','hint','close','cancel','resume_auto','inspect_hint','modes','replay','mode_daily','mode_classic'):
            self.cancel_input()
        if key=='theme':
            self.theme='dark' if self.theme=='light' else 'light';self.warm_tiles();self.warm_modal_text();self.warm_journey();self.warm_adventures();self.save();return
        super().act(key)
        if key in ('undo','redo','motion'):self.effects.clear()
        if self.modal!=old_modal:
            self.modal_render_key=None
            if self.modal and not old_modal:self.modal_progress=0. if self.motion else 1.
        if not self.motion:self.modal_progress=float(bool(self.modal))

    def draw_board(self,now):
        for i in range(16):
            x,y=self.cell_xy(i)
            self.box(x,y,CELL,CELL,core.mix(self.p['slot'],self.p['bg'],.6),27)
        anim=self.animation
        if anim:
            u=glide((now-anim['start'])/anim['duration'])
            for tr in anim['tracks']:
                x,y=self.cell_xy(tr.source);tx,ty=self.cell_xy(tr.target)
                scale,alpha,flash=self.tile_effect(tr.source,now,anim['effects'])
                self.tile(tr.value,x+(tx-x)*u,y+(ty-y)*u,scale,flash,alpha)
        else:
            for i,v in enumerate(self.game.board):
                scale,alpha,flash=self.tile_effect(i,now)
                self.tile(v,*self.cell_xy(i),scale,flash,alpha)
        if self.game.mode=='expedition' and self.game.extra['freeze'] and not self.modal:
            color=self.p['gold']
            for xx,yy,dx,dy in ((BX-8,BY-8,1,1),(BX+BS+8,BY-8,-1,1),(BX-8,BY+BS+8,1,-1),(BX+BS+8,BY+BS+8,-1,-1)):
                self.line((xx,yy+dy*18),(xx,yy),color,1.3);self.line((xx,yy),(xx+dx*18,yy),color,1.3)
        if self.ended and not self.animation:
            if self.game.mode in ('puzzle','sprint','expedition','rescue'):
                self.draw_episode_end();return
            self.float_panel(BX-3,BY+149,494,187,30,shadow=True)
            self.text('本局结束',540,BY+191,26,anchor='center')
            self.text(f'{self.game.score:,} 分',540,BY+231,16,self.p['muted'],anchor='center')
            if self.game.history:
                self.button('undo',372,BY+265,158,46,'撤销最后一步',selected=True)
                self.button('new',546,BY+265,158,46,'再来一局',primary=True)
            else:self.button('new',450,BY+265,180,46,'再来一局',primary=True)
            self.draw_rescue_prompt()

    def draw_chrome(self,now):
        p=self.p
        self.text('2048',70,57,30,p['text'],'display')
        mode='每日 · '+self.game.challenge_date[5:].replace('-','.') if self.game.mode=='daily' else {'classic':'经典 · 自由练习','puzzle':'解局剧场','sprint':'60 步冲刺','expedition':'能力远征','rescue':'绝境重生'}[self.game.mode]
        self.button('modes',64,102,192,30,mode+'  /  大厅',small=True)
        self.float_panel(752,55,252,48,24,shadow=False)
        self.button('replay',758,59,80,40,'复盘',enabled=bool(self.game.history),small=True)
        self.button('coach',848,59,88,40,'教练 开' if self.coach else '教练',selected=self.coach,small=True)
        self.line((947,68),(947,90),p['line'])
        self.button('settings',955,59,40,40,icon='settings')
        self.float_panel(405,49,275,68,34)
        self.text('得分',443,65,10,p['muted']);self.text(f'{round(self.score_display):,}',441,84,21,p['text'],'number')
        self.line((543,69),(543,98),core.mix(p['line'],p['panel'],.3))
        if self.game.mode=='puzzle':label,value='已用步数',self.game.moves
        elif self.game.mode=='sprint':label,value='剩余步数',max(0,60-self.game.moves)
        elif self.game.mode=='expedition':label,value='关卡',str(self.game.extra['stage']+1)+' / 6'
        elif self.game.mode=='rescue':label,value='剩余步数',max(0,self.game.extra['limit']-self.game.moves)
        else:label,value='最佳',self.store.data['best']
        self.text(label,568,65,10,p['muted']);self.text(f'{value:,}' if isinstance(value,int) else value,566,84,21,p['text'],'number')
        self.float_panel(322,699,438,62,31)
        self.button('undo',331,709,44,42,icon='undo',enabled=bool(self.game.history))
        self.button('redo',377,709,44,42,icon='redo',enabled=bool(self.game.future))
        self.button('hint',425,709,44,42,icon='spark',enabled=not self.ended)
        self.button('auto',480,708,174,44,'暂停' if self.auto else '演示解法' if self.game.mode in ('puzzle','rescue') else '自动玩',icon='pause' if self.auto else 'play',primary=True,enabled=not self.ended)
        self.button('new',676,709,66,42,icon='plus')
        status=self.status_text()
        if status and status.startswith('建议'):status='方向键执行 · Enter 让 AI 走一步'
        self.text(status or '方向键移动 · 空格自动玩',540,787,11,p['muted'],anchor='center')
        mins,secs=divmod(int(self.game.elapsed),60)
        self.text(f'{self.game.moves:,} 步 · {mins:02}:{secs:02}',72,787,11,p['muted'],anchor='midleft')
        self.text('示例棋盘' if self.args.demo else '进度自动保存' if self.save_ok else '保存失败 · 请检查磁盘',1000,787,11,p['muted'] if self.save_ok else p['gold'],anchor='midright')
        if self.last_gain and self.motion:
            gain,stamp=self.last_gain;age=now-stamp
            if age<.7:self.text(f'+{gain:,}',514,123-age*10,11,p['gold'],'number',anchor='topright',alpha=round((1-age/.7)*255))

    def draw(self):
        now=time.monotonic();self.buttons=[];self.tip=None;self.modal_composite=None
        key=(self.modal,self.theme,tuple(self.game.board))
        if self.modal=='lobby':
            _,background=self.backdrop();self.canvas.blit(background,(0,0));self.draw_lobby(now)
        elif self.modal and self.modal_render_key==key:
            self.canvas.blit(self.modal_scene,(0,0))
        else:
            _,background=self.backdrop();self.canvas.blit(background,(0,0))
            self.draw_board(now);self.draw_chrome(now);self.draw_journey_sides(now)
        if self.modal!='lobby' and (self.modal or self.modal_progress>0):self.draw_modal()
        self.toasts=[t for t in self.toasts if now-t[1]<2.5]
        if self.toasts and not self.modal:
            self.float_panel(375,652,330,30,15,shadow=False)
            self.text(self.toasts[-1][0],540,667,11,anchor='center')
        tip_key=self.tip[0] if self.tip else None
        if tip_key!=self.tip_key:self.tip_key=tip_key;self.tip_since=now
        if self.tip and not self.modal and now-self.tip_since>.38 and not self.pressed:
            label,x,y=self.tip;self.panel(x-57,y-33,114,27,13,self.p['panel'])
            self.text(label,x,y-19,10,self.p['muted'],anchor='center')
        if not self.modal and self.modal_progress==0 and not self.toasts:self.draw_hint(now)
        self.button_context=self.modal
        hand=any(enabled and r.collidepoint(self.mouse) for _,r,enabled in self.buttons)
        if hand!=self.cursor_hand:
            try:pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND if hand else pg.SYSTEM_CURSOR_ARROW)
            except pg.error:pass
            self.cursor_hand=hand
        sw,sh=self.screen.get_size();self.factor=min(sw/W,sh/H)
        dw,dh=round(W*self.factor),round(H*self.factor);self.offset=((sw-dw)//2,(sh-dh)//2)
        if self.present_surface is None or self.present_surface.get_size()!=(dw,dh):
            self.present_surface=pg.Surface((dw,dh)).convert()
        pg.transform.smoothscale(self.canvas,(dw,dh),self.present_surface)
        if self.modal_composite:
            p,crop,bounds=self.modal_composite
            if self.modal_base_output is None or self.modal_base_output.get_size()!=(dw,dh):
                self.modal_base_output=pg.transform.smoothscale(self.modal_base,(dw,dh))
            self.modal_base_output.set_alpha(round(p*255) if p<.999 else None)
            self.present_surface.blit(self.modal_base_output,(0,0))
            scale=(.97+.03*p)*self.factor/S
            overlay=pg.transform.smoothscale(crop,(max(1,round(crop.get_width()*scale)),max(1,round(crop.get_height()*scale))))
            overlay.set_alpha(round(p*255))
            center=(round(bounds.centerx*self.factor/S),round((bounds.centery+12*S*(1-p))*self.factor/S))
            self.present_surface.blit(overlay,overlay.get_rect(center=center))
        self.screen.fill(self.p['bg']);self.screen.blit(self.present_surface,self.offset)
        present_start=time.perf_counter();pg.display.flip();self.present_wait=time.perf_counter()-present_start

    def capture_surface(self):
        if self.present_surface is None:self.draw()
        if self.modal_composite:
            p,crop,bounds=self.modal_composite;capture=self.canvas.copy()
            base=pg.transform.smoothscale(self.modal_base,(W*S,H*S));base.set_alpha(round(p*255));capture.blit(base,(0,0))
            scale=.97+.03*p
            overlay=pg.transform.smoothscale(crop,(round(crop.get_width()*scale),round(crop.get_height()*scale)))
            overlay.set_alpha(round(p*255))
            capture.blit(overlay,overlay.get_rect(center=(bounds.centerx,bounds.centery+round(12*S*(1-p)))))
            return capture
        return self.canvas

    def draw_hint(self,now):
        if self.game.mode in ('expedition','rescue'):return self.draw_adventure_hint(now)
        result=self.ai_result
        if result and result.get('backend')=='exact' and not result.get('solvable') and not self.ended and not self.animation:
            self.float_panel(302,655,476,36,18,shadow=False)
            self.text('这条路在余下步数内无解 · 可以撤销或重试',540,673,11,self.p['muted'],anchor='center');return
        visible=bool(result and result.get('direction') and not result.get('applied') and not self.auto and not self.animation and not self.ended)
        self.hint_alpha+=(float(visible)-self.hint_alpha)*(1-math.exp(-self.ui_dt/.065))
        if not visible:return
        direction=result['direction'];_,gain,_,merges=slide(self.game.board,direction)
        self.float_panel(302,655,476,36,18,shadow=False)
        self.icon(direction,316,665,self.p['text'],16)
        name={'left':'向左','up':'向上','right':'向右','down':'向下'}[direction]
        detail=f'可合并 {len(merges)} 组 · +{gain:,}' if merges else '整理局面'
        self.text(f'{name}  ·  {detail}',345,657,11,self.p['text'],alpha=round(255*self.hint_alpha))
        self.text(result.get('explanation','相同数字相遇就会合并。'),345,675,9,self.p['muted'],alpha=round(255*self.hint_alpha))
        if merges:
            outline=pg.Surface((CELL*S,CELL*S),pg.SRCALPHA)
            pg.draw.rect(outline,(*pg.Color(self.p['gold'])[:3],round(90*self.hint_alpha)),outline.get_rect().inflate(-4*S,-4*S),width=S,border_radius=25*S)
            for i in merges:
                x,y=self.cell_xy(i);self.canvas.blit(outline,(x*S,y*S))

    def modal_veil(self):
        # The root view composites the dimming and blur once for the whole sheet.
        pass

    def draw_modal(self):
        scene=self.canvas
        if self.modal:
            key=(self.modal,self.theme,tuple(self.game.board))
            if self.modal_render_key!=key:
                self.modal_scene=scene.copy()
                small=pg.transform.smoothscale(scene,(W//40,H//40))
                self.modal_blurred=small
                self.modal_base=small.copy()
                dim=pg.Surface(small.get_size(),pg.SRCALPHA)
                dim.fill((8,13,24,38 if self.theme=='light' else 80));self.modal_base.blit(dim,(0,0))
                self.modal_base=self.modal_base.convert();self.modal_base_output=None
                self.modal_render_key=key;self._modal_face=None
            self.modal_layer.fill((0,0,0,0));self.canvas=self.modal_layer;self.drawing_modal=True
            try:super().draw_modal()
            finally:self.canvas=scene;self.drawing_modal=False
        else:self.buttons=[]
        if self.modal_blurred is None or self.modal_bounds is None:return
        p=glide(self.modal_progress) if self.motion else float(bool(self.modal))
        crop=self.modal_layer.subsurface(self.modal_bounds)
        # Composite at the window's actual pixel size. Text is still drawn at 2×,
        # but a soft overlay need not blend four times as many display pixels.
        self.modal_composite=(p,crop,self.modal_bounds)
        if self.modal_progress<.94:self.buttons=[]

    def panel(self,x,y,w,h,radius=18,fill=None,border=False):
        if self.modal and fill is None and w==600:
            self.modal_bounds=pg.Rect(round((x-40)*S),round((y-40)*S),round((w+80)*S),round((h+80)*S))
            if self._modal_face is None:
                self._modal_face=self.surfaces[('sheetface',h,self.theme)]
            skey=('sheet',w,h,self.theme)
            if skey not in self.shadows:self.shadows[skey]=soft_shadow(round(w*S),round(h*S),28*S,14*S,30 if self.theme=='light' else 75)
            shadow,pad=self.shadows[skey];self.canvas.blit(shadow,(round(x*S)-pad,round((y+12)*S)-pad))
            self.canvas.blit(self._modal_face,(round(x*S),round(y*S)));return
        super().panel(x,y,w,h,radius,fill,border)

    def pointer_down(self,pos,pointer='mouse'):
        if self.pointer_id is not None or self.button_context!=self.modal:return
        if self.modal_progress>0 and not self.modal:return
        self.pointer_id=pointer;self.mouse=pos
        for key,r,enabled in reversed(self.buttons):
            if enabled and r.collidepoint(pos):self.pressed=(key,r.copy(),self.modal);return
        if not self.modal and pg.Rect(BX,BY,BS,BS).collidepoint(pos):self.swipe_start=pos

    def pointer_up(self,pos,pointer='mouse'):
        if pointer!=self.pointer_id:return
        pressed=self.pressed;start=self.swipe_start;self.pressed=None;self.swipe_start=None;self.pointer_id=None;self.mouse=pos
        if pressed:
            key,bounds,context=pressed
            if context==self.modal and bounds.collidepoint(pos) and any(k==key and enabled for k,_,enabled in self.buttons):self.act(key)
        elif start and not self.modal:
            dx,dy=pos[0]-start[0],pos[1]-start[1]
            if max(abs(dx),abs(dy))>25:self.move(('right' if dx>0 else 'left') if abs(dx)>abs(dy) else ('down' if dy>0 else 'up'))

    def events(self):
        self.mouse=self.screen_point(pg.mouse.get_pos())
        keys={pg.K_LEFT:'left',pg.K_a:'left',pg.K_UP:'up',pg.K_w:'up',pg.K_RIGHT:'right',pg.K_d:'right',pg.K_DOWN:'down',pg.K_s:'down'}
        shortcuts={pg.K_SPACE:'auto',pg.K_z:'undo',pg.K_y:'redo',pg.K_h:'hint',pg.K_RETURN:'step',pg.K_n:'new',pg.K_t:'theme',pg.K_m:'sound',pg.K_f:'full',pg.K_p:'export',pg.K_F1:'help',pg.K_c:'coach',pg.K_r:'replay',pg.K_b:'lobby'}
        for e in pg.event.get():
            if e.type==pg.QUIT:self.running=False
            elif e.type==pg.WINDOWFOCUSLOST:self.focused=False;self.cancel_input()
            elif e.type==pg.WINDOWFOCUSGAINED:self.focused=True
            elif e.type==pg.WINDOWRESIZED and not self.fullscreen:self.windowed_size=self.screen.get_size()
            elif e.type==pg.KEYDOWN:
                if e.key==pg.K_ESCAPE:
                    self.cancel_input()
                    if self.modal:self.act('close')
                    elif self.fullscreen:self.act('full')
                    else:self.stop_auto()
                elif self.modal=='replay' and e.key in (pg.K_LEFT,pg.K_RIGHT,pg.K_HOME,pg.K_END,pg.K_SPACE):
                    self.act({pg.K_LEFT:'replay_prev',pg.K_RIGHT:'replay_next',pg.K_HOME:'replay_first',pg.K_END:'replay_last',pg.K_SPACE:'replay_play'}[e.key])
                elif not self.modal and self.modal_progress==0:
                    if e.key in keys:self.move(keys[e.key])
                    elif e.key==pg.K_z and getattr(e,'mod',0)&pg.KMOD_SHIFT:self.act('redo')
                    elif e.key in shortcuts:self.act(shortcuts[e.key])
            elif e.type==pg.MOUSEBUTTONDOWN and e.button==1 and not getattr(e,'touch',False):self.pointer_down(self.screen_point(e.pos))
            elif e.type==pg.MOUSEBUTTONUP and e.button==1 and not getattr(e,'touch',False):self.pointer_up(self.screen_point(e.pos))
            elif e.type==pg.FINGERDOWN:
                pos=self.screen_point((e.x*self.screen.get_width(),e.y*self.screen.get_height()))
                self.pointer_down(pos,('touch',e.finger_id))
            elif e.type==pg.FINGERUP:
                self.pointer_up(self.screen_point((e.x*self.screen.get_width(),e.y*self.screen.get_height())),('touch',e.finger_id))

    def run(self):
        refresh=pg.display.get_current_refresh_rate() or 120
        pacer=FramePacer(refresh);start=time.monotonic();last_refresh=start
        try:
            while self.running:
                # Trust native pacing while it actually blocks; otherwise cap
                # rendering to the display rate without stacking two timers.
                dt=pacer.tick(wait=not pg.display.is_vsync() or pacer.fallback)
                frame_start=time.perf_counter();self.events();self.update(dt);self.draw()
                pacer.observe(time.perf_counter()-frame_start,self.present_wait)
                now=time.monotonic()
                if now-last_refresh>1:
                    pacer.set_rate(pg.display.get_current_refresh_rate() or 120);last_refresh=now
                if self.args.screenshot and now-start>.6:
                    pg.image.save(self.capture_surface(),self.args.screenshot);break
                if self.args.smoke_seconds and now-start>self.args.smoke_seconds:break
        finally:
            self.save();self.flush_save();self.requests.put(None);self.process.join(timeout=.8)
            if self.process.is_alive():self.process.terminate();self.process.join(timeout=1)
            pg.quit()


def main():
    parser=argparse.ArgumentParser(description='2048')
    parser.add_argument('--demo',action='store_true');parser.add_argument('--screenshot');parser.add_argument('--smoke-seconds',type=float,default=0)
    Atelier(parser.parse_args()).run()
if __name__=='__main__':mp.freeze_support();main()
