"""2048 — a quiet, tactile board game. Python renderer and native search."""
from __future__ import annotations
import argparse,math,multiprocessing as mp,os,time
from pathlib import Path
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame as pg
import interface_base as base
from prism import glass,soft_shadow,glass_light

W,H,S=1080,820,2
BX,BY,BS,GAP,PAD=64,160,544,12,16
CELL=(BS-2*PAD-3*GAP)/4
for name in ('W','H','S','BX','BY','BS','GAP','PAD','CELL'):setattr(base,name,globals()[name])
ROOT=Path(__file__).resolve().parent
DARK=dict(bg='#111318',panel='#1c1f26',board='#171a21',slot='#1d2028',line='#2b2e36',text='#eff0f4',muted='#858992',accent='#e6e7ed',ink='#24262e',soft='#2a2e37',gold='#d2b38c',shadow='#0c0e13')
LIGHT=dict(bg='#f1f2f5',panel='#fcfcfd',board='#e5e7ed',slot='#dce0e7',line='#d1d5de',text='#272b36',muted='#777e8e',accent='#323a4b',ink='#f7f8fb',soft='#e3e6ec',gold='#9b7750',shadow='#d6dbe5')
COLORS={2:'#3b4453',4:'#435a74',8:'#42717c',16:'#5f7c84',32:'#647c9d',64:'#827ba5',128:'#a283a2',256:'#b58897',512:'#c8977d',1024:'#d6b486',2048:'#e7d1a5',4096:'#bcb9cd',8192:'#96b7c9',16384:'#a3bec3',32768:'#d5b592'}
R=base.rect
mix=base.blend


class Atelier(base.Atelier):
    def __init__(self,args):
        super().__init__(args)
        pg.display.set_caption('2048')
        # Apply the new default once; subsequent appearance choices persist.
        self.materials={};self.hover_values={};self.buffered_direction=None
        self.tile_shadows={}
        self._cached_background={}
        size=round(CELL*S)
        self.hover_light=glass_light(size*2)
        self.tile_mask=pg.Surface((size,size),pg.SRCALPHA)
        pg.draw.rect(self.tile_mask,(255,255,255,255),self.tile_mask.get_rect(),border_radius=16*S)
        self.toasts=[]
        if args.demo:
            self.game.board=[0,2,4,0,2,8,16,4,4,32,64,8,8,128,512,1024]
            self.game.score=12384;self.game.moves=384;self.game.elapsed=521
            self.score_display=12384;self.store.data['best']=491144
            self.ai_result=None;self.known_achievements={128,512}
        self.set_app_icon()

    @property
    def p(self):return LIGHT if self.theme=='light' else DARK

    def font(self,size,kind='body'):
        key=(size,kind)
        if key not in self.fonts:
            candidates={
                'body':['/System/Library/Fonts/Hiragino Sans GB.ttc','C:/Windows/Fonts/msyh.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'],
                'latin':['/System/Library/Fonts/HelveticaNeue.ttc','C:/Windows/Fonts/segoeui.ttf'],
                'number':['/System/Library/Fonts/HelveticaNeue.ttc','C:/Windows/Fonts/segoeui.ttf'],
                'display':['/System/Library/Fonts/HelveticaNeue.ttc','C:/Windows/Fonts/segoeui.ttf'],
            }.get(kind,[])
            path=next((p for p in candidates if Path(p).exists()),None)
            self.fonts[key]=pg.font.Font(path,round(size*S))
        return self.fonts[key]

    def set_app_icon(self):
        icon=pg.Surface((128,128),pg.SRCALPHA)
        pg.draw.rect(icon,'#151820',(0,0,128,128),border_radius=28)
        icon.blit(glass(102,'#827ba5',22),(13,13))
        word=self.font(18,'number').render('2048',True,'#f9f5fd')
        icon.blit(word,word.get_rect(center=(64,64)));pg.display.set_icon(icon)

    def panel(self,x,y,w,h,radius=18,fill=None,border=False):
        self.box(x,y,w,h,fill or self.p['panel'],radius,self.p['line'] if border else None)

    def button(self,key,x,y,w,h,label='',icon=None,primary=False,selected=False,enabled=True,small=False):
        r=pg.Rect(x,y,w,h);hover=r.collidepoint(self.mouse) and enabled
        t=self.hover_values.get(key,0.)+(float(hover)-self.hover_values.get(key,0.))*.22
        self.hover_values[key]=t
        bg=None
        if primary:
            bg=mix(self.p['accent'],'#ffffff',t*.2)
            if not enabled:bg=mix(bg,self.p['bg'],.7)
        elif selected:bg=mix(self.p['soft'],self.p['text'],t*.04)
        elif t>.02:bg=mix(self.p['panel'],self.p['soft'],t)
        if bg:self.panel(x,y,w,h,12,bg)
        fg=self.p['ink'] if primary else self.p['text'] if enabled else mix(self.p['muted'],self.p['bg'],.46)
        if icon and label:
            label_width=self.font(13 if small else 14,'body').size(label)[0]/S
            total=18+10+label_width;left=x+(w-total)/2
            self.icon(icon,left,y+(h-18)/2,fg,18)
            self.text(label,left+28,y+h/2,13 if small else 14,fg,anchor='midleft')
        elif icon:self.icon(icon,x+(w-18)/2,y+(h-18)/2,fg,18)
        elif label:self.text(label,x+w/2,y+h/2,13 if small else 14,fg,anchor='center')
        self.buttons.append((key,r,enabled))

    def icon(self,name,x,y,color=None,size=20):
        if name in ('settings','more'):
            color=color or self.p['text']
            if name=='more':
                for i in range(3):self.circle(x+3+i*6,y+10,1.6,color)
            else:
                for i in range(3):
                    yy=y+4+i*6;xx=x+(6 if i%2==0 else 13)
                    self.line((x+1,yy),(x+19,yy),color,1.3)
                    self.box(xx-2,yy-2.5,4,5,color,1)
        else:super().icon(name,x,y,color,size)

    def background(self):
        if self.theme not in self._cached_background:
            bg=pg.Surface((W*S,H*S)).convert();bg.fill(self.p['bg'])
            self._cached_background[self.theme]=bg
        return self._cached_background[self.theme]

    def board_base(self):
        key=('board',self.theme)
        if key not in self.materials:
            board=pg.Surface((BS*S,BS*S),pg.SRCALPHA)
            pg.draw.rect(board,self.p['board'],board.get_rect(),border_radius=26*S)
            pg.draw.rect(board,self.p['line'],board.get_rect(),S,border_radius=26*S)
            for i in range(16):
                x=PAD+(i%4)*(CELL+GAP);y=PAD+(i//4)*(CELL+GAP)
                pg.draw.rect(board,self.p['slot'],R(x,y,CELL,CELL),border_radius=16*S)
                pg.draw.rect(board,mix(self.p['slot'],self.p['line'],.20),R(x,y,CELL,CELL),S,border_radius=16*S)
            self.materials[key]=board
            self.tile_shadows[key]=soft_shadow(BS*S,BS*S,26*S,16*S,60 if self.theme=='dark' else 18)
        return self.materials[key]

    def tile(self,value,x,y,scale=1,flash=0):
        if not value:return
        key=(value,self.theme)
        if key not in self.tiles:
            face=COLORS.get(value,'#c0a7c5');fg='#f5f6fb' if value<512 else '#382f32'
            size=round(CELL*S)
            tile=pg.Surface((size+16*S,size+16*S),pg.SRCALPHA)
            sh,pad=soft_shadow(size,size,16*S,3*S,60 if self.theme=='dark' else 32)
            tile.blit(sh,(8*S-pad,11*S-pad))
            tile.blit(glass(size,face,16*S,self.theme=='light'),(8*S,8*S))
            fs=49 if value<100 else 43 if value<1000 else 35 if value<10000 else 29
            word=self.font(fs,'number').render(str(value),True,fg)
            while word.get_width()>CELL*S*.83 and fs>12:
                fs-=1;word=self.font(fs,'number').render(str(value),True,fg)
            tile.blit(word,word.get_rect(center=(round((8+CELL/2)*S),round((8+CELL/2)*S))))
            self.tiles[key]=tile
        tile=self.tiles[key]
        if abs(scale-1)>.001:tile=pg.transform.smoothscale(tile,(max(1,round(tile.get_width()*scale)),max(1,round(tile.get_height()*scale))))
        self.canvas.blit(tile,tile.get_rect(center=(round((x+CELL/2)*S),round((y+CELL/2)*S))))
        if self.motion and not self.auto and not self.modal and not self.animation and pg.Rect(x,y,CELL,CELL).collidepoint(self.mouse):
            light=pg.Surface(self.tile_mask.get_size(),pg.SRCALPHA)
            light.blit(self.hover_light,((self.mouse[0]-x-CELL)*S,(self.mouse[1]-y-CELL)*S))
            light.blit(self.tile_mask,(0,0),special_flags=pg.BLEND_RGBA_MULT)
            self.canvas.blit(light,(round(x*S),round(y*S)))
        if flash>0:
            overlay=pg.Surface((round(CELL*S),round(CELL*S)),pg.SRCALPHA)
            pg.draw.rect(overlay,(245,240,255,round(flash*38)),overlay.get_rect(),border_radius=16*S)
            self.canvas.blit(overlay,(round(x*S),round(y*S)))

    def draw_header(self,now):
        p=self.p
        self.text('2048',BX,44,39,p['text'],'display')
        self.line((BX+115,55),(BX+115,83),p['line'])
        self.text('经典',BX+135,68,12,p['muted'],anchor='midleft')
        self.button('sound',W-203,48,40,40,icon='sound')
        self.button('theme',W-148,48,40,40,icon='sun')
        self.button('settings',W-93,48,40,40,icon='settings')
        self.line((BX,113),(W-BX,113))
        self.circle(BX+5,137,2.5,p['gold'])
        self.text('经典模式',BX+18,137,11,p['muted'],anchor='midleft')
        self.text('4 × 4',BX+BS-2,137,11,p['muted'],'latin',anchor='midright')
        x=676;right=W-BX
        self.text('本局得分',x,175,12,p['muted'])
        value=round(self.score_display)
        self.text(f'{value:,}',x-2,203,57 if value<1000000 else 48,p['text'],'number')
        self.icon('trophy',x,287,p['muted'],14)
        self.text('最佳',x+27,293,12,p['muted'],anchor='midleft')
        self.text(f"{self.store.data['best']:,}",right,293,17,p['text'],'number',anchor='midright')
        self.line((x,329),(right,329))
        if self.last_gain and self.motion:
            gain,stamp=self.last_gain;age=now-stamp
            if age<.7:self.text(f'+{gain:,}',right,198-age*14,14,p['gold'],'number',anchor='topright',alpha=round((1-age/.7)*255))

    def draw_board(self,now):
        board=self.board_base();sh,pad=self.tile_shadows[('board',self.theme)]
        self.canvas.blit(sh,((BX*S-pad),(BY*S-pad+7*S)))
        self.canvas.blit(board,(BX*S,BY*S))
        anim=self.animation
        if anim:
            duration=.075 if self.auto and self.speed==2 else .13
            elapsed=now-anim['start'];t=elapsed/duration
            if t<1:
                t=1-(1-t)**3
                for track in anim['tracks']:
                    x,y=self.cell_xy(track.source);tx,ty=self.cell_xy(track.target)
                    self.tile(track.value,x+(tx-x)*t,y+(ty-y)*t)
            else:
                u=min(1,(elapsed-duration)/(.09 if self.auto and self.speed==2 else .17))
                for i,v in enumerate(self.game.board):
                    scale=1.;flash=0
                    if i in anim['merges']:
                        scale=1+.075*math.sin(math.pi*u)*(1-u);flash=max(0,1-u*2)
                    if i==anim['spawn']:
                        # Quick settling instead of a distracting full-size bounce.
                        scale=.65+.35*(1-(1-min(1,u*1.5))**3)
                    self.tile(v,*self.cell_xy(i),scale,flash)
                if u>=1:self.animation=None
        else:
            for i,v in enumerate(self.game.board):self.tile(v,*self.cell_xy(i))
        if self.ended and not self.animation:
            veil=pg.Surface((BS*S,BS*S),pg.SRCALPHA)
            pg.draw.rect(veil,(*pg.Color(self.p['bg'])[:3],218),veil.get_rect(),border_radius=23*S)
            self.canvas.blit(veil,(BX*S,BY*S))
            self.text('本局结束',BX+BS/2,BY+BS/2-48,28,anchor='center')
            self.text(f'{self.game.score:,} 分',BX+BS/2,BY+BS/2-5,19,self.p['muted'],anchor='center')
            self.button('new',BX+BS/2-89,BY+BS/2+35,178,45,'再来一局',icon='plus',primary=True)

    def status_text(self):
        if self.ai_error:return 'AI 暂时不可用'
        if (self.pending or self.auto) and not self.ai_ready:return 'AI 正在准备…'
        if self.auto:return '自动进行中 · 空格暂停'
        if self.pending:return 'AI 思考中…'
        if self.ai_result and not self.ai_result.get('applied'):
            return '建议'+{'left':'向左','up':'向上','right':'向右','down':'向下'}.get(self.ai_result.get('direction'),'继续')
        return None

    def draw_controls(self):
        p=self.p;x=676;right=W-BX;rw=right-x
        largest=max(self.game.board)
        targets=[128,512,2048,8192,16384,32768,65536,131072,1048576]
        target=next((v for v in targets if v>largest),largest*2)
        self.text('下个目标',x,353,12,p['muted'])
        self.text(f'{target:,}',right,345,25,p['text'],'number',anchor='topright')
        self.box(x,390,rw,3,p['line'],1)
        self.box(x,390,max(3,rw*min(1,largest/target)),3,p['gold'],1)
        self.text(f'最大方块  {largest:,}',x,409,11,p['muted'])
        self.button('auto',x,478,rw,52,'暂停自动玩' if self.auto else '自动玩',icon='pause' if self.auto else 'play',primary=True,enabled=not self.ended)
        self.button('undo',x,546,(rw-12)/2,46,'撤销',icon='undo',enabled=bool(self.game.history),selected=True)
        self.button('hint',x+(rw+12)/2,546,(rw-12)/2,46,'提示',icon='spark',selected=True)
        self.button('new',x,610,rw,42,'新游戏',icon='plus')
        status=self.status_text()
        self.text(status or '相同数字相遇，就会合并。',x+rw/2,682,11,p['muted'],anchor='center')
        self.line((BX,741),(W-BX,741))
        self.text('方向键 / WASD 移动',BX,767,11,p['muted'],anchor='midleft')
        self.text('空格自动玩',BX+173,767,11,p['muted'],anchor='midleft')
        mins,secs=divmod(int(self.game.elapsed),60)
        self.text(f'{self.game.moves:,} 步   /   {mins:02}:{secs:02}',BX+BS,767,11,p['muted'],anchor='midright')
        self.circle(x+3,767,2.5,p['gold'] if self.auto else p['muted'])
        self.text('AI 自动进行中' if self.auto else '示例棋盘' if self.args.demo else '进度自动保存',x+15,767,11,p['muted'],anchor='midleft')
        self.button('records',right-66,750,66,34,'战绩',small=True)

    def draw(self):
        now=time.monotonic();self.buttons=[]
        self.canvas.blit(self.background(),(0,0))
        self.draw_header(now);self.draw_board(now);self.draw_controls()
        if self.modal:self.draw_modal()
        self.toasts=[t for t in self.toasts if now-t[1]<2.5]
        if self.toasts and not self.modal:
            message,stamp=self.toasts[-1]
            self.panel(W/2-195,43,390,32,16,self.p['soft'])
            self.text(message,W/2,59,12,self.p['text'],anchor='center')
        sw,sh=self.screen.get_size();self.factor=min(sw/W,sh/H)
        dw,dh=round(W*self.factor),round(H*self.factor);self.offset=((sw-dw)//2,(sh-dh)//2)
        self.screen.fill(self.p['bg'])
        self.screen.blit(pg.transform.smoothscale(self.canvas,(dw,dh)),self.offset)
        pg.display.flip()

    def new_game(self):
        super().new_game();self.buffered_direction=None;self.toasts=[]

    def screen_point(self,pos):
        sw,sh=self.screen.get_size();factor=min(sw/W,sh/H)
        dw,dh=round(W*factor),round(H*factor)
        return ((pos[0]-(sw-dw)//2)*W/dw,(pos[1]-(sh-dh)//2)*H/dh)

    def move(self,direction,by_ai=False):
        if self.modal or self.ended:return
        if self.animation and not by_ai:
            self.stop_auto();self.buffered_direction=direction;return
        super().move(direction,by_ai)

    def update(self,dt):
        super().update(dt)
        if self.buffered_direction and not self.animation and not self.modal:
            direction=self.buffered_direction;self.buffered_direction=None;self.move(direction)

    def play_sound(self,name):
        if self.auto and self.speed==3:return
        super().play_sound(name)

    def draw_modal(self):
        p=self.p
        self.modal_veil();self.buttons=[]
        w,h=600,570
        if self.modal=='new':h=254
        if self.modal=='help':h=510
        x,y=(W-w)/2,(H-h)/2
        self.panel(x,y,w,h,22)
        self.button('close',x+w-60,y+20,36,36,icon='close')
        titles={'settings':'设置','intelligence':'AI 分析','help':'玩法与快捷键','records':'战绩','new':'开始新游戏？'}
        self.text(titles.get(self.modal,'设置'),x+32,y+29,24)
        if self.modal=='settings':
            self.text('AI 思考',x+32,y+94,13,p['muted'])
            for i,(key,label) in enumerate([(3,'自适应'),(0,'快速'),(1,'标准'),(2,'深入')]):
                self.button('quality'+str(key),x+163+i*97,y+80,91,40,label,selected=self.quality==key)
            self.text('此模式使用专用规则搜索与验证。' if self.game.mode in ('puzzle','rescue','expedition') else ['每步约 25 毫秒','每步约 100 毫秒','每步约 450 毫秒','简单局面快走，拥挤局面多想一步'][self.quality],x+171,y+128,11,p['muted'])
            self.text('自动速度',x+32,y+181,13,p['muted'])
            for i,label in enumerate(['慢速','正常','快速','冲分']):
                self.button('speed'+str(i),x+163+i*97,y+167,91,40,label,selected=self.speed==i)
            self.text('冲分模式跳过动画，以最快速度自动进行。',x+171,y+214,11,p['muted'])
            self.line((x+32,y+252),(x+w-32,y+252))
            for i,(key,label,value) in enumerate([('theme','外观','浅色' if self.theme=='light' else '深色'),('sound','音效','开启' if self.sound else '关闭'),('motion','动画','开启' if self.motion else '关闭')]):
                yy=y+270+i*51
                self.text(label,x+32,yy+12,14)
                self.button(key,x+w-145,yy,113,40,value,selected=True)
            self.line((x+32,y+433),(x+w-32,y+433))
            self.button('records',x+26,y+452,140,42,'战绩',icon='trophy')
            self.button('help',x+167,y+452,162,42,'玩法与快捷键')
            self.button('intelligence',x+368,y+452,200,42,'查看 AI 分析',icon='spark')
            self.text('进度自动保存',x+32,y+527,11,p['muted'])
            self.button('full',x+w-132,y+509,100,40,'全屏')
        elif self.modal=='intelligence':
            result=self.ai_result
            self.text('上一步搜索结果' if result and result.get('applied') else '当前棋盘的方向比较',x+32,y+78,13,p['muted'])
            if result:
                vals=dict(result.get('values',[]))
                lo=min(vals.values()) if vals else 0;hi=max(vals.values()) if vals else 1
                for i,d in enumerate(('left','up','right','down')):
                    xx=x+40+i*135;valid=d in vals
                    bar=(.22+.78*(vals[d]-lo)/max(1,hi-lo))*135 if valid else 4
                    self.panel(xx,y+126,110,166,12,p['soft'])
                    self.panel(xx+11,y+280-bar,88,bar,7,p['accent'] if result.get('direction')==d else mix(p['accent'],p['soft'],.55))
                    self.text({'left':'向左','up':'向上','right':'向右','down':'向下'}[d],xx+55,y+318,16,p['text'],anchor='center')
                    self.text('推荐' if result.get('direction')==d else '可走' if valid else '不可走',xx+55,y+350,12,p['muted'],anchor='center')
                self.text(f"前瞻 {result.get('depth',0)} 层",x+32,y+396,18)
                self.text(f"{result.get('nodes',0):,} 个局面 · {result.get('ms',0)} ms",x+w-32,y+402,12,p['muted'],anchor='topright')
                self.text('条形表示相对局面评分，并非胜率。',x+32,y+442,12,p['muted'])
            else:
                self.text('获取提示后，可以查看各方向的搜索结果。',x+w/2,y+243,15,p['muted'],anchor='center')
                self.text('思考中…' if self.pending else 'Expectimax · 概率搜索',x+w/2,y+284,12,p['muted'],anchor='center')
            self.button('inspect_hint',x+32,y+h-72,258,42,'重新分析',icon='spark',selected=True)
            self.button('resume_auto',x+306,y+h-72,262,42,'开始自动玩',icon='play',primary=True)
        elif self.modal=='help':
            self.text('移动方块，合并相同数字。达到 2048 后仍可继续。',x+32,y+85,13,p['muted'])
            entries=[('方向键 / WASD','移动；也支持鼠标拖动与触控滑动'),('空格','开始或暂停自动玩'),('Z / ⇧Z / H','撤销 / 重做 / 提示'),('N / T / M','新游戏 / 切换外观 / 开关音效'),('F / P / Esc','全屏 / 保存截图 / 关闭面板或暂停')]
            for i,(key,value) in enumerate(entries):
                yy=y+141+i*51
                self.text(key,x+32,yy,13,p['accent']);self.text(value,x+219,yy,12,p['muted'])
                self.line((x+32,yy+34),(x+w-32,yy+34))
            self.text('B 模式大厅 · C 教练 · R 复盘 · Enter 让 AI 走一步。',x+32,y+429,11,p['muted'])
            self.button('step',x+w-157,y+457,125,34,'AI 走一步',selected=True)
        elif self.modal=='new':
            self.text('重新尝试同一个开局，已获星级保留。' if self.game.mode=='puzzle' else '开启新的 60 步冲刺，最佳成绩保留。' if self.game.mode=='sprint' else '重新挑战同一残局，完成记录保留。' if self.game.mode=='rescue' else '开启新远征，能力组合重新选择。' if self.game.mode=='expedition' else '当前战绩会保留。',x+32,y+102,15,p['muted'])
            self.button('cancel',x+32,y+177,258,44,'继续这一局',selected=True)
            self.button('confirm_new',x+306,y+177,262,44,'开始新游戏',primary=True)
        elif self.modal=='records':
            self.text('本机最高 7 局',x+32,y+85,13,p['muted'])
            rows=[r for r in self.store.data['records'] if r.get('id')!=self.game.id]
            if self.game.moves and self.game.mode not in ('puzzle','sprint','expedition','rescue'):rows.append(dict(id=self.game.id,score=self.game.score,tile=max(self.game.board),ai=bool(self.game.ai_moves),assisted=self.game.assisted,mode=self.game.mode,date='进行中'))
            rows=sorted(rows,key=lambda r:r.get('score',0),reverse=True)[:7]
            if not rows:self.text('完成第一局后，成绩会出现在这里。',x+w/2,y+290,15,p['muted'],anchor='center')
            for i,row in enumerate(rows):
                yy=y+139+i*51
                self.text(f'{i+1:02}',x+32,yy,13,p['muted'],'number')
                self.text(f"{row['score']:,}",x+77,yy-6,23,p['text'],'number')
                self.text(f"最大 {row['tile']:,}",x+228,yy+2,12,p['muted'])
                label=('每日·' if row.get('mode')=='daily' else '')+('辅助' if row.get('assisted',row.get('ai')) else '手动')
                self.text(label,x+357,yy+2,11,p['accent'])
                self.text(row.get('date',''),x+w-32,yy+2,10,p['muted'],anchor='topright')
                self.line((x+32,yy+34),(x+w-32,yy+34))
            self.text('自动保存于本机',x+32,y+h-39,11,p['muted'])

    def act(self,key):
        if key in ('settings','intelligence'):
            last=self.ai_result;self.stop_auto();self.ai_result=last
            self.buffered_direction=None;self.modal=key;return
        if key=='inspect_hint':
            self.stop_auto();self.manual_request='inspect';return
        if key=='resume_auto':
            self.modal=None;super().act('auto');return
        if key=='step':self.modal=None
        super().act(key)
        if key in ('confirm_new','undo','new','help','records'):self.buffered_direction=None

    def modal_veil(self):
        overlay=pg.Surface((W*S,H*S),pg.SRCALPHA)
        overlay.fill((5,7,13,70 if self.theme=='light' else 115));self.canvas.blit(overlay,(0,0))


def main():
    parser=argparse.ArgumentParser(description='2048 · Python 桌面游戏')
    parser.add_argument('--demo',action='store_true')
    parser.add_argument('--screenshot')
    parser.add_argument('--smoke-seconds',type=float,default=0)
    Atelier(parser.parse_args()).run()

if __name__=='__main__':
    mp.freeze_support();main()
