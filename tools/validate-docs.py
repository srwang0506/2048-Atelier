#!/usr/bin/env python3
"""Validate the standalone guide tree; no browser or network required."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re
root=Path(__file__).resolve().parents[1];issues=[];checked=0
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.gifs=[];self.lang=None;self.chapters=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='html':self.lang=d.get('lang')
  for attr in ['href','src','data-gif','data-poster']:
   if attr in d:self.refs.append(d[attr])
  if tag=='img' and 'data-gif' in d:self.gifs.append(d)
  if tag=='article':self.chapters.append(d.get('data-chapter'))
pages={}
for p in (root/'docs').rglob('*.html'):
 if p.name.startswith('._'):continue
 page=Page();page.feed(p.read_text(encoding='utf-8'));pages[p.resolve()]=page
 if len(page.ids)!=len(set(page.ids)):issues.append(f'{p}: duplicate IDs')
def check(source,ref):
 global checked
 u=urlsplit(ref)
 if u.scheme or u.netloc:return
 checked+=1;target=(source.parent/unquote(u.path)).resolve() if u.path else source.resolve()
 if not target.exists():issues.append(f'{source.relative_to(root)}: missing {ref}');return
 if u.fragment and target.suffix=='.html' and unquote(u.fragment) not in pages[target].ids:issues.append(f'{source.relative_to(root)}: missing anchor {ref}')
for p in [*root.glob('README*.md'),*(root/'docs').rglob('*.md'),*(root/'reference').glob('*.md')]:
 if p.name.startswith('._'):continue
 for ref in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):check(p,ref)
for p,page in pages.items():
 for ref in page.refs:check(p,ref)
 if p.parent.name in ['zh-CN','en','ja']:
  n=9 if 'native' in p.relative_to(root).parts else 12
  if len(page.chapters)!=n:issues.append(f'{p}: wrong chapter count')
  if len(page.gifs)!=(9 if n==9 else 17):issues.append(f'{p}: wrong playable GIF count')
  if page.lang!=p.parent.name:issues.append(f'{p}: wrong language')
levels=json.loads((root/'reference/puzzle-levels.json').read_text(encoding='utf-8'));practices=json.loads((root/'reference/rescue-practice.json').read_text(encoding='utf-8'))
arrows={'left':'←','up':'↑','right':'→','down':'↓'}
for lang in ['zh-CN','en','ja']:
 if len(list((root/'docs'/lang).glob('[0-9][0-9]-*.md')))!=12:issues.append(f'{lang}: wrong chapters')
 for path in [root/'docs'/lang/'11-solutions.md',root/'docs/native/docs'/lang/'08-solutions.md']:
  txt=path.read_text(encoding='utf-8');routes=re.findall(r'(?:路线|Route|ルート): \*\*([^*]+)\*\*',txt)
  if len(routes)!=12:issues.append(f'{path}: missing puzzle route')
  for level,route in zip(levels,routes):
   if ''.join(route.split())!=''.join(arrows[d] for d in level['solution']):issues.append(f'{path}: wrong route {level["id"]}')
  practice_routes=re.findall(r'\*\*([←↑→↓ ]+)\*\*',txt)[-3:]
  if len(practice_routes)!=3:issues.append(f'{path}: missing practice routes')
  for practice,route in zip(practices,practice_routes):
   if ''.join(route.split())!=''.join(arrows[d] for d in practice['solution']):issues.append(f'{path}: wrong practice route')
 if not (root/f'README.{lang}.md').exists():issues.append(f'{lang}: README missing')
media=0;frames=0
for folder,want in [(root/'docs/media',8),(root/'docs/native/docs/media',9)]:
 manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
 assert len(manifest)==want
 for clip in manifest:
  media+=1;frames+=clip['frames']
  for name,info in clip['files'].items():
   p=folder/name
   if hashlib.sha256(p.read_bytes()).hexdigest()!=info['sha256'] or p.stat().st_size!=info['bytes']:issues.append(f'{name}: hash/size mismatch')
  if (folder/(clip['name']+'.mp4')).read_bytes()[4:8]!=b'ftyp':issues.append(f'{clip["name"]}: MP4 header')
  if clip['decoded_video_frames']!=clip['frames']:issues.append(f'{clip["name"]}: frame count')
  if abs(clip['duration']-clip['gif_duration_ms']/1000)>=.1 or clip['gif_frames']<2:issues.append(f'{clip["name"]}: GIF duration/animation')
if issues:print('\n'.join(issues));raise SystemExit(1)
print(f'PASS: 3 × 12 unified chapters + 3 × 9 preserved native chapters = 63; 4 root READMEs; {checked} local references/anchors; 72 translated puzzle routes + 18 practice-route occurrences; {media} GIF/MP4/poster sets; {frames} decoded video frames.')
print('Offline HTML browser visual/interaction acceptance is not completed; structural checks do not replace it.')
