#!/usr/bin/env python3
"""Validate translated documentation, local links, solution routes and media hashes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re,struct
root=Path(__file__).resolve().parents[1]
issues=[]; checked=0
class Page(HTMLParser):
 def __init__(self): super().__init__(); self.ids=[]; self.refs=[]; self.gifs=[]; self.lang=None
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='html':self.lang=d.get('lang')
  for attr in ['href','src','data-gif','data-poster']:
   if attr in d:self.refs.append(d[attr])
  if tag=='img' and 'data-gif' in d:self.gifs.append(d)

def check_ref(source,ref):
 global checked
 u=urlsplit(ref)
 if u.scheme or u.netloc:return
 checked+=1
 target=(source.parent/unquote(u.path)).resolve() if u.path else source
 if not target.exists():issues.append(f'{source.relative_to(root)}: missing {ref}');return
 if u.fragment and target.suffix=='.html':
  p=Page();p.feed(target.read_text())
  if unquote(u.fragment) not in p.ids:issues.append(f'{source.relative_to(root)}: missing anchor {ref}')
files=list((root/'docs').rglob('*.md'))+list(root.glob('README*.md'))+[root/'QA.md',root/'BUGFIXES-1.0.1.md']
for p in files:
 text=p.read_text()
 for ref in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):check_ref(p,ref)
 for token in ['TODO','TBD','lorem ipsum']:
  if token.lower() in text.lower():issues.append(f'{p}: placeholder {token}')
for p in (root/'docs').rglob('*.html'):
 page=Page();page.feed(p.read_text())
 if len(page.ids)!=len(set(page.ids)):issues.append(f'{p}: duplicate heading IDs')
 for ref in page.refs:check_ref(p,ref)
 if p.parent.name in ['zh-CN','en','ja']:
  if len(page.gifs)!=9:issues.append(f'{p}: expected 9 playable GIFs')
  if page.lang!=p.parent.name:issues.append(f'{p}: wrong language')
levels=json.loads((root/'Sources/LuminaCore/Resources/puzzle-levels.json').read_text())
arrows={'left':'←','up':'↑','right':'→','down':'↓'}
for lang in ['zh-CN','en','ja']:
 chapters=list((root/'docs'/lang).glob('[0-9][0-9]-*.md'))
 if len(chapters)!=9:issues.append(f'{lang}: expected 9 chapters')
 solution=(root/'docs'/lang/'08-solutions.md').read_text()
 routes=re.findall(r'(?:路线|Route|ルート): \*\*([^*]+)\*\*',solution)
 if len(routes)!=12:issues.append(f'{lang}: expected 12 puzzle routes')
 for level,route in zip(levels,routes):
  if ''.join(route.split())!=''.join(arrows[d] for d in level['solution']):issues.append(f'{lang}: incorrect route {level["id"]}')
 if not (root/f'README.{lang}.md').exists():issues.append(f'{lang}: README missing')
manifest=json.loads((root/'docs/media/manifest.json').read_text())
assert len(manifest)==9
for clip in manifest:
 for name,info in clip['files'].items():
  p=root/'docs/media'/name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=info['sha256']:issues.append(f'{name}: SHA-256 mismatch')
  if p.stat().st_size!=info['bytes']:issues.append(f'{name}: size mismatch')
 video=root/'docs/media'/(clip['name']+'.mp4');data=video.read_bytes()
 if data[4:8]!=b'ftyp':issues.append(f'{video}: missing MP4 file type header')
 if clip['decoded_video_frames']!=clip['frames']:issues.append(f'{video}: decoded frame count mismatch')
 if abs(clip['duration']-clip['gif_duration_ms']/1000)>0.1:issues.append(f'{video}: GIF duration drift')
 if clip['gif_frames']<2:issues.append(f'{video}: static GIF')
if issues:
 print('\n'.join(issues));raise SystemExit(1)
print(f'PASS: 3 languages × 9 chapters; 3 localized READMEs + Chinese default; {checked} local links/anchors; 36 translated puzzle routes; 9 GIFs + 9 MP4s + 9 posters with SHA-256 verification.')
print('Browser visual QA was blocked by local-file URL security policy; this validator does not replace it.')
