// Rules and randomness are independent of rendering. MT19937 matches Python Random(int).
export const DIRS = ['left','up','right','down'];
export const clone = value => structuredClone(value);
export const empty = board => board.reduce((n,v)=>n+!v,0);
export const validBoard = b => Array.isArray(b)&&b.length===16&&b.every(v=>Number.isSafeInteger(v)&&(v===0||(v>=2&&Number.isInteger(Math.log2(v)))));
export const validRng=r=>r&&Array.isArray(r.mt)&&r.mt.length===624&&r.mt.every(v=>Number.isInteger(v)&&v>=0&&v<=0xffffffff)&&Number.isInteger(r.index)&&r.index>=0&&r.index<=624;
export class Random {
  constructor(seed=0,state=null) {
    if(state){this.mt=state.mt.slice();this.index=state.index;return;}
    this.mt=new Array(624);this.mt[0]=19650218;
    for(let i=1;i<624;i++)this.mt[i]=(Math.imul(1812433253,this.mt[i-1]^(this.mt[i-1]>>>30))+i)>>>0;
    let n=BigInt(seed),words=[];do{words.push(Number(n&0xffffffffn));n>>=32n;}while(n);
    let i=1,j=0;
    for(let k=Math.max(624,words.length);k;k--){this.mt[i]=((this.mt[i]^Math.imul(this.mt[i-1]^(this.mt[i-1]>>>30),1664525))+words[j]+j)>>>0;if(++i>=624){this.mt[0]=this.mt[623];i=1;}if(++j>=words.length)j=0;}
    for(let k=623;k;k--){this.mt[i]=((this.mt[i]^Math.imul(this.mt[i-1]^(this.mt[i-1]>>>30),1566083941))-i)>>>0;if(++i>=624){this.mt[0]=this.mt[623];i=1;}}
    this.mt[0]=0x80000000;this.index=624;
  }
  uint(){if(this.index>=624){for(let i=0;i<624;i++){let y=(this.mt[i]&0x80000000)|(this.mt[(i+1)%624]&0x7fffffff);this.mt[i]=(this.mt[(i+397)%624]^(y>>>1)^((y&1)?0x9908b0df:0))>>>0;}this.index=0;}let y=this.mt[this.index++];y^=y>>>11;y^=(y<<7)&0x9d2c5680;y^=(y<<15)&0xefc60000;y^=y>>>18;return y>>>0;}
  random(){return ((this.uint()>>>5)*67108864+(this.uint()>>>6))/9007199254740992;}
  choice(n){let k=Math.floor(Math.log2(n))+1,v;do{v=this.uint()>>>(32-k);}while(v>=n);return v;}
  state(){return {mt:this.mt.slice(),index:this.index};}
}
export function slide(board,direction){
  if(!DIRS.includes(direction))throw new Error('Invalid direction');
  const out=Array(16).fill(0),tracks=[],merges=[];let gain=0;
  for(let line=0;line<4;line++){
    const ids=Array.from({length:4},(_,c)=>direction==='left'?line*4+c:direction==='right'?line*4+3-c:direction==='up'?c*4+line:(3-c)*4+line);
    const vals=ids.filter(i=>board[i]);let dest=0;
    for(let n=0;n<vals.length;n++){
      const src=vals[n],target=ids[dest++];let value=board[src];tracks.push({source:src,target,value});
      if(n+1<vals.length&&board[vals[n+1]]===value){tracks.push({source:vals[++n],target,value});value*=2;gain+=value;merges.push(target);}
      out[target]=value;
    }
  }
  return {board:out,gain,tracks,merges,changed:out.some((v,i)=>v!==board[i])};
}
export function canMove(b){return b.some(Boolean)&&(empty(b)>0||b.some((v,i)=>(i%4<3&&v===b[i+1])||(i<12&&v===b[i+4])));}
export function spawn(board,rng,mode='classic',prob=.1){const cells=board.map((v,i)=>!v?i:-1).filter(i=>i>=0);if(!cells.length)return null;const i=cells[mode==='puzzle'?Math.floor(rng.random()*cells.length):rng.choice(cells.length)];board[i]=rng.random()<1-prob?2:4;return i;}
export const STAGES=[['启程',100,26],['蓄势',260,34],['回响',520,42],['临界',900,46],['跃迁',1400,52],['终章',2200,60]];
export const ABILITIES={
  combo:['连击引擎','连续合并，每层加成 25% / 40%，最多叠加四层。','↗'],battery:['蓄能核心','每组合并额外获得 1 / 2 点能量。','ϟ'],gambit:['豪赌协议','得分 ×2 / ×2.5；新方块为 4 的概率升至 30% / 40%。','◇'],corner:['角落增幅','在四角合并时，额外得分 50% / 100%。','⌜'],echo:['共鸣回路','同时合并至少两组，基础分额外增加 50% / 100%。','◎'],flow:['空间回流','合并至少 3 / 2 组，本步不生成新方块。','≈'],reserve:['从容节拍','每关额外增加 4 / 8 次有效移动。','+'],warp:['折跃透镜','交换方块消耗降至 4 / 3 点能量。','⇄'],ice:['凝时晶体','凝时延长至 3 / 4 步，冷却仍为六步。','❄']};
export function remaining(g){return g.mode==='sprint'?Math.max(0,60-g.moves):g.mode==='expedition'?Math.max(0,STAGES[g.extra.stage][2]+4*(g.extra.perks.reserve||0)-(g.moves-g.extra.stage_start)):g.mode==='puzzle'?Math.max(0,g.extra.level.limit-g.moves):g.mode==='rescue'?Math.max(0,g.extra.limit-g.moves):Infinity;}
export const swapCost=e=>[6,4,3][e.perks.warp||0];
export const fourProbability=e=>e?.perks?.gambit?.valueOf()? .2+.1*e.perks.gambit:.1;
const roundEven=n=>n%1===.5?Math.round(n/2)*2:Math.round(n);
export function reward(board,gain,merges,extra){
  const e=clone(extra),p=e.perks;e.streak=gain?e.streak+1:0;
  const multiplier=p.combo?1+Math.min(4,Math.max(0,e.streak-1))*(p.combo===2?.4:.25):1;
  let bonus=merges.filter(i=>[0,3,12,15].includes(i)).reduce((n,i)=>n+board[i],0)*.5*(p.corner||0);
  if(merges.length>=2)bonus+=gain*.5*(p.echo||0);
  const points=roundEven((gain+bonus)*multiplier*(p.gambit?(p.gambit===1?2:2.5):1));
  e.energy=Math.min(12,e.energy+merges.length*(1+(p.battery||0)));
  const skip=e.freeze>0||(p.flow>0&&merges.length>=4-p.flow);e.freeze=Math.max(0,e.freeze-1);e.cooldown=Math.max(0,e.cooldown-1);
  return {points,skip,extra:e};
}
export function powers(g){if(g.mode!=='expedition'||g.extra.phase!=='play')return [];const e=g.extra,result=[];
  if(e.energy>=5&&!e.freeze&&!e.cooldown&&canMove(g.board))result.push('freeze');
  if(e.energy>=swapCost(e))for(let i=0;i<16;i++)for(let j=i+1;j<16;j++)if(g.board[i]&&g.board[j]&&g.board[i]!==g.board[j])result.push(`swap:${i}:${j}`);
  return result;
}
function refresh(g){const e=g.extra;if(g.mode!=='expedition'||e.phase!=='play')return;
  if(g.score-e.stage_score>=STAGES[e.stage][1]){e.cleared=e.stage+1;e.phase=e.stage===5?'won':'clear';if(e.phase==='clear'){const pool=Object.keys(ABILITIES).filter(k=>(e.perks[k]||0)<2),r=new Random(BigInt(e.seed)+BigInt(e.stage+1)*0x9e3779b9n);for(let i=pool.length-1;i>0;i--){let j=r.choice(i+1);[pool[i],pool[j]]=[pool[j],pool[i]];}e.offers=pool.slice(0,3);}}
  else if(!remaining(g)||(!canMove(g.board)&&!powers(g).length))e.phase='lost';
}
export function status(g){
  if(g.mode==='expedition')return g.extra.phase;
  if(g.mode==='puzzle'&&Math.max(...g.board)>=g.extra.level.target)return 'won';
  if(g.mode==='rescue'&&empty(g.board)>=g.extra.goal)return 'won';
  if(!remaining(g)||!canMove(g.board))return 'lost';return 'play';
}
export function snapshot(g){return {board:g.board.slice(),rng:clone(g.rng),score:g.score,moves:g.moves,extra:clone(g.extra),aiMoves:g.aiMoves};}
function pushHistory(g){g.history.push(snapshot(g));if(g.history.length>100)g.history.shift();g.future=[];}
export function newGame(mode='classic',seed=Date.now(),data=null){
  if(!['classic','daily','sprint','puzzle','expedition','rescue'].includes(mode))throw new Error('Invalid mode');
  const rng=new Random(seed),g={id:`${Date.now()}-${Math.random().toString(36).slice(2)}`,mode,board:Array(16).fill(0),score:0,moves:0,aiMoves:0,undos:0,assisted:false,history:[],future:[],extra:{},rng:null};
  if(mode==='puzzle'){g.board=data.board.slice();g.extra={level:clone(data)};}
  else if(mode==='rescue'){g.board=data.origin.board.slice();g.extra={challenge:data.id,goal:data.goal,limit:data.limit,par:data.par};g.rng=clone(data.origin.rng);}
  else {spawn(g.board,rng,mode);spawn(g.board,rng,mode);}
  g.rng||=rng.state();
  if(mode==='expedition')g.extra={seed:String(seed),stage:0,phase:'draft',perks:{},offers:['combo','battery','gambit'],stage_score:0,stage_start:0,energy:0,streak:0,freeze:0,cooldown:0,cleared:0};
  if(mode==='daily')g.extra.date=data;
  return g;
}
export function choose(g,key){const e=g.extra;if(g.mode!=='expedition'||!['draft','clear'].includes(e.phase)||!e.offers.includes(key))return false;
  if(e.phase==='clear'){e.stage++;e.stage_score=g.score;e.stage_start=g.moves;const ids=g.board.map((v,i)=>v?i:-1).filter(i=>i>=0);if(ids.length>1){ids.sort((a,b)=>g.board[a]-g.board[b]||a-b);g.board[ids[0]]=0;}}
  e.perks[key]=(e.perks[key]||0)+1;e.phase='play';e.offers=[];e.freeze=0;e.cooldown=0;e.streak=0;g.history=[];g.future=[];refresh(g);return true;
}
export function move(g,direction,assisted=false){
  if(status(g)!=='play')return null;
  if(direction==='freeze'||direction.startsWith('swap:')){
    if(!powers(g).includes(direction))return null;pushHistory(g);const tracks=g.board.map((value,i)=>({source:i,target:i,value})).filter(t=>t.value);
    if(direction==='freeze'){g.extra.energy-=5;g.extra.freeze=2+(g.extra.perks.ice||0);g.extra.cooldown=6;}
    else {const [,a,b]=direction.split(':').map(Number);[g.board[a],g.board[b]]=[g.board[b],g.board[a]];for(const t of tracks){if(t.source===a)t.target=b;else if(t.source===b)t.target=a;}g.extra.energy-=swapCost(g.extra);}
    g.assisted||=assisted;g.aiMoves+=+assisted;refresh(g);return {tracks,merges:[],gain:0,spawn:null,board:g.board};
  }
  const result=slide(g.board,direction);if(!result.changed)return null;
  pushHistory(g);let skip=false;g.board=result.board;
  if(g.mode==='expedition'){const r=reward(g.board,result.gain,result.merges,g.extra);result.gain=r.points;skip=r.skip;g.extra=r.extra;}
  const rng=new Random(0,g.rng);result.spawn=skip?null:spawn(g.board,rng,g.mode,fourProbability(g.extra));g.rng=rng.state();
  g.score+=result.gain;g.moves++;g.assisted||=assisted;g.aiMoves+=+assisted;refresh(g);return result;
}
export function undo(g){if(!g.history.length)return false;g.future.push(snapshot(g));Object.assign(g,g.history.pop());g.undos++;return true;}
export function redo(g){if(!g.future.length)return false;g.history.push(snapshot(g));Object.assign(g,g.future.pop());return true;}
export async function dailySeed(date){const raw=new TextEncoder().encode(`2048-Atelier/daily/v1/${date}`),hash=new Uint8Array(await crypto.subtle.digest('SHA-256',raw));return hash.slice(0,8).reduce((n,v)=>(n<<8n)+BigInt(v),0n);}
export function validateGame(g){
  if(!g||!validBoard(g.board)||!['classic','daily','sprint','puzzle','expedition','rescue'].includes(g.mode))return false;
  const validFrame=f=>f&&validBoard(f.board)&&validRng(f.rng)&&['moves','score','aiMoves'].every(k=>Number.isSafeInteger(f[k])&&f[k]>=0)&&validExtra(g.mode,f.extra);
  if(typeof g.id!=='string'||g.id.length>100||typeof g.assisted!=='boolean'||!Number.isSafeInteger(g.undos)||g.undos<0)return false;
  if(!validFrame(g)||!Array.isArray(g.history)||!Array.isArray(g.future)||g.history.length+g.future.length>100||![...g.history,...g.future].every(validFrame))return false;
  return true;
}
function validExtra(mode,e){if(!e||typeof e!=='object'||Array.isArray(e))return false;
  const int=(v,min,max)=>Number.isSafeInteger(v)&&v>=min&&v<=max;
  if(mode==='expedition'){
    if(!int(e.stage,0,5)||!['draft','play','clear','won','lost'].includes(e.phase)||!e.perks||typeof e.perks!=='object'||Array.isArray(e.perks)||Object.entries(e.perks).some(([k,v])=>!Object.hasOwn(ABILITIES,k)||![1,2].includes(v))||!Array.isArray(e.offers)||e.offers.length>3||new Set(e.offers).size!==e.offers.length||e.offers.some(k=>!Object.hasOwn(ABILITIES,k)||(e.perks[k]||0)>=2))return false;
    if(['draft','clear'].includes(e.phase)&&e.offers.length!==3)return false;
    if(!/^\d{1,16}$/.test(String(e.seed))||BigInt(e.seed)>9007199254740992n)return false;
    return Object.entries({energy:12,streak:1e6,freeze:4,cooldown:6,cleared:6,stage_score:Number.MAX_SAFE_INTEGER,stage_start:1e9}).every(([k,max])=>int(e[k],0,max));
  }
  if(mode==='puzzle'){const l=e.level;return l&&validBoard(l.board)&&int(l.id,0,11)&&int(l.seed,0,Number.MAX_SAFE_INTEGER)&&int(l.target,2,65536)&&Number.isInteger(Math.log2(l.target))&&int(l.par,1,7)&&int(l.limit,l.par,7)&&typeof l.title==='string'&&l.title.length<=30;}
  if(mode==='rescue')return int(e.goal,2,5)&&int(e.limit,1,7)&&int(e.par,1,e.limit)&&typeof e.challenge==='string'&&e.challenge.length<=120;
  if(mode==='daily')return typeof e.date==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(e.date)&&!Number.isNaN(Date.parse(e.date));
  return true;
}
export function validChallenge(c){try{
  if(!c||typeof c.id!=='string'||c.id.length>120||typeof c.title!=='string'||c.title.length>40||!validBoard(c.origin?.board)||!validRng(c.origin?.rng)||!Number.isInteger(c.goal)||c.goal<2||c.goal>5||!Number.isInteger(c.limit)||c.limit<1||c.limit>7||!Number.isInteger(c.par)||!Array.isArray(c.solution)||c.solution.length!==c.par||c.par<1||c.par>c.limit||c.solution.some(d=>!DIRS.includes(d)))return false;
  if(!Number.isInteger(c.rewind)||c.rewind<1||c.rewind>10||!['source_score','source_moves'].every(k=>Number.isSafeInteger(c[k])&&c[k]>=0)||!Array.isArray(c.original)||c.original.length>10||c.original.some(f=>!validBoard(f.board)||(f.direction!==null&&!DIRS.includes(f.direction))))return false;
  const g=newGame('rescue',0,c);if(empty(g.board)>=c.goal)return false;for(const d of c.solution)if(!move(g,d))return false;return status(g)==='won';
}catch{return false;}}
