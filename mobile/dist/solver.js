import {DIRS,Random,slide,spawn,canMove,empty,clone,reward,powers,swapCost,fourProbability,STAGES,remaining} from './engine.js';
const now=()=>performance.now();
// Exact search carries the complete random state down each branch. No sampled spawns.
export function exact(g,budget=1800){
  const start=now(),deadline=start+budget,goal=b=>g.mode==='puzzle'?Math.max(...b)>=g.extra.level.target:empty(b)>=g.extra.goal&&canMove(b);
  const limit=remaining(g);if(goal(g.board))return {direction:null,solution:[],complete:true,solvable:true,nodes:0,depth:0,ms:0,kind:'exact'};
  let queue=[{board:g.board,rng:g.rng,path:[]}],head=0,nodes=0,complete=true;
  while(head<queue.length){const current=queue[head++];nodes++;if(nodes%32===0&&now()>deadline){complete=false;break;}if(current.path.length>=limit)continue;
    for(const d of DIRS){const s=slide(current.board,d);if(!s.changed)continue;const rng=new Random(0,current.rng);spawn(s.board,rng,g.mode);const path=[...current.path,d];
      if(goal(s.board))return {direction:path[0],solution:path,complete:true,solvable:true,nodes,depth:path.length,ms:Math.round(now()-start),kind:'exact'};
      if(path.length<limit&&canMove(s.board))queue.push({board:s.board,rng:rng.state(),path});
    }
  }
  return {direction:null,solution:[],complete,solvable:false,nodes,depth:limit,ms:Math.round(now()-start),kind:'exact'};
}
export function extractRescue(failed,budget=2800){
  if(!['classic','daily','sprint'].includes(failed.mode)||canMove(failed.board))return {status:'ineligible'};
  const start=now(),history=failed.history;let incomplete=false;
  for(let distance=1;distance<=Math.min(10,history.length);distance++){
    const origin=history[history.length-distance];if(empty(origin.board)>1)continue;
    const left=budget-(now()-start);if(left<=0){incomplete=true;break;}
    const candidate={mode:'rescue',board:origin.board,rng:origin.rng,moves:0,extra:{goal:3,limit:6}};
    const result=exact(candidate,left);if(!result.complete){incomplete=true;break;}if(!result.solvable)continue;
    // Verify the witness with precisely the production spawn order before returning it.
    let b=origin.board.slice(),rng=new Random(0,origin.rng);
    for(const d of result.solution){const s=slide(b,d);if(!s.changed)throw new Error('Invalid rescue witness');b=s.board;spawn(b,rng);}
    if(empty(b)<3||!canMove(b))throw new Error('Invalid rescue objective');
    const frames=[...history.slice(history.length-distance),failed],original=[];
    for(let i=0;i<frames.length-1;i++){
      let direction=null;for(const d of DIRS){const s=slide(frames[i].board,d);if(!s.changed)continue;spawn(s.board,new Random(0,frames[i].rng));if(s.board.every((v,j)=>v===frames[i+1].board[j])){direction=d;break;}}
      original.push({board:frames[i+1].board.slice(),direction});
    }
    return {status:'found',challenge:{id:`rescue-${failed.id}-${origin.moves}`,title:'我的转机',origin:{board:origin.board.slice(),rng:clone(origin.rng)},goal:3,limit:6,par:result.solution.length,solution:result.solution,original,source_score:failed.score,source_moves:origin.moves,rewind:distance,practice:false}};
  }
  return {status:incomplete?'timeout':'not_found'};
}

// Row tables evaluate all ordinary 16-bit rows. Wider tiles use the same formula directly.
const rowScore=new Float64Array(65536),rowLeft=new Uint32Array(65536),rowRight=new Uint32Array(65536),rowGain=new Float64Array(65536);
let ready=false;
function evaluateRow(a){let inc=0,dec=0,smooth=0,merges=0,zeros=0;const nz=[];
  for(let i=0;i<4;i++){if(!a[i])zeros++;else nz.push(a[i]);if(i<3){const d=a[i]**3.5-a[i+1]**3.5;inc+=Math.max(0,d);dec+=Math.max(0,-d);if(a[i]&&a[i+1])smooth+=Math.abs(a[i]-a[i+1]);}}
  for(let i=0;i<nz.length-1;i++)if(nz[i]===nz[i+1]){merges++;i++;}
  return zeros*270+merges*200-Math.min(inc,dec)*11-smooth*8;
}
function compact(a){const nz=a.filter(Boolean),out=[];let gain=0;for(let i=0;i<nz.length;i++){let v=nz[i];if(nz[i+1]===v){v++;i++;gain+=2**v;}out.push(v);}while(out.length<4)out.push(0);return {out,gain};}
function initTables(){if(ready)return;for(let code=0;code<65536;code++){const a=[code&15,(code>>>4)&15,(code>>>8)&15,code>>>12];rowScore[code]=evaluateRow(a);const l=compact(a),r=compact([...a].reverse());rowGain[code]=l.gain;rowLeft[code]=l.out.some(v=>v>15)?65536:l.out.reduce((n,v,i)=>n|(v<<(4*i)),0);rowRight[code]=r.out.some(v=>v>15)?65536:r.out.reverse().reduce((n,v,i)=>n|(v<<(4*i)),0);}ready=true;}
function shift(b,d){const out=Array(16).fill(0);let changed=false,gain=0;
  for(let line=0;line<4;line++){const ids=[0,1,2,3].map(c=>(d===0||d===2)?line*4+c:c*4+line),a=ids.map(i=>b[i]),reverse=d===2||d===3;
    let code=a.reduce((n,v,i)=>n|(v<<(4*i)),0),result=a.every(v=>v<16)?(reverse?rowRight[code]:rowLeft[code]):65536;
    if(result===65536){const r=compact(reverse?[...a].reverse():a);gain+=r.gain;const values=reverse?r.out.reverse():r.out;ids.forEach((id,i)=>{out[id]=values[i];changed||=out[id]!==b[id];});}
    else{gain+=rowGain[code];ids.forEach((id,i)=>{out[id]=(result>>>(4*i))&15;changed||=out[id]!==b[id];});}
  }return {board:out,gain,changed};
}
function evaluate(b){let value=0;
  for(let r=0;r<4;r++){const row=b.slice(r*4,r*4+4),col=[b[r],b[r+4],b[r+8],b[r+12]];for(const a of [row,col])value+=a.every(v=>v<16)?rowScore[a[0]|a[1]<<4|a[2]<<8|a[3]<<12]:evaluateRow(a);}
  const max=Math.max(...b),corner=Math.max(b[0],b[3],b[12],b[15])===max;return value+(corner?max*max*14:-max*max*20);
}
export function heuristic(board){initTables();return evaluate(board.map(v=>v?Math.log2(v):0));}
export function search(g,budget=160){
  initTables();const start=now(),deadline=start+Math.max(25,Math.min(1200,budget)),isExp=g.mode==='expedition',root=g.board.map(v=>v?Math.log2(v):0);let nodes=0,depthDone=0,cache=new Map();
  const check=()=>{if((++nodes&127)===0&&now()>deadline)throw new Error('deadline');};
  function player(b,depth,prob,e){check();if(depth<=0||prob<.00012)return evaluate(b)+(e?.energy||0)*24;
    const key=String.fromCharCode(...b)+':'+depth+(e?`:${e.streak}:${e.energy}:${e.freeze}:${e.cooldown}`:'');const found=cache.get(key);if(found!==undefined)return found;
    let best=-1e8;for(let d=0;d<4;d++){const r=shift(b,d);if(!r.changed)continue;let points=r.gain,skip=false,next=e;if(e){const original=b.map(v=>v?2**v:0),s=slide(original,DIRS[d]),rr=reward(s.board,s.gain,s.merges,e);points=rr.points;skip=rr.skip;next=rr.extra;}
      const value=points*.18+(skip?player(r.board,depth-1,prob,next):chance(r.board,depth-1,prob,next));best=Math.max(best,value);}
    if(best===-1e8&&e&&e.energy>=swapCost(e))best=-20000;
    if(cache.size<60000)cache.set(key,best);return best;
  }
  function chance(b,depth,prob,e){check();const cells=b.map((v,i)=>!v?i:-1).filter(i=>i>=0);if(!cells.length)return player(b,depth,prob,e);const four=e?fourProbability(e):.1;let value=0;
    for(const i of cells){const child=b.slice();child[i]=1;value+=(1-four)*player(child,depth,prob*(1-four)/cells.length,e);child[i]=2;value+=four*player(child,depth,prob*four/cells.length,e);}return value/cells.length;
  }
  const choices={},fallback={};
  for(let d=0;d<4;d++){const r=shift(root,d);if(!r.changed)continue;let points=r.gain,skip=false,e=isExp?g.extra:null;if(e){const s=slide(g.board,DIRS[d]),rr=reward(s.board,s.gain,s.merges,e);points=rr.points;skip=rr.skip;e=rr.extra;}
    choices[DIRS[d]]={board:r.board,points,skip,extra:e};fallback[DIRS[d]]=evaluate(r.board)+points*.18;}
  let values=fallback;
  try{for(let depth=1;depth<=7;depth++){let iteration={};cache=new Map();for(const [d,c] of Object.entries(choices))iteration[d]=c.points*.18+(c.skip?player(c.board,depth-1,1,c.extra):chance(c.board,depth-1,1,c.extra));values=iteration;depthDone=depth;if(now()>deadline||!Object.keys(choices).length)break;}}catch(e){if(e.message!=='deadline')throw e;}
  if(isExp){const needed=STAGES[g.extra.stage][1]-(g.score-g.extra.stage_score),finish=Object.entries(choices).filter(([,c])=>c.points>=needed);
    for(const [d,c] of Object.entries(choices)){if(c.points>=needed)values[d]+=1e7;else if(remaining(g)===1)values[d]-=1e7;}
    if(!finish.length){const available=powers(g),base=heuristic(g.board),ranked=[];
      for(const p of available)if(p.startsWith('swap:')){const [,a,b]=p.split(':').map(Number),board=g.board.slice();[board[a],board[b]]=[board[b],board[a]];const gain=heuristic(board)-base;if(!canMove(g.board)||gain>600)ranked.push({p,gain});}
      ranked.sort((a,b)=>b.gain-a.gain);if(ranked.length)values[ranked[0].p]=Math.max(-1e8,...Object.values(values))+Math.max(1,ranked[0].gain-500);
      else if(available.includes('freeze')&&empty(g.board)<=3)values.freeze=Math.max(-1e8,...Object.values(values))+1;
    }
  }
  const ranked=Object.entries(values).sort((a,b)=>b[1]-a[1]);return {direction:ranked[0]?.[0]||null,values:ranked,nodes,depth:depthDone,ms:Math.round(now()-start),kind:'expectimax'};
}
