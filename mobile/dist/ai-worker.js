import {search,exact,extractRescue} from './solver.js';
self.onmessage=({data:{id,task,game,budget}})=>{try{const result=task==='extract'?extractRescue(game,budget):['puzzle','rescue'].includes(game.mode)?exact(game,budget||1800):search(game,budget);self.postMessage({id,result});}catch(error){self.postMessage({id,error:error.message||'Search failed'});}};
