"""Coaching, saved play modes, and read-only replay; UI extensions stay separate."""
import time,re
import pygame as pg
from engine import Game,can_move
from insight import NAMES,analyze_moves
from modes import SessionBook,daily_game,today,timeline,session_key

class Features:
    def __init__(self,args):
        super().__init__(args)
        self.sessions=SessionBook(self.store.data)
        self.coach=bool(self.store.data['settings'].get('coach',False))
        self.coach_token=None;self.coach_seen=self.token;self.coach_due=time.monotonic()+.5
        self.review_frames=[];self.review_index=0;self.review_playing=False;self.review_tick=0.
        self.preview_direction=None
        if self.store.data.get('intelligence_version')!=8:
            if self.quality==1:self.quality=3
            self.store.data['intelligence_version']=8

    def make_new_game(self):
        return daily_game(self.game.challenge_date) if self.game.mode=='daily' else Game()

    def new_game(self):
        super().new_game();self.coach_token=None;self.review_playing=False;self.review_frames=[]

    def switch_mode(self,mode):
        self.cancel_input();self.stop_auto();self.store.record(self.game)
        self.activate_game(self.sessions.switch(self.game,mode))

    def activate_game(self,game):
        self.game=game
        self.animation=None;self.effects.clear();self.modal=None;self.last_gain=None
        self.score_display=float(self.game.score);self.ended=not can_move(self.game.board)
        self.won=max(self.game.board)>=2048;self.played=self.game.moves>0
        self.review_frames=[];self.review_playing=False;self.coach_token=None
        self.toasts=[];self.save()

    def update_features(self,dt):
        now=time.monotonic()
        if self.token!=self.coach_seen:
            self.coach_seen=self.token;self.coach_due=now+.45
        if self.modal=='replay' and self.review_playing and now>=self.review_tick:
            self.review_index=min(len(self.review_frames)-1,self.review_index+1)
            self.review_tick=now+.45
            if self.review_index==len(self.review_frames)-1:self.review_playing=False
        if (self.coach and self.focused and not self.modal and not self.auto and not self.animation
            and not self.input_queue and not self.ended and self.ai_ready and not self.ai_error
            and not self.pending and not self.manual_request and not self.queued_ai
            and self.coach_token!=self.token and now>=self.coach_due):
            self.coach_token=self.token
            if not self.ai_result:self.ask_ai('coach')

    def act(self,key):
        if key=='coach':
            self.coach=not self.coach;self.coach_token=None;self.coach_due=time.monotonic()+.3
            if not self.coach and self.pending and self.pending[1]=='coach':self.invalidate_ai()
            if not self.coach and self.ai_result and self.ai_result.get('source')=='coach':self.ai_result=None
            self.save();return
        if key=='modes':self.stop_auto();self.modal='modes';return
        if key in ('mode_classic','mode_daily'):self.switch_mode(key[5:]);return
        if key=='replay':
            self.stop_auto();self.review_frames=timeline(self.game);self.review_index=len(self.review_frames)-1
            self.review_playing=False;self.modal='replay';return
        if key.startswith('replay_'):
            if not self.review_frames:return
            last=len(self.review_frames)-1
            if key=='replay_play':
                if self.review_index==last:self.review_index=0
                self.review_playing=not self.review_playing;self.review_tick=time.monotonic()+.45;return
            self.review_playing=False
            if key=='replay_first':self.review_index=0
            elif key=='replay_prev':self.review_index=max(0,self.review_index-1)
            elif key=='replay_next':self.review_index=min(last,self.review_index+1)
            elif key=='replay_last':self.review_index=last
            elif key=='replay_seek':self.review_index=round(max(0,min(1,(self.mouse[0]-272)/536))*last)
            return
        if key.startswith('preview_'):self.preview_direction=key[8:];return
        if key in ('close','cancel'):self.review_playing=False
        if key in ('intelligence','inspect_hint'):self.preview_direction=None
        super().act(key)
        if key=='intelligence' and (not self.ai_result or 'choices' not in self.ai_result) and not self.ended:
            self.manual_request='hint'

    def wrapped(self,text,x,y,width,size=12,color=None,limit=3):
        lines=[];line=''
        for char in re.findall(r'\d+(?:[.,]\d+)*(?:%)?|[A-Za-z]+|.',text):
            if self.font(size,'body').size(line+char)[0]/2>width and line:
                lines.append(line);line=char
            else:line+=char
        if line:lines.append(line)
        for i,line in enumerate(lines[:limit]):self.text(line,x,y+i*(size+7),size,color or self.p['muted'])

    def mini_board(self,board,x,y):
        for i,value in enumerate(board):
            xx=x+i%4*64;yy=y+i//4*64
            if not value:self.box(xx,yy,57,57,self.p['slot'],12);continue
            key=('mini',self.theme,value)
            if key not in self.surfaces:
                self.surfaces[key]=pg.transform.smoothscale(self.tile_surface(value).subsurface((48,48,224,224)),(114,114))
            self.canvas.blit(self.surfaces[key],(round(xx*2),round(yy*2)))

    def draw_modal(self):
        if self.modal not in ('modes','replay','intelligence'):return super().draw_modal()
        self.buttons=[];x,y,w,h=240,125,600,570;p=self.p
        self.panel(x,y,w,h,28);self.button('close',x+w-60,y+20,36,36,icon='close')
        self.text({'modes':'选择玩法','replay':'这一局的轨迹','intelligence':'AI 分析'}[self.modal],x+32,y+29,24)
        if self.modal=='modes':
            self.text('切换玩法会保留各自的进度。',x+32,y+82,13,p['muted'])
            for index,(key,title,description) in enumerate([
                ('classic','经典模式','自由练习，随时暂停、撤销或让 AI 接管。'),
                ('daily','每日同局','每日固定开局，相同操作可复现相同的落子。')]):
                yy=y+126+index*156
                self.panel(x+32,yy,536,138,20,p['soft'])
                self.text(title,x+52,yy+20,19)
                self.text(description,x+52,yy+56,11,p['muted'])
                active=self.game.mode==key and (key=='classic' or self.game.challenge_date==today())
                saved=self.sessions.sessions.get('classic' if key=='classic' else 'daily:'+today())
                label='继续这一局' if active else ('继续今日' if key=='daily' else '继续经典') if saved else '进入挑战' if key=='daily' else '开始经典'
                self.button('mode_'+key,x+388,yy+88,156,34,label,primary=True,small=True)
                subtitle=f'{self.game.score:,} 分 · {self.game.moves:,} 步' if active else f"{saved['score']:,} 分 · {saved['moves']:,} 步" if saved else today() if key=='daily' else '独立保存的经典对局'
                self.text(subtitle,x+52,yy+99,11,p['muted'])
            self.text('提示、教练与自动玩会标记为「含辅助」。',x+32,y+466,11,p['muted'])
            self.text('每日挑战在本机进行，不需要登录。',x+32,y+491,11,p['muted'])
        elif self.modal=='replay':self.draw_replay(x,y)
        else:self.draw_analysis(x,y)

    def draw_replay(self,x,y):
        p=self.p;frames=self.review_frames or timeline(self.game);index=min(self.review_index,len(frames)-1)
        frame=frames[index];first=frames[0]
        self.text('查看最近的走棋，不改变当前对局。',x+32,y+82,13,p['muted'])
        self.mini_board(frame['board'],x+32,y+126)
        self.text(f"第 {frame['moves']:,} 步",x+310,y+128,20)
        self.text(f"{frame['score']:,}",x+310,y+177,34,p['text'],'number')
        self.text('当时得分',x+312,y+219,11,p['muted'])
        self.text(f"最大方块  {max(frame['board']):,}",x+310,y+264,13)
        gain=frame['score']-frames[index-1]['score'] if index else 0
        self.text(f'本步 +{gain:,}' if index else '可回看的起点',x+310,y+298,12,p['muted'])
        if index:
            ai=frame['ai_moves']>frames[index-1]['ai_moves']
            self.text('AI 执行' if ai else '手动操作',x+310,y+332,11,p['muted'])
        values=[v['score'] for v in frames];lo,hi=min(values),max(values)
        pts=[(x+32+i/max(1,len(values)-1)*536,y+432-(value-lo)/max(1,hi-lo)*38) for i,value in enumerate(values)]
        for a,b in zip(pts,pts[1:]):self.line(a,b,p['gold'],1.7)
        dot=pts[index];self.circle(*dot,3,p['accent'])
        self.buttons.append(('replay_seek',pg.Rect(x+32,y+391,536,54),True))
        self.text(f"第 {first['moves']:,} 步",x+32,y+448,10,p['muted'])
        self.text(f"第 {frames[-1]['moves']:,} 步",x+568,y+448,10,p['muted'],anchor='topright')
        self.button('replay_first',x+32,y+498,72,42,'起点',enabled=index>0)
        self.button('replay_prev',x+112,y+498,72,42,'前一步',enabled=index>0)
        self.button('replay_play',x+192,y+498,168,42,'暂停回放' if self.review_playing else '播放回放',primary=True,enabled=len(frames)>1)
        self.button('replay_next',x+368,y+498,80,42,'后一步',enabled=index<len(frames)-1)
        self.button('replay_last',x+456,y+498,112,42,'回到当前',enabled=index<len(frames)-1)

    def draw_analysis(self,x,y):
        result=self.ai_result;p=self.p
        if result and result.get('choices'):
            choices=result['choices'];values=dict(result.get('values',[]));lo=min(values.values(),default=0);hi=max(values.values(),default=0)
            selected=self.preview_direction if self.preview_direction in choices else result.get('direction')
            selected=selected if selected in choices else next(iter(choices));move=choices[selected]
            self.text(('上一手的分析' if result.get('applied') else '当前局面')+' · 点击方向查看合并预览',x+32,y+82,12,p['muted'])
            for i,(direction,name) in enumerate(NAMES.items()):
                xx=x+32+i*136
                self.button('preview_'+direction,xx,y+113,128,37,name+(' · 推荐' if direction==result.get('direction') else ''),selected=direction==selected,enabled=direction in choices,small=True)
                if direction in values:
                    self.box(xx+9,y+155,110*(.12+.88*(values[direction]-lo)/max(1.,hi-lo)),2,p['gold'],1)
            self.mini_board(move['board'],x+32,y+176)
            self.text('合并收益',x+310,y+177,11,p['muted'])
            self.text(f"+{move['gain']:,}",x+308,y+201,31,p['text'],'number')
            self.text(f"{move['merges']} 组合并 · 落子后 {move['empty']} 个空格",x+310,y+264,12)
            self.text('下一次落子后的终局风险',x+310,y+301,11,p['muted'])
            self.text(f"{move['loss']:.0%}",x+310,y+324,23,p['gold'] if move['loss'] else p['text'],'number')
            note=result.get('explanation','') if selected==result.get('direction') else '正在比较这个方向，推荐方向仍以搜索结果为准。'
            self.wrapped(note,x+310,y+371,248,11,limit=3)
            policy='复用分析' if result.get('cached') else '自适应' if result.get('adaptive') else '固定预算'
            self.text(f"{policy} · 搜索 {result.get('depth',0)} 层 · {result.get('nodes',0):,} 局面 · {result.get('ms',0)} ms",x+32,y+443,11,p['muted'])
            self.text('细条是相对评分；预览不含随机新方块。风险只计算下一次落子。',x+32,y+469,10,p['muted'])
        else:
            self.text('本局已结束，可在复盘里回看。' if self.ended else '正在分析四个方向…' if self.pending or self.manual_request else '点击重新分析，比较四个方向。',x+300,y+250,16,p['muted'],anchor='center')
            self.text('保留棋盘，在后台计算。' if not self.ended else '撤销最后一步，也可以继续探索。',x+300,y+289,12,p['muted'],anchor='center')
        self.button('inspect_hint',x+32,y+498,258,42,'重新分析',icon='spark',selected=True,enabled=not self.ended)
        self.button('resume_auto',x+306,y+498,262,42,'开始自动玩',icon='play',primary=True,enabled=not self.ended)
