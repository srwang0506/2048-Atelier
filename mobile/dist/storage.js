import {validateGame,validChallenge,clone} from './engine.js';
export const sessionKey=g=>g.mode==='daily'?`daily:${g.extra.date}`:g.mode;
const DB_NAME='lumina-2048-touch-v1';
export const defaults=()=>({settings:{sound:false,motion:true,theme:'light',strength:'balanced',pace:'calm'},best:{},stars:{},records:[],rescues:[]});
export function validMeta(m){return !!m&&m.settings&&['sound','motion'].every(k=>typeof m.settings[k]==='boolean')&&['light','dark','system'].includes(m.settings.theme)&&['quick','balanced','deep'].includes(m.settings.strength)&&['calm','quick'].includes(m.settings.pace)&&m.best&&typeof m.best==='object'&&Object.keys(m.best).length<=100&&Object.values(m.best).every(v=>Number.isSafeInteger(v)&&v>=0)&&m.stars&&typeof m.stars==='object'&&Object.entries(m.stars).every(([k,v])=>/^\d{1,2}$/.test(k)&&Number(k)<12&&[0,1,2,3].includes(v))&&Array.isArray(m.records)&&m.records.length<=100&&m.records.every(r=>r&&typeof r.id==='string'&&typeof r.date==='string'&&['classic','daily','puzzle','sprint','expedition','rescue'].includes(r.mode)&&['score','moves','tile'].every(k=>Number.isSafeInteger(r[k])&&r[k]>=0)&&typeof r.assisted==='boolean')&&Array.isArray(m.rescues)&&m.rescues.length<=6&&m.rescues.every(validChallenge);}
export class Storage {
  constructor(report){this.db=null;this.report=report;this.meta=defaults();this.sessions={};this.pending=Promise.resolve();this.updated=0;this.revisions={};this.practiceIDs=[];}
  async open(){
    try{this.db=await new Promise((resolve,reject)=>{const req=indexedDB.open(DB_NAME,1);req.onupgradeneeded=()=>req.result.createObjectStore('data');req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);req.onblocked=()=>reject(new Error('存档被其他窗口占用'));});
      const items=await new Promise((resolve,reject)=>{const tx=this.db.transaction('data'),s=tx.objectStore('data'),rows={};s.openCursor().onsuccess=e=>{const c=e.target.result;if(c){rows[c.key]=c.value;c.continue();}};tx.oncomplete=()=>resolve(rows);tx.onerror=()=>reject(tx.error);});
      if(validMeta(items.meta?.value))this.meta=items.meta.value;
      for(const [key,row] of Object.entries(items)){if(!key.startsWith('game:'))continue;const name=key.slice(5);if(validateGame(row.value)&&sessionKey(row.value)===name){this.sessions[name]=row.value;this.revisions[name]=row.revision||0;}else if(validateGame(items[`backup:${name}`]?.value)){this.sessions[name]=items[`backup:${name}`].value;this.report('已从备用存档恢复这一局');}}
      this.report(null);
    }catch(e){this.report('无法使用自动存档，请导出备份后再离开');}
    try{const emergency=JSON.parse(localStorage.getItem('lumina-emergency'));if(emergency&&validateGame(emergency.game)&&emergency.time>(this.revisions[sessionKey(emergency.game)]||0)){const key=sessionKey(emergency.game),previous=this.sessions[key];if(!previous||previous.id!==emergency.game.id||previous.moves!==emergency.game.moves||previous.score!==emergency.game.score||JSON.stringify(previous.extra)!==JSON.stringify(emergency.game.extra)||previous.board.some((v,i)=>v!==emergency.game.board[i]))this.sessions[key]=emergency.game;else{previous.assisted||=emergency.game.assisted;previous.undos=Math.max(previous.undos,emergency.game.undos);}}}catch{}
    return this;
  }
  emergency(g){try{localStorage.setItem('lumina-emergency',JSON.stringify({time:Date.now(),game:{...g,history:[],future:[]}}));}catch{}}
  save(g){const key=sessionKey(g),value=clone(g),revision=Date.now(),previous=this.sessions[key];this.sessions[key]=value;this.emergency(value);
    const days=Object.keys(this.sessions).filter(k=>k.startsWith('daily:')).sort().reverse();const obsolete=days.slice(7);obsolete.forEach(k=>delete this.sessions[k]);
    const keep=days.slice(0,7);for(const k of Object.keys(this.meta.best))if(k.startsWith('daily:')&&!keep.some(d=>k.startsWith(d+':')))delete this.meta.best[k];const meta=clone(this.meta);
    this.pending=this.pending.catch(()=>{}).then(()=>new Promise((resolve,reject)=>{
      if(!this.db){resolve();return;}const tx=this.db.transaction('data','readwrite'),s=tx.objectStore('data');
      s.put({value,revision},`game:${key}`);if(previous)s.put({value:previous,revision:this.revisions[key]||0},`backup:${key}`);s.put({value:meta,revision},'meta');for(const k of obsolete){s.delete(`game:${k}`);s.delete(`backup:${k}`);}
      tx.oncomplete=()=>{this.revisions[key]=revision;this.report(null);resolve();};tx.onerror=()=>{this.report('存档空间不足或被禁用，请导出备份');reject(tx.error);};
    }));return this.pending.catch(()=>{});
  }
  export(){return JSON.stringify({format:'lumina-touch',version:1,exported:new Date().toISOString(),meta:this.meta,sessions:this.sessions});}
  async import(text){if(text.length>20000000)throw new Error('备份文件过大');const data=JSON.parse(text);if(data.format!=='lumina-touch'||data.version!==1||!data.sessions||!data.meta)throw new Error('请选择 LUMINA 触屏版备份');
    if(Object.keys(data.sessions).length>12||Object.entries(data.sessions).some(([key,g])=>!validateGame(g)||sessionKey(g)!==key))throw new Error('备份中有无法读取的棋盘');
    const m=data.meta;if(!validMeta(m))throw new Error('备份数据不完整');
    if(data.sessions.rescue&&!m.rescues.some(c=>c.id===data.sessions.rescue.extra.challenge)&&!this.practiceIDs.includes(data.sessions.rescue.extra.challenge))throw new Error('重生挑战缺少原局');
    if(!this.db)throw new Error('浏览器存储不可用，暂时不能导入');
    await this.pending;await new Promise((resolve,reject)=>{const tx=this.db.transaction('data','readwrite'),s=tx.objectStore('data');s.clear();for(const [key,value] of Object.entries(data.sessions))s.put({value,revision:Date.now()},`game:${key}`);s.put({value:m,revision:Date.now()},'meta');tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});
    this.sessions=data.sessions;this.meta={...defaults(),...m,settings:{...defaults().settings,...m.settings}};try{localStorage.removeItem('lumina-emergency');}catch{}
  }
}
