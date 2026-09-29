// The complete game is local. Never cache sign-in redirects or external responses.
const CACHE='lumina-touch-v1';
const FILES=['./','./index.html','./styles.css','./app.js','./engine.js','./solver.js','./ai-worker.js','./storage.js','./puzzle-levels.json','./rescue-practice.json','./manifest.webmanifest','./icon.svg','./icon-180.png','./icon-192.png','./icon-512.png'];
self.addEventListener('install',event=>event.waitUntil((async()=>{const cache=await caches.open(CACHE);for(const path of FILES){const r=await fetch(new Request(path,{cache:'reload',credentials:'same-origin'}));if(!r.ok||r.redirected||r.type==='opaque')throw new Error('Offline assets unavailable');await cache.put(path,r);}})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==self.location.origin)return;const relative='./'+url.pathname.slice(new URL(self.registration.scope).pathname.length);if(event.request.mode!=='navigate'&&!FILES.includes(relative))return;
  event.respondWith((async()=>{const cache=await caches.open(CACHE);const cached=await cache.match(event.request,{ignoreSearch:true});if(cached)return cached;if(event.request.mode==='navigate'){const shell=await cache.match('./index.html');if(shell)return shell;}return fetch(event.request);})());
});
