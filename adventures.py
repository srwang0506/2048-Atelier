"""Ability expeditions and verified second-chance games, integrated with the UI."""
from copy import deepcopy
from hashlib import sha256
import math,time
import pygame as pg
from engine import Game,can_move
from modes import timeline
from expedition import (ABILITIES,STAGES,make_expedition,choose,remaining,limit,swap_cost,powers,refresh,description)
from rescue import make_rescue,practice_challenges,valid_challenge
from insight import NAMES

class Adventures:
    def __init__(self,args):
        self.lobby_tab='classic';self.rescue_tab='personal';self.rescue_job=None;self.rescue_status=''
        self.swap_selection=[];self.review_step=0;self.review_original=False;self.adventure_stamp=None;self.reference_cache={}
        super().__init__(args)
        raw=self.store.data.get('rescue_archive',[])
        self.rescue_archive=[c for c in raw if valid_challenge(c)][:6] if isinstance(raw,list) else []
        self.practice=practice_challenges()
        self.store.data['rescue_archive']=self.rescue_archive.copy()
        raw=self.store.data.get('rescue_checked',[])
        self.rescue_checked=[s for s in raw if isinstance(s,str)][:12] if isinstance(raw,list) else []
        self.store.data['rescue_checked']=self.rescue_checked.copy()
        raw=self.store.data.get('rescue_results',{})
        ids={c['id'] for c in self.rescue_archive+self.practice}
        self.rescue_results={k:{kind:n for kind,n in v.items() if kind in ('manual','assisted') and type(n) is int and 1<=n<=6} for k,v in raw.items() if k in ids and isinstance(v,dict)} if isinstance(raw,dict) else {}
        self.store.data['rescue_results']=deepcopy(self.rescue_results)
        raw=self.store.data.get('expedition_records',[])
        self.expedition_records=[r for r in raw if isinstance(r,dict) and isinstance(r.get('id'),str) and all(type(r.get(k)) is int and r[k]>=0 for k in ('score','cleared','moves'))][:12] if isinstance(raw,list) else []
        self.store.data['expedition_records']=deepcopy(self.expedition_records)
        self.refresh_adventure()

    def warm_adventures(self):
        for geometry in ((54,197,202,224),(54,442,202,205),(825,197,202,450),(54,197,202,262),(825,197,202,225)):
            self.float_panel(*geometry,24)
        for c in self.practice+self.rescue_archive:self.reference(c)

    def reference(self,c):
        if c['id'] not in self.reference_cache:
            g=make_rescue(c);frames=[dict(board=g.board[:])]
            for d in c['solution']:g.move(d);frames.append(dict(board=g.board[:]))
            self.reference_cache[c['id']]=frames
        return self.reference_cache[c['id']]

    def challenge(self,identity=None):
        identity=identity or (self.game.extra.get('challenge') if self.game.mode=='rescue' else None)
        return next((c for c in self.rescue_archive+self.practice if c['id']==identity),None)

    def refresh_adventure(self):
        g=self.game
        if g.mode=='expedition':refresh(g);self.ended=g.extra['phase']!='play'
        elif g.mode=='rescue':self.ended=g.board.count(0)>=g.extra['goal'] or g.moves>=g.extra['limit'] or not can_move(g.board)

    def activate_game(self,game):
        super().activate_game(game);self.swap_selection=[];self.adventure_stamp=None;self.refresh_adventure()
        if game.mode=='expedition' and game.extra['phase'] in ('draft','clear'):self.modal='draft'

    def make_new_game(self):
        if self.game.mode=='expedition':return make_expedition()
        if self.game.mode=='rescue':
            c=self.challenge()
            if c:return make_rescue(c)
            return Game()
        return super().make_new_game()

    def new_game(self):
        super().new_game();self.adventure_stamp=None;self.refresh_adventure()
        if self.game.mode=='expedition':self.modal='draft';self.toasts=[]

    def move(self,direction,by_ai=False):
        was_auto=self.auto
        before=(self.game.moves,len(self.game.history),self.game.score,self.game.extra.get('energy'))
        super().move(direction,by_ai);self.refresh_adventure()
        if was_auto and by_ai and self.game.mode=='expedition' and not self.ended:self.auto=True
        if before!=(self.game.moves,len(self.game.history),self.game.score,self.game.extra.get('energy')) and self.game.mode in ('expedition','rescue'):
            if self.ended:self.stop_auto()
            self.save()

    def ai_options(self,kind):
        if self.game.mode=='expedition':
            e=deepcopy(self.game.extra);e['_remaining']=remaining(self.game);e['_needed']=STAGES[e['stage']][1]-(self.game.score-e['stage_score'])
            return {'expedition':e}
        if self.game.mode=='rescue':return {'rescue':dict(rng=self.game.rng.getstate(),goal=self.game.extra['goal'],remaining=self.game.extra['limit']-self.game.moves)}
        return super().ai_options(kind)

    def request_rescue(self):
        g=self.game
        if self.rescue_job or g.mode not in ('classic','daily','sprint') or can_move(g.board):return
        stamp=f"{g.id}:{g.moves}:"+sha256(repr(g.board).encode()).hexdigest()[:8]
        if stamp in self.rescue_checked:return
        self.rescue_job=('rescue:'+stamp,time.monotonic());self.rescue_status='正在回溯结束前的局面…'
        self.requests.put((self.rescue_job[0],[],.1,{'extract_rescue':g.serialize()}))

    def receive_rescue(self,token,result):
        if not self.rescue_job or token!=self.rescue_job[0]:return
        self.rescue_job=None
        if result.get('status')!='timeout' and 'error' not in result:
            self.rescue_checked=([token[7:]]+self.rescue_checked)[:12];self.store.data['rescue_checked']=self.rescue_checked.copy()
        c=result.get('challenge')
        if c and valid_challenge(c):
            rows=[c]+[r for r in self.rescue_archive if r['id']!=c['id']]
            pinned=self.game.extra.get('challenge') if self.game.mode=='rescue' else self.sessions.sessions.get('rescue',{}).get('extra',{}).get('challenge')
            held=next((r for r in rows if r['id']==pinned),None)
            self.rescue_archive=rows[:6]
            if held and held not in self.rescue_archive:self.rescue_archive=rows[:5]+[held]
            self.store.data['rescue_archive']=deepcopy(self.rescue_archive)
            self.rescue_status=f"找到一条 {c['par']} 步翻盘路线，已经收入你的残局。"
            self.toast('这局还有另一条路 · 已收入绝境重生')
        elif result.get('status')=='not_found':self.rescue_status='没有找到符合条件的残局，可以先体验练习局。'
        elif result.get('status')=='timeout':
            self.rescue_status='本次搜索预算用尽，可手动重新检查。'
            # Avoid resubmitting every frame; an explicit retry clears this key.
            self.rescue_checked=([token[7:]]+self.rescue_checked)[:12]
        else:self.rescue_status='暂时无法生成残局，可以稍后重试。';self.rescue_checked=([token[7:]]+self.rescue_checked)[:12]
        self.save()

    def update_features(self,dt):
        self.refresh_adventure();super().update_features(dt)
        g=self.game
        if g.mode in ('classic','daily','sprint') and not can_move(g.board):self.request_rescue()
        if self.rescue_job and (not self.process.is_alive() or time.monotonic()-self.rescue_job[1]>20):
            stamp=self.rescue_job[0][7:];self.rescue_checked=([stamp]+self.rescue_checked)[:12]
            self.rescue_job=None;self.rescue_status='搜索进程未返回，可以稍后重试。'
        if g.mode=='expedition' and g.extra['phase'] in ('draft','clear') and not self.modal and not self.animation:
            self.cancel_input();self.stop_auto();self.modal='draft';self.modal_progress=0.
        stamp=(g.id,g.mode,g.moves,g.score,g.assisted,g.undos)
        if not self.ended or stamp==self.adventure_stamp:return
        if g.mode=='expedition' and g.extra['phase'] in ('won','lost'):
            self.adventure_stamp=stamp
            row=dict(id=g.id,score=g.score,moves=g.moves,cleared=g.extra['cleared'],won=g.extra['phase']=='won',assisted=g.assisted,perks=deepcopy(g.extra['perks']))
            self.expedition_records=sorted([row]+[r for r in self.expedition_records if r['id']!=g.id],key=lambda r:(r['cleared'],r['score']),reverse=True)[:12]
            self.store.data['expedition_records']=deepcopy(self.expedition_records);self.save()
        elif g.mode=='rescue' and g.board.count(0)>=g.extra['goal']:
            self.adventure_stamp=stamp;key=g.extra['challenge'];kind='assisted' if g.assisted else 'manual'
            self.rescue_results=deepcopy(self.rescue_results);row=self.rescue_results.setdefault(key,{})
            row[kind]=min(row.get(kind,99),g.moves);self.store.data['rescue_results']=deepcopy(self.rescue_results);self.save()

    def act(self,key):
        if key in ('tab_featured','tab_classic'):
            self.lobby_tab=key[4:];self.cancel_input();return
        if key in ('expedition_intro','rescue_library','expedition_rules','rescue_review'):
            self.cancel_input();self.stop_auto();self.modal=key;self.modal_progress=0.
            if key=='rescue_review':
                self.review_step=0;self.review_original=False
                if not self.ended:self.game.assisted=True;self.save()
            return
        if key=='mode_expedition':
            self.cancel_input();self.stop_auto();self.switch_mode('expedition');return
        if key in ('expedition_new','expedition_confirm'):
            self.cancel_input();self.stop_auto()
            saved=self.game.extra if self.game.mode=='expedition' else self.sessions.sessions.get('expedition',{}).get('extra',{})
            if key=='expedition_new' and saved and saved.get('phase') not in ('won','lost'):
                self.modal='expedition_reset';return
            self.sessions.stash(self.game);self.activate_game(make_expedition());return
        if key.startswith('perk_'):
            if self.game.mode=='expedition' and choose(self.game,key[5:]):
                self.cancel_input();self.stop_auto();self.effects.clear();self.modal=None;self.refresh_adventure();self.save();self.toast('已获得 '+ABILITIES[key[5:]][0])
            return
        if key=='draft':self.cancel_input();self.stop_auto();self.modal='draft';return
        if key=='freeze':self.cancel_input();self.move('freeze');return
        if key=='swap':
            self.cancel_input();self.stop_auto();self.swap_selection=[];self.modal='swap';self.modal_progress=0.;return
        if key.startswith('swapcell_'):
            i=int(key[9:])
            if not self.game.board[i]:return
            if i in self.swap_selection:self.swap_selection.remove(i)
            else:self.swap_selection=(self.swap_selection+[i])[-2:]
            return
        if key=='swap_confirm':
            if len(self.swap_selection)==2:
                i,j=self.swap_selection;action=f'swap:{min(i,j)}:{max(i,j)}'
                if action in powers(self.game):self.modal=None;self.cancel_input();self.move(action)
            return
        if key in ('rescue_personal','rescue_practice'):
            self.rescue_tab=key[7:];return
        if key=='rescue_resume':
            saved=self.sessions.sessions.get('rescue')
            if self.game.mode=='rescue':self.modal=None
            elif saved:self.cancel_input();self.stop_auto();self.sessions.stash(self.game);self.activate_game(Game.restore(saved))
            return
        if key.startswith('rescue_play_'):
            c=self.challenge(key[12:])
            if c:
                self.cancel_input();self.stop_auto();self.sessions.stash(self.game)
                saved=self.sessions.sessions.get('rescue')
                g=Game.restore(saved) if saved and saved.get('extra',{}).get('challenge')==c['id'] else None
                if not g or g.moves>=g.extra['limit'] or g.board.count(0)>=g.extra['goal']:g=make_rescue(c)
                self.activate_game(g)
            return
        if key=='rescue_retry':self.cancel_input();self.new_game();return
        if key=='find_rescue':self.rescue_checked=[];self.request_rescue();self.act('rescue_library');return
        if key=='review_prev':self.review_step=max(0,self.review_step-1);return
        if key=='review_next':self.review_step=min(10,self.review_step+1);return
        if key=='review_original':self.review_original=not self.review_original;self.review_step=0;return
        if key in ('close','cancel') and self.modal=='draft':self.act('lobby');return
        super().act(key)
        if key in ('undo','redo'):self.refresh_adventure()

    def draw_lobby(self,now):
        if self.lobby_tab=='classic':super().draw_lobby(now)
        else:
            p=self.p
            self.text('2048',64,40,30,p['text'],'display')
            self.button('close',836,40,180,44,'继续当前局',icon='play',selected=True)
            self.text('选择玩法',64,112,30,p['text'],'title')
            self.text('构筑一场远征，或救回一盘败局。',66,155,14,p['muted'])
            for x,tint in ((64,'#c6d9ef'),(552,'#ddd2ef')):self.float_panel(x,210,464,494,24,strength=.05,tint=tint)
            self.text('能力远征',96,243,30,p['text'],'title')
            self.text('六关挑战 · 能力三选一 · 组合你的打法',98,290,13,p['muted'])
            self.text('绝境重生',584,243,30,p['text'],'title')
            self.text('回到真实败局的关键一步，找出另一条路。',585,290,13,p['muted'])
            for i,(title,big,detail) in enumerate([('连击','×2','连续合并'),('蓄能','06','能量交换'),('豪赌','×2.5','高分与风险')]):
                xx=97+i*132;yy=359+(10 if i!=1 else 0)
                self.float_panel(xx,yy,120,168,18,strength=.025,tint='#c7d5ef')
                self.text(title,xx+16,yy+17,16,p['text'],'body_medium')
                self.text(big,xx+60,yy+85,30,p['gold'],'number',anchor='center')
                self.text(detail,xx+60,yy+137,11,p['muted'],anchor='center')
            self.text('合并充能 → 释放能力 → 过关升级',97,575,13,p['muted'])
            record=max((r['cleared'] for r in self.expedition_records),default=0)
            self.text(f'个人进度  {record} / 6 关',98,609,12,p['gold'])
            self.button('expedition_intro',96,650,400,36,'进入远征',primary=True)
            c=self.rescue_archive[0] if self.rescue_archive else self.practice[0] if self.practice else None
            if c:
                ref=self.reference(c)[-1]['board']
                self.draw_small_board(c['origin']['board'],585,363,176)
                self.draw_small_board(ref,809,363,176)
                self.icon('right',772,437,p['gold'],23)
                self.text('结束前的局面',673,558,12,p['muted'],anchor='center')
                self.text(f"{c['par']} 步后的可能",897,558,12,p['muted'],anchor='center')
            self.text(f'你的残局  {len(self.rescue_archive)} 局 · 另有 3 局练习' if self.rescue_archive else '先玩一局练习，再挑战自己的残局',585,609,12,p['gold'])
            self.button('rescue_library',584,650,400,36,'寻找翻盘机会',selected=True)
            self.line((64,744),(1016,744),p['line'])
            self.text('支持撤销与复盘 · 每种模式独立保存',66,765,12,p['muted'])
            self.text('经典、每日、解局与冲刺 →',1014,765,12,p['muted'],anchor='topright')
        self.button('tab_classic',746,115,135,38,'经典与挑战',selected=self.lobby_tab=='classic')
        self.button('tab_featured',891,115,125,38,'精选玩法',selected=self.lobby_tab=='featured')

    def draw_small_board(self,board,x,y,width):
        cell=(width-18)/4;step=cell+6
        for i,value in enumerate(board):
            xx=x+i%4*step;yy=y+i//4*step
            self.box(xx,yy,cell,cell,self.p['soft'] if value else self.p['slot'],9)
            if value:self.text(str(value),xx+cell/2,yy+cell/2,17 if value<100 else 13 if value<1000 else 11,self.p['gold'],'number',anchor='center')

    def draw_journey_sides(self,now):
        g=self.game;p=self.p
        if g.mode=='expedition':
            e=g.extra;stage=e['stage'];progress=g.score-e['stage_score'];target=STAGES[stage][1]
            self.float_panel(54,197,202,224,24)
            self.text(f'第 {stage+1} / 6 关',77,219,12,p['muted'],'body_medium')
            self.text(STAGES[stage][0],75,247,26,p['text'],'title')
            self.text(f'{progress:,}',76,288,29,p['text'],'number')
            self.text(f'本关目标 {target:,} 分',77,331,12,p['muted'])
            self.box(77,366,154,4,p['line'],2);self.box(77,366,max(2,154*min(1,progress/target)),4,p['gold'],2)
            self.text(f'剩余 {remaining(g)} 步',77,388,12,p['text'],'body_medium')
            self.float_panel(54,442,202,205,24)
            self.text('能量',77,463,12,p['muted']);self.text(f"{e['energy']} / 12",231,460,19,p['gold'],'number',anchor='topright')
            for i in range(12):self.box(77+i*13,497,9,5,p['gold'] if i<e['energy'] else p['line'],2)
            self.text(f"连击 {e['streak']}"+(' · 凝时 '+str(e['freeze'])+' 步' if e['freeze'] else ''),77,517,11,p['muted'])
            self.button('freeze',69,546,172,36,'凝时 · 5 能量' if not e['cooldown'] else f"凝时冷却 {e['cooldown']} 步",enabled='freeze' in powers(g),selected=True,small=True)
            self.button('swap',69,592,172,36,f'交换 · {swap_cost(e)} 能量',enabled=any(a.startswith('swap:') for a in powers(g)),selected=True,small=True)
            self.float_panel(825,197,202,450,24)
            self.text('能力组合',848,219,15,p['text'],'body_medium')
            if not e['perks']:self.text('选择第一枚能力',848,265,12,p['muted'])
            for i,(key,rank) in enumerate(e['perks'].items()):
                yy=265+i*53
                self.text(ABILITIES[key][0],848,yy,14,p['text'],'body_medium')
                self.text('Ⅱ' if rank==2 else 'Ⅰ',1003,yy,14,p['gold'],anchor='topright')
                self.text(ABILITIES[key][2],848,yy+24,10,p['muted'])
            self.button('expedition_rules',840,600,172,32,'查看能力与规则',small=True)
        elif g.mode=='rescue':
            c=self.challenge();self.float_panel(54,197,202,262,24)
            self.text('绝境重生',77,220,12,p['muted'],'body_medium')
            self.text('打开空间',75,254,25,p['text'],'title')
            self.text(f"{g.board.count(0)} / {g.extra['goal']}",75,300,36,p['gold'],'number')
            self.text('至少留下三个空格',77,353,12,p['muted'])
            self.wrapped('落子沿用当时的随机状态，换条路就有不同结果。',77,391,154,11,limit=3)
            self.button('rescue_retry',54,484,202,42,'原局重试',selected=True)
            self.button('rescue_library',54,535,202,42,'选择残局')
            self.float_panel(825,197,202,225,24)
            self.text('剩余步数',848,220,12,p['muted']);self.text(str(max(0,g.extra['limit']-g.moves)),845,251,46,p['text'],'number')
            self.text(f"最快 {g.extra['par']} 步 · 上限 6 步",848,321,11,p['muted'])
            self.text('练习残局' if c and c.get('practice') else '来自你的真实对局',848,373,12,p['gold'])
            if c:self.wrapped(f"回到第 {c['source_moves']} 步，距离当时结束还有 {c['rewind']} 步。",848,447,155,12,limit=3)
            self.button('rescue_review',832,535,186,42,'并排对照解法',small=True)
        else:super().draw_journey_sides(now)

    def draw_episode_end(self):
        g=self.game;p=self.p
        if g.mode not in ('expedition','rescue'):return super().draw_episode_end()
        self.float_panel(302,329,472,187,28)
        if g.mode=='expedition':
            phase=g.extra['phase'];title={'won':'六关远征，完成！','lost':'这次远征到此为止','draft':'选择你的第一枚能力','clear':'本关达成，选择升级'}[phase]
            self.text(title,538,366,23,anchor='center')
            self.text(f"{g.score:,} 分 · 完成 {g.extra['cleared']} / 6 关 · "+('含辅助' if g.assisted else '手动'),538,405,12,p['muted'],anchor='center')
            self.button('lobby',324,444,201,44,'返回大厅',selected=True)
            self.button('draft' if phase in ('clear','draft') else 'expedition_intro',541,444,210,44,'选择能力' if phase in ('clear','draft') else '远征档案',primary=True)
        else:
            won=g.board.count(0)>=g.extra['goal']
            self.text('这一次，救回来了。' if won else '还有别的走法',538,366,24,anchor='center')
            self.text(f"{g.moves} 步 · "+('辅助完成' if g.assisted else '独立完成') if won else '可以撤销一步，也可以重新挑战同一局面',538,405,12,p['muted'],anchor='center')
            self.button('rescue_retry',324,444,201,44,'原局重试',selected=True)
            self.button('rescue_review',541,444,210,44,'对照两条路线',primary=True)

    def draw_rescue_prompt(self):
        p=self.p
        self.button('rescue_library' if self.rescue_archive else 'find_rescue',365,531,350,40,'翻盘机会已找到 · 进入绝境重生' if self.rescue_archive else '正在验证翻盘路线…' if self.rescue_job else '寻找翻盘机会',enabled=not self.rescue_job,selected=True)

    def draw_adventure_hint(self,now):
        r=self.ai_result
        if not r or self.auto or self.animation or self.ended:return
        self.float_panel(302,655,476,36,18,shadow=False)
        d=r.get('direction');label='凝时' if d=='freeze' else '交换两枚方块' if d and d.startswith('swap:') else NAMES.get(d,'暂无验证路线')
        self.text(label,318,663,12,self.p['text'],'body_medium')
        text=r.get('explanation','')
        self.text(text,760,665,10,self.p['muted'],anchor='topright')

    def draw_modal(self):
        modal=self.modal
        if modal not in ('expedition_intro','draft','swap','expedition_rules','rescue_library','rescue_review','expedition_reset'):return super().draw_modal()
        self.buttons=[];x,y=240,125;p=self.p
        if modal=='expedition_reset':
            y=283;self.panel(x,y,600,254,28)
            self.text('重新开始远征？',x+32,y+30,24,p['text'],'title')
            self.text('当前远征的棋盘与能力组合将被新旅程替换。',x+32,y+102,14,p['muted'])
            self.button('expedition_intro',x+32,y+177,258,44,'保留当前远征',selected=True)
            self.button('expedition_confirm',x+306,y+177,262,44,'重新出发',primary=True);return
        self.panel(x,y,600,570,28)
        titles={'expedition_intro':'能力远征','draft':'选择一枚能力','swap':'交换方块','expedition_rules':'能力与规则','rescue_library':'绝境重生','rescue_review':'两条路线，同一个起点'}
        self.text(titles[modal],x+32,y+29,25,p['text'],'title');self.button('close',x+540,y+20,36,36,icon='close')
        if modal=='expedition_intro':self.draw_expedition_intro(x,y)
        elif modal=='draft':self.draw_draft(x,y)
        elif modal=='swap':self.draw_swap(x,y)
        elif modal=='expedition_rules':self.draw_expedition_rules(x,y)
        elif modal=='rescue_library':self.draw_rescue_library(x,y)
        else:self.draw_rescue_review(x,y)

    def draw_expedition_intro(self,x,y):
        p=self.p
        self.text('六关挑战。每次选择，都让这一局有不同的打法。',x+32,y+81,13,p['muted'])
        for i,(name,target,steps) in enumerate(STAGES):
            xx=x+50+i*91
            if i<5:self.line((xx+15,y+158),(xx+76,y+158),p['line'],2)
            self.circle(xx,y+158,14,p['soft']);self.text(str(i+1),xx,y+158,13,p['gold'],'number',anchor='center')
            self.text(name,xx,y+194,12,p['muted'],anchor='center')
        rows=[('01','选择能力','开局与每次过关三选一；同名能力可以升级一次。'),('02','合并充能','能量上限 12。凝时暂停落子，交换改变数字位置。'),('03','逐关突破','达到本关分数过关；移除一枚最小方块后继续。')]
        for i,(num,title,detail) in enumerate(rows):
            yy=y+244+i*64;self.text(num,x+32,yy,13,p['gold'],'number');self.text(title,x+68,yy-2,15,p['text'],'body_medium')
            self.text(detail,x+68,yy+25,11,p['muted'])
        best=max((r['cleared'] for r in self.expedition_records),default=0)
        manual=max((r['score'] for r in self.expedition_records if not r.get('assisted')),default=0)
        self.text(f'最远 {best} / 6 关 · 手动最高 {manual:,} 分',x+32,y+460,12,p['gold'])
        saved=self.sessions.sessions.get('expedition');current=self.game if self.game.mode=='expedition' else Game.restore(saved) if saved else None
        resume=current is not None and current.extra['phase'] not in ('won','lost')
        self.button('mode_expedition' if resume else 'lobby',x+32,y+508,258,42,'继续当前远征' if resume else '返回大厅',selected=True)
        self.button('expedition_new',x+306,y+508,262,42,'开启新远征',primary=True)

    def draw_draft(self,x,y):
        if self.game.mode!='expedition':return
        e=self.game.extra;p=self.p
        title='选择起手能力，开始第一关。' if e['phase']=='draft' else f"第 {e['stage']+1} 关完成。选择能力，进入下一关。"
        self.text(title,x+32,y+82,13,p['muted'])
        for i,key in enumerate(e['offers']):
            xx=x+32+i*182;rank=e['perks'].get(key,0)+1
            self.panel(xx,y+128,171,322,18,p['soft'])
            self.text('升级至 Ⅱ' if rank==2 else '新能力 · Ⅰ',xx+17,y+149,11,p['gold'],'body_medium')
            self.text(ABILITIES[key][0],xx+16,y+184,19,p['text'],'title')
            self.text(ABILITIES[key][2],xx+17,y+224,11,p['muted'])
            self.wrapped(description(key,rank),xx+17,y+267,138,13,p['text'],limit=5)
            self.button('perk_'+key,xx+14,y+397,143,36,'选择此能力',primary=True,small=True)
        self.text('过关后保留棋盘与能量；新的关卡重新记录撤销历史。',x+32,y+478,11,p['muted'])
        self.button('lobby',x+32,y+516,536,34,'保存进度，稍后选择',small=True)

    def draw_swap(self,x,y):
        p=self.p;g=self.game
        if g.mode!='expedition':return
        self.text('选择两枚不同数字。交换不占步数，可撤销。',x+32,y+81,13,p['muted'])
        self.mini_board(g.board,x+32,y+136)
        for i,value in enumerate(g.board):
            xx=x+32+i%4*64;yy=y+136+i//4*64
            if i in self.swap_selection:pg.draw.rect(self.canvas,p['accent'],pg.Rect(xx*2,yy*2,114,114),3,border_radius=24)
            self.buttons.append(('swapcell_'+str(i),pg.Rect(xx,yy,57,57),bool(value)))
        self.text('能量消耗',x+322,y+151,12,p['muted']);self.text(str(swap_cost(g.extra)),x+319,y+184,44,p['gold'],'number')
        self.wrapped('把关键数字放到更合适的位置，接续合并和连击。',x+322,y+271,206,13,limit=4)
        valid=len(self.swap_selection)==2 and g.board[self.swap_selection[0]]!=g.board[self.swap_selection[1]] and g.extra['energy']>=swap_cost(g.extra)
        self.text('已选择 '+str(len(self.swap_selection))+' / 2 枚',x+32,y+451,12,p['muted'])
        self.button('close',x+32,y+508,258,42,'取消',selected=True);self.button('swap_confirm',x+306,y+508,262,42,'确认交换',enabled=valid,primary=True)

    def draw_expedition_rules(self,x,y):
        if self.game.mode!='expedition':return
        p=self.p;e=self.game.extra
        self.text('主动能力不消耗步数；只有有效移动推进回合。',x+32,y+81,12,p['muted'])
        self.wrapped('每组合并获得 1 点基础能量。凝时消耗 5 点，基础阻止两次落子、六次有效移动后冷却。交换消耗 6 点，可由能力降低。',x+32,y+115,536,12,limit=3)
        for i,(key,rank) in enumerate(e['perks'].items()):
            yy=y+204+i*44;self.text(ABILITIES[key][0]+(' Ⅱ' if rank==2 else ' Ⅰ'),x+32,yy,13,p['text'],'body_medium')
            self.wrapped(description(key,rank),x+182,yy,354,11,limit=2)
        self.text('AI 使用远征规则搜索，可使用能量；能力选择由你决定。',x+32,y+484,11,p['muted'])
        self.button('close',x+32,y+516,536,34,'回到远征',primary=True,small=True)

    def draw_rescue_library(self,x,y):
        p=self.p;personal=self.rescue_tab=='personal';rows=self.rescue_archive if personal else self.practice
        self.text('六步之内打开三个空格。每一局都有经过验证的路线。',x+32,y+80,12,p['muted'])
        self.button('rescue_personal',x+32,y+114,258,36,'我的残局',selected=personal,small=True)
        self.button('rescue_practice',x+308,y+114,260,36,'练习残局',selected=not personal,small=True)
        if not rows:
            self.icon('undo',x+275,y+225,p['gold'],44)
            self.text('下一盘败局，也可能是新的开始',x+300,y+303,20,p['text'],'title',anchor='center')
            self.text('经典、每日或冲刺卡死后，自动检查结束前的十步。',x+300,y+353,12,p['muted'],anchor='center')
            self.text('有解的局面会出现在这里。也可以先体验练习残局。',x+300,y+382,12,p['muted'],anchor='center')
            self.button('rescue_practice',x+169,y+420,262,38,'先练一局',primary=True,small=True)
        for i,c in enumerate(rows[:6]):
            xx=x+32+i%2*276;yy=y+172+i//2*97
            self.panel(xx,yy,260,85,16,p['soft'])
            title=c.get('title','第 '+str(c['source_moves'])+' 步的另一条路')
            self.text(title,xx+16,yy+13,14,p['text'],'body_medium')
            result=self.rescue_results.get(c['id'],{});best=result.get('manual')
            detail=f'独立完成 · {best} 步' if best else f"最快 {c['par']} 步 · "+('辅助完成' if result.get('assisted') else '待挑战')
            self.text(detail,xx+16,yy+49,11,p['muted']);self.icon('right',xx+225,yy+50,p['gold'],14)
            self.buttons.append(('rescue_play_'+c['id'],pg.Rect(xx,yy,260,85),True))
        if self.rescue_status:self.wrapped(self.rescue_status,x+32,y+472,536,11,limit=2)
        else:self.text('独立与辅助成绩分别记录；原来的对局始终保留。',x+32,y+477,11,p['muted'])
        saved=self.game.mode=='rescue' or bool(self.sessions.sessions.get('rescue'))
        eligible=self.game.mode in ('classic','daily','sprint') and not can_move(self.game.board)
        if eligible:
            self.button('lobby',x+32,y+516,166,34,'返回大厅',small=True)
            self.button('find_rescue',x+217,y+516,166,34,'重新搜索',enabled=not self.rescue_job,small=True)
            self.button('rescue_resume',x+402,y+516,166,34,'继续残局',enabled=saved,selected=True,small=True)
        else:
            self.button('lobby',x+32,y+516,258,34,'返回大厅',small=True)
            self.button('rescue_resume',x+306,y+516,262,34,'继续当前残局',enabled=saved,selected=True,small=True)

    def draw_rescue_review(self,x,y):
        c=self.challenge();p=self.p
        if not c:
            self.text('从残局中进入对照，可以看到本次与参考走法。',x+32,y+100,12,p['muted']);return
        reference=self.reference(c)
        mine=[dict(board=c['origin']['board'])]+c['original'] if self.review_original else timeline(self.game)
        last=max(len(mine),len(reference))-1;step=min(self.review_step,last)
        self.text('左侧 '+('原来的败局' if self.review_original else '本次走法')+' · 右侧已验证的最短路线',x+32,y+80,12,p['muted'])
        self.text(f"{'当时' if self.review_original else '本次'} · 第 {min(step,len(mine)-1)} 步",x+32,y+119,13,p['text'],'body_medium')
        self.text(f'参考 · 第 {min(step,len(reference)-1)} 步',x+318,y+119,13,p['gold'],'body_medium')
        self.mini_board(mine[min(step,len(mine)-1)]['board'],x+32,y+157)
        self.mini_board(reference[min(step,len(reference)-1)]['board'],x+318,y+157)
        self.text(' → '.join(NAMES[d][1:] for d in c['solution']),x+318,y+424,12,p['gold'])
        self.button('review_original',x+32,y+457,252,34,'查看本次走法' if self.review_original else '对比原来的败局',small=True)
        self.text(f'{step} / {last}',x+550,y+465,12,p['muted'],'number',anchor='topright')
        self.button('review_prev',x+32,y+510,166,38,'上一步',enabled=step>0,small=True)
        self.button('review_next',x+218,y+510,166,38,'下一步',enabled=step<last,primary=True,small=True)
        self.button('close',x+404,y+510,164,38,'回到棋盘',small=True)

    def draw_analysis(self,x,y):
        if self.game.mode not in ('expedition','rescue'):return super().draw_analysis(x,y)
        p=self.p;r=self.ai_result
        self.text('能力、能量与风险共同参与判断' if self.game.mode=='expedition' else '按原对局随机状态，验证有限步数内的解法',x+32,y+82,12,p['muted'])
        if r and r.get('backend') in ('expedition','rescue'):
            direction=r.get('direction');choices=r.get('choices',r.get('previews',{}))
            if direction and direction in choices:
                self.mini_board(choices[direction]['board'],x+32,y+145)
                label='凝时' if direction=='freeze' else '交换方块' if direction.startswith('swap:') else NAMES[direction]
                self.text(label,x+320,y+152,24,p['text'],'title')
                self.wrapped(r.get('explanation',''),x+320,y+206,216,13,limit=5)
                self.text('包含本次确定的新方块' if self.game.mode=='rescue' else '示意不包含随机新方块',x+32,y+418,11,p['muted'])
            else:self.wrapped(r.get('explanation','暂无可用结果'),x+32,y+160,536,15,limit=3)
            self.text(f"搜索 {r.get('nodes',0):,} 个局面 · {r.get('ms',0)} ms",x+32,y+463,11,p['muted'])
        else:self.text('正在分析…',x+300,y+269,16,p['muted'],anchor='center')
        self.button('inspect_hint',x+32,y+516,258,34,'重新分析',enabled=not self.ended,small=True)
        self.button('resume_auto',x+306,y+516,262,34,'演示走法',enabled=not self.ended,primary=True,small=True)
