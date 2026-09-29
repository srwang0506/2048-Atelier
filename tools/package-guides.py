"""Create docs-only and Windows-with-docs archives; preserve original runtime bytes."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,os,copy
root=Path(__file__).resolve().parents[1]
original=Path(os.environ.get('WINDOWS_ZIP',root/'releases/2048-v12-Windows-x64.zip'))
out=Path(os.environ.get('PACKAGE_OUT',root.parent/'outputs'));out.mkdir(exist_ok=True)
win=out/'2048-v12-Windows-x64-with-docs.zip';doc=out/'LUMINA-All-Platforms-Documentation-ZH-EN-JA-20260929.zip'
prefix='2048-Windows/'
# Limit packaging to documentation, even when run from a full installed game tree.
known_tools=['README.md','build-docs.mjs','build-media.py','capture-desktop.py','write-guide.py','validate-docs.py','package-guides.py']
candidates=[*root.glob('README*.md'),root/'START-HERE.txt',*(root/'tools'/n for n in known_tools)]
for folder in ['docs','reference']:candidates.extend((root/folder).rglob('*'))
files=sorted(p for p in candidates if p.is_file() and not p.name.startswith('._') and '__pycache__' not in p.parts and p.name not in ('package-validation.json','release-manifest.json','package-build.log','delivered-files.json'))
new={prefix+p.relative_to(root).as_posix():p.read_bytes() for p in files}
with ZipFile(original) as old:
 assert old.testzip() is None
 collisions=set(old.namelist()) & new.keys()
 assert collisions=={prefix+'README.md'},collisions
 report=dict(original_windows_zip_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),original_entries=len(old.namelist()),updated_original_entries=sorted(collisions),retained_original_entries=len(old.namelist())-len(collisions),new_documentation_entries=len(new)-len(collisions),all_retained_original_bytes_match=False,zip_crc_pass=False)
 with ZipFile(win,'w',ZIP_DEFLATED,compresslevel=6) as z:
  for info in old.infolist():
   if info.filename not in collisions:z.writestr(copy.copy(info),old.read(info.filename))
  for name,data in new.items():z.writestr(name,data)
 with ZipFile(win) as z:
  assert len(z.namelist())==len(set(z.namelist()))
  assert z.testzip() is None
  for info in old.infolist():
   if info.filename not in collisions:assert old.read(info.filename)==z.read(info.filename),info.filename
  for name,data in new.items():assert z.read(name)==data,name
report.update(all_retained_original_bytes_match=True,zip_crc_pass=True)
(root/'package-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with ZipFile(win,'a',ZIP_DEFLATED) as z:z.write(root/'package-validation.json',prefix+'package-validation.json')
with ZipFile(doc,'w',ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[root/'package-validation.json']:z.write(p,'LUMINA-All-Platforms-Documentation/'+p.relative_to(root).as_posix())
for p in [win,doc]:
 with ZipFile(p) as z:assert z.testzip() is None
manifest={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [win,doc]}
(out/'LUMINA-All-Platforms-20260929-SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(validation=report,archives=manifest),ensure_ascii=False,indent=2))
