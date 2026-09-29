"""A mode lobby, verified puzzle chapters, and a finite 60-turn score attack."""
import time,math
import pygame as pg
from engine import Game,can_move
from puzzles import LEVELS,make_puzzle,spawn_draws
from insight import NAMES
from modes import today

class Journey:
    def __init__(self,args):
        super().__init__(args)
        raw=self.store.data.get('puzzle_progress',{})
        self.progress={k:v for k,v in raw.items() if k in {str(i) for i in range(len(LEVELS))}
            and isinstance(v,dict) and type(v.get('stars')) is int and 1<=v['stars']<=3} if isinstance(raw,dict) else {}
        self.store.data['puzzle_progress']=self.progress.copy()
        raw=self.store.data.get('sprint_best',{})
        self.store.data['sprint_best']={k:v for k,v in raw.items() if k in ('manual','assisted') and type(v) is int and v>=0} if isinstance(raw,dict) else {}
        self.path_revealed=False;self.episode_recorded=None
        self.refresh_episode()

    def make_new_game(self):
        if self.game.mode=='puzzle':return make_puzzle(self.game.puzzle_id)
        if self.game.mode=='sprint':return Game(mode='sprint')
        return super().make_new_game()

    def activate_game(self,game):
        super().activate_game(game);self.modal_progress=0.;self.path_revealed=False;self.refresh_episode()

    def new_game(self):
        super().new_game();self.path_revealed=False;self.refresh_episode()

    def refresh_episode(self):
        game=self.game
        if game.mode=='puzzle':self.ended=max(game.board)>=LEVELS[game.puzzle_id]['target'] or game.moves>=LEVELS[game.puzzle_id]['limit'] or not can_move(game.board)
        elif game.mode=='sprint':self.ended=game.moves>=60 or not can_move(game.board)

    def check_achievements(self):
        if self.game.mode not in ('puzzle','sprint','expedition','rescue'):super().check_achievements()

    def move(self,direction,by_ai=False):
        before=self.game.moves;super().move(direction,by_ai)
        if self.game.moves!=before:
            self.path_revealed=False;self.refresh_episode()
            if self.ended:self.auto=False

    def update_features(self,dt):
        self.refresh_episode();super().update_features(dt)
        game=self.game;stamp=(game.id,game.moves,game.assisted,game.undos)
        if game.mode not in ('puzzle','sprint','expedition','rescue') or not self.ended or stamp==self.episode_recorded:return
        self.episode_recorded=stamp
        if game.mode=='puzzle' and max(game.board)>=LEVELS[game.puzzle_id]['target']:
            stars=1 if game.assisted else 3 if game.moves<=LEVELS[game.puzzle_id]['par'] and not game.undos else 2
            key=str(game.puzzle_id);previous=self.progress.get(key,{})
            if stars>previous.get('stars',0):
                self.progress={**self.progress,key:dict(stars=stars,moves=game.moves,assisted=game.assisted)}
                self.store.data['puzzle_progress']=self.progress.copy()
        elif game.mode=='sprint':
            key='assisted' if game.assisted else 'manual'
            scores=self.store.data['sprint_best'];self.store.data['sprint_best']={**scores,key:max(scores.get(key,0),game.score)}
        self.save()

    def ai_options(self,kind):
        options=super().ai_options(kind)
        if self.game.mode=='puzzle':
            level=LEVELS[self.game.puzzle_id]
            options['puzzle']=dict(rng=self.game.rng.getstate(),target=level['target'],remaining=level['limit']-self.game.moves)
        return options

    def act(self,key):
        if key in ('modes','lobby'):
            self.cancel_input();self.stop_auto();self.modal='lobby';self.modal_progress=1.
            self.modal_render_key=None;self.modal_blurred=None;self.modal_bounds=None;return
        if key=='puzzle_levels':
            self.cancel_input();self.stop_auto();self.modal='levels';self.modal_progress=0.;return
        if key.startswith('level_'):
            index=int(key[6:])
            if not 0<=index<len(LEVELS):return
            self.cancel_input();self.stop_auto();self.sessions.stash(self.game)
            saved=self.sessions.sessions.get('puzzle')
            resume=bool(saved and saved.get('puzzle_id')==index and saved['moves']<LEVELS[index]['limit'] and max(saved['board'])<LEVELS[index]['target'])
            self.activate_game(Game.restore(saved) if resume else make_puzzle(index));return
        if key in ('mode_puzzle','mode_sprint'):
            self.switch_mode(key[5:]);return
        if key=='puzzle_retry':self.cancel_input();self.new_game();return
        if key=='puzzle_next':
            self.act('level_'+str(self.game.puzzle_id+1)) if self.game.puzzle_id+1<len(LEVELS) else self.act('puzzle_levels');return
        if key=='reveal_path':self.path_revealed=True;return
        if key in ('close','cancel') and self.modal=='lobby':self.modal_progress=0.
        if key in ('hint','inspect_hint'):self.path_revealed=False
        super().act(key)
        if key in ('undo','redo','confirm_new'):self.refresh_episode()

    def draw_lobby(self,now):
        p=self.p
        self.text('2048',64,40,30,p['text'],'display')
        self.button('close',836,40,180,44,'继续当前局',icon='play',selected=True)
        self.text('选择玩法',64,112,30,p['text'],'title')
        self.text('四种玩法，各自保存进度。',66,155,14,p['muted'])

        def card(key,x,y,w,h,tint):
            rect=pg.Rect(x,y,w,h);hover=rect.collidepoint(self.mouse)
            t=self.hover_values.get(key,0)+(float(hover)-self.hover_values.get(key,0))*(1-math.exp(-self.ui_dt/.09))
            self.hover_values[key]=t
            if not self.motion:t=float(hover)
            self.float_panel(x,y,w,h,24,strength=.035,tint=tint)
            if t>.01:
                overlay=pg.Surface((w*2,h*2),pg.SRCALPHA)
                colour=pg.Color(p['gold']);colour.a=round(t*100)
                pg.draw.rect(overlay,colour,overlay.get_rect().inflate(-3,-3),width=2,border_radius=47)
                self.canvas.blit(overlay,(x*2,y*2))
            self.buttons.append((key,rect,True))
            return t

        def action(label,x,y,right,hover,primary=False):
            self.text(label,x,y,15,p['text'],'body_medium')
            self.box(right-32,y-6,32,32,p['accent'] if primary else p['soft'],16)
            fg=p['ink'] if primary else p['text'];xx=right-23+hover*2
            self.line((xx,y+10),(xx+12,y+10),fg,1.5)
            self.line((xx+8,y+6),(xx+12,y+10),fg,1.5)
            self.line((xx+8,y+14),(xx+12,y+10),fg,1.5)

        def resume_label(mode,initial):
            key='daily:'+today() if mode=='daily' else mode
            current=self.game.mode==mode and (mode!='daily' or self.game.challenge_date==today())
            return '继续游戏' if current or key in self.sessions.sessions else initial

        hover=card('mode_classic',64,204,464,500,'#c9ddfa')
        self.text('经典',96,235,28,p['text'],'title')
        self.text('合并数字，挑战更高的方块。',97,278,14,p['muted'])
        self.draw_lobby_board(178,335)
        self.text('无限步数 · 随时保存',97,595,12,p['muted'])
        self.line((96,632),(496,632),p['line'])
        action(resume_label('classic','开始游戏'),97,655,496,hover,True)

        hover=card('puzzle_levels',552,204,464,228,'#ded8f4')
        self.text('解局剧场',584,235,25,p['text'],'title')
        self.text('在有限步数里，找到最短的解法。',585,276,13,p['muted'])
        self.text('固定落子 · 三星挑战',585,305,12,p['muted'])
        self.draw_mode_emblem('puzzle',913,238,now)
        self.text(f'{len(self.progress):02} / 12',585,367,19,p['gold'],'number')
        self.text('章节完成',674,373,11,p['muted'])
        action('选择章节',845,373,984,hover)

        hover=card('mode_sprint',552,456,220,248,'#edddce')
        self.text('限步冲刺',576,484,22,p['text'],'title')
        self.text('用 60 步，争取最高分。',577,523,12,p['muted'])
        self.text('60',574,558,45,p['text'],'number')
        self.text('步',640,589,13,p['muted'])
        action(resume_label('sprint','开始冲刺'),577,655,748,hover)

        hover=card('mode_daily',796,456,220,248,'#cfe4df')
        self.text('每日同局',820,484,22,p['text'],'title')
        self.text('每天一个相同的开局。',821,523,12,p['muted'])
        self.text(today()[8:],818,558,45,p['text'],'number')
        self.text(str(int(today()[5:7]))+' 月',884,589,13,p['muted'])
        action(resume_label('daily','今日挑战'),821,655,992,hover)

        self.line((64,744),(1016,744),p['line'])
        self.text('方向键移动 · 空格开启自动玩',66,765,12,p['muted'])
        self.text('所有模式均支持 AI、撤销和复盘',1014,765,12,p['muted'],anchor='topright')

    def draw_lobby_board(self,x,y):
        # Reuse the real tile material, cached at the size of this illustration.
        key=('lobby_board',self.theme)
        if key not in self.surfaces:
            board=pg.Surface((240*2,240*2),pg.SRCALPHA)
            pg.draw.rect(board,self.p['soft'],board.get_rect(),border_radius=40)
            values=[0,2,4,8,2,4,16,32,4,16,64,128,8,32,256,2048]
            for i,value in enumerate(values):
                xx=13+(i%4)*55;yy=13+(i//4)*55
                if not value:
                    pg.draw.rect(board,self.p['slot'],pg.Rect(xx*2,yy*2,96,96),border_radius=24)
                else:
                    tile=pg.transform.smoothscale(self.tile_surface(value),(137,137))
                    board.blit(tile,tile.get_rect(center=((xx+24)*2,(yy+24)*2)))
            self.surfaces[key]=board
        self.canvas.blit(self.surfaces[key],(x*2,y*2))

    def warm_journey(self):
        # Generate new game panels before input starts, including the finish
        # overlay; a win should never pause to build a large blurred shadow.
        for x,y,w,h,r in [(54,197,202,265,24),(825,197,202,213,24),
            (54,197,202,258,24),(825,197,202,215,24),(302,329,472,187,28)]:
            self.float_panel(x,y,w,h,r)

    def draw_mode_emblem(self,mode,x,y,now):
        p=self.p
        if mode in ('classic','puzzle'):
            for i,value in enumerate(([2,4,8,16] if mode=='classic' else [16,0,16,32])):
                xx=x+(i%2)*32;yy=y+(i//2)*32
                self.box(xx,yy,27,27,p['soft'] if value else p['slot'],8)
                if value:self.text(str(value),xx+13.5,yy+13.5,12,p['gold'],'number',anchor='center')
            if mode=='puzzle':self.icon('spark',x+34,y+2,p['gold'],22)
        elif mode=='sprint':
            self.text('60',x+30,y+28,39,p['gold'],'number',anchor='center')
            for i in range(12):self.box(x+i*5,y+59,3,8 if i%3 else 12,p['line'],1)
        else:
            self.box(x,y,64,65,p['soft'],14)
            self.text(today()[5:7]+'月',x+32,y+13,9,p['muted'],anchor='center')
            self.text(today()[8:],x+32,y+39,29,p['gold'],'number',anchor='center')

    def draw_journey_sides(self,now):
        p=self.p;game=self.game
        if game.mode=='puzzle':
            level=LEVELS[game.puzzle_id];left=max(0,level['limit']-game.moves)
            self.float_panel(54,197,202,265,24)
            self.text(f"第 {game.puzzle_id+1:02} 章",77,220,12,p['muted'],'body_medium')
            self.text(level['title'],75,249,27)
            self.text('合成目标',77,301,11,p['muted'])
            self.text(str(level['target']),74,327,40,p['gold'],'number')
            self.wrapped(level['note'],77,394,154,11,limit=2)
            self.float_panel(825,197,202,213,24)
            self.text('剩余步数',848,221,11,p['muted'])
            self.text(f'{left:02}',844,246,47,p['text'],'number')
            self.text(f"最短 {level['par']} 步 · 上限 {level['limit']} 步",848,312,11,p['muted'])
            self.text('下一枚',848,363,11,p['muted'])
            next_value=spawn_draws(game.rng.getstate(),1)[0][1]
            self.box(961,348,42,42,p['soft'],12);self.text(str(next_value),982,369,23,p['gold'],'number',anchor='center')
            self.button('puzzle_retry',54,484,202,42,'原局重试',selected=True)
            self.button('puzzle_levels',54,535,202,42,'选择章节')
            self.wrapped('固定落子，重试可以走出不同的解法。',849,437,155,11,limit=3)
            self.wrapped('独立最短完成得三星；辅助完成得一星。',849,509,155,11,limit=3)
        elif game.mode=='sprint':
            self.float_panel(54,197,202,258,24)
            self.text('限步冲刺',77,222,12,p['muted'],'body_medium')
            self.text('60 步挑战',76,258,23,p['text'],'title')
            self.text('剩余步数',77,309,11,p['muted'])
            self.text(f'{max(0,60-game.moves):02}',74,335,49,p['gold'],'number')
            self.box(77,417,154,4,p['line'],2)
            if game.moves<60:self.box(77,417,max(2,154*(60-game.moves)/60),4,p['gold'],2)
            self.float_panel(825,197,202,215,24)
            scores=self.store.data['sprint_best']
            self.text('个人最佳 · 手动',848,222,11,p['muted'])
            self.text(f"{scores.get('manual',0):,}",846,252,27,p['text'],'number')
            self.text('个人最佳 · 含辅助',848,320,11,p['muted'])
            self.text(f"{scores.get('assisted',0):,}",846,350,24,p['gold'],'number')
            self.wrapped('只计算有效移动。撤销会回退步数，重新考虑也算一种策略。',77,492,154,11,limit=4)
            self.wrapped('第 60 步结算；无路可走时提前结束。',849,440,155,11,limit=3)

    def draw_episode_end(self):
        p=self.p;game=self.game
        self.float_panel(302,329,472,187,28)
        if game.mode=='puzzle':
            won=max(game.board)>=LEVELS[game.puzzle_id]['target']
            self.text('这一局，解开了。' if won else '再换一条路。',538,367,25,anchor='center')
            award='一星 · 辅助完成' if game.assisted else '三星 · 独立最短完成' if game.moves<=LEVELS[game.puzzle_id]['par'] and not game.undos else '二星 · 独立完成'
            detail=award+f' · {game.moves} 步' if won else '可以撤销一步，或回到同一个开局'
            self.text(detail,538,406,12,p['muted'],anchor='center')
            self.button('puzzle_retry',324,444,201,44,'原局再试',selected=True)
            self.button('puzzle_next' if won else 'undo',541,444,210,44,'下一章' if won else '撤销一步',primary=True,enabled=won or bool(game.history))
        else:
            self.text('六十步，你的答案。' if game.moves==60 else '本次冲刺结束',538,363,24,anchor='center')
            self.text(f'{game.score:,} 分 · '+('含辅助' if game.assisted else '手动'),538,406,16,p['gold'],anchor='center')
            self.button('new',324,444,201,44,'再冲一次',selected=True)
            self.button('lobby',541,444,210,44,'返回大厅',primary=True)

    def draw_modal(self):
        if self.modal!='levels':return super().draw_modal()
        self.buttons=[];x,y=240,125;p=self.p;self.panel(x,y,600,570,28)
        self.text('解局剧场',x+32,y+29,25)
        self.button('close',x+540,y+20,36,36,icon='close')
        self.text('12 个固定残局 · 在限定步数内合成目标方块',x+32,y+76,13,p['muted'])
        for i,level in enumerate(LEVELS):
            xx=x+32+i%3*182;yy=y+112+i//3*90
            self.panel(xx,yy,171,78,16,p['soft'])
            if pg.Rect(xx,yy,171,78).collidepoint(self.mouse):pg.draw.rect(self.canvas,p['gold'],pg.Rect(xx*2,yy*2,342,156),width=2,border_radius=32)
            self.text(f'{i+1:02}',xx+14,yy+13,12,p['gold'],'number')
            self.text(level['title'],xx+44,yy+12,15,p['text'],'body_medium')
            self.text(f"{level['target']} · {level['limit']} 步内",xx+14,yy+48,11,p['muted'])
            stars=self.progress.get(str(i),{}).get('stars',0)
            for star in range(3):
                points=[]
                for tip in range(10):
                    angle=-math.pi/2+tip*math.pi/5;radius=4.5 if tip%2==0 else 2.1
                    points.append((round((xx+128+star*13+math.cos(angle)*radius)*2),round((yy+55+math.sin(angle)*radius)*2)))
                pg.draw.polygon(self.canvas,p['gold'] if star<stars else p['line'],points)
            self.buttons.append(('level_'+str(i),pg.Rect(xx,yy,171,78),True))
        self.text(f'已完成 {len(self.progress)} / 12 章 · 独立最短完成得三星',x+32,y+485,11,p['muted'])
        self.button('lobby',x+32,y+516,256,34,'返回模式大厅',small=True)
        self.button('mode_puzzle',x+308,y+516,260,34,'继续解局',primary=True,small=True)

    def draw_analysis(self,x,y):
        if self.game.mode!='puzzle':return super().draw_analysis(x,y)
        p=self.p;result=self.ai_result
        self.text('上一手的验证 · 固定落子' if result and result.get('applied') else '固定落子 · 搜索验证的最短解法',x+32,y+82,13,p['muted'])
        if result and result.get('backend')=='exact':
            previews=result.get('previews',{});selected=self.preview_direction if self.preview_direction in previews else result.get('direction') or next(iter(previews),None)
            for i,(direction,name) in enumerate(NAMES.items()):
                self.button('preview_'+direction,x+32+i*136,y+113,128,37,name,selected=selected==direction,enabled=direction in previews,small=True)
            if selected:
                self.mini_board(previews[selected]['board'],x+32,y+176)
                distance=result['distances'][selected]
                self.text('选择这个方向后',x+310,y+182,11,p['muted'])
                self.text('可以完成' if distance else '步数内无解',x+310,y+214,23)
                self.text(f'含这一步，最快 {distance} 步' if distance else '试试别的方向，或撤销重来。',x+310,y+259,12,p['gold'])
                self.wrapped('左侧包含本次确定的新方块。这里显示的是验证结果，而非概率预测。',x+310,y+300,244,11,limit=4)
            if self.path_revealed and result.get('solution'):
                self.text(' → '.join(NAMES[d][1:] for d in result['solution']),x+32,y+449,17,p['gold'])
            else:self.button('reveal_path',x+32,y+438,536,34,'展开整条解法' if result.get('solvable') else '当前余下步数内没有解法',enabled=bool(result.get('solvable')),small=True)
            self.text(f"完整验证 {result.get('nodes',0):,} 个局面 · {result.get('ms',0)} ms",x+32,y+482,10,p['muted'])
        else:self.text('正在寻找确定的解法…' if not self.ended else '返回棋盘，重试或继续下一章。',x+300,y+265,15,p['muted'],anchor='center')
        self.button('inspect_hint',x+32,y+516,258,34,'重新验证',enabled=not self.ended,small=True)
        self.button('resume_auto',x+306,y+516,262,34,'演示解法',primary=True,enabled=not self.ended,small=True)
