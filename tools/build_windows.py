"""Assemble a relocatable Windows x64 application from verified vendor wheels.

Run on any host; execution testing still needs Windows. The input directory
contains windows-dependencies.json, windows-wheels/, the official Python ZIP
and its release page. No installer, registry edits or system Python is used.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import struct
import tempfile
import zipfile

FILES='''game.py desktop_start.py platform_paths.py check_runtime.py air_ui.py ui_core.py interface_base.py motion.py persistence.py clear_material.py prism.py engine.py ai.py ai_legacy.py search_native.py features.py modes.py insight.py journey.py puzzles.py puzzle_levels.json typography.py expedition.py rescue.py adventures.py rescue_practice.json requirements.txt README.md 测试报告.md 启动游戏.bat check-windows.bat Windows使用说明.txt THIRD_PARTY.md'''.split()
PYTHON='3.13.15'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def pe_details(data):
    offset=struct.unpack_from('<I',data,0x3c)[0]
    if data[offset:offset+4]!=b'PE\0\0':raise ValueError('Not a PE binary')
    machine,sections=struct.unpack_from('<HH',data,offset+4)
    optional=offset+24;size=struct.unpack_from('<H',data,offset+20)[0]
    magic=struct.unpack_from('<H',data,optional)[0]
    directory=optional+(112 if magic==0x20b else 96)
    spans=[]
    for i in range(sections):
        section=optional+size+i*40
        virtual_size,rva,raw_size,raw=struct.unpack_from('<IIII',data,section+8)
        spans.append((rva,max(virtual_size,raw_size),raw))
    def file_offset(rva):
        return next(raw+rva-start for start,length,raw in spans if start<=rva<start+length)
    def name(rva):
        pos=file_offset(rva);return data[pos:data.index(b'\0',pos)].decode('ascii')
    imports=[];symbols={};exports=set()
    export_table=struct.unpack_from('<I',data,directory)[0]
    if export_table:
        pos=file_offset(export_table)
        count=struct.unpack_from('<I',data,pos+24)[0]
        names=struct.unpack_from('<I',data,pos+32)[0]
        if count:
            start=file_offset(names)
            exports={name(struct.unpack_from('<I',data,start+i*4)[0]) for i in range(count)}
    table=struct.unpack_from('<I',data,directory+8)[0]
    if table:
        pos=file_offset(table)
        while any(data[pos:pos+20]):
            dll=name(struct.unpack_from('<I',data,pos+12)[0]).lower();imports.append(dll)
            thunk=struct.unpack_from('<I',data,pos)[0] or struct.unpack_from('<I',data,pos+16)[0]
            if thunk:
                cursor=file_offset(thunk);width=8 if magic==0x20b else 4;fmt='<Q' if width==8 else '<I'
                while True:
                    address=struct.unpack_from(fmt,data,cursor)[0]
                    if not address:break
                    if not address & (1<<(width*8-1)):symbols.setdefault(dll,set()).add(name(address+2))
                    cursor+=width
            pos+=20
    return machine,imports,symbols,exports

def assemble(source,downloads,target):
    package=target/'2048-Windows';package.mkdir(parents=True)
    runtime=package/'runtime';runtime.mkdir()
    archive=downloads/f'python-{PYTHON}-embed-amd64.zip'
    html=(downloads/'python-release.html').read_text(encoding='utf-8')
    row=next(row for row in html.split('<tr>') if archive.name+'"' in row)
    expected=''.join(re.findall(r'[0-9a-f]{16}',row[row.index('class="checksum"'):]))
    assert len(expected)==64 and sha(archive)==expected,'Python checksum mismatch'
    with zipfile.ZipFile(archive) as z:z.extractall(runtime)
    (runtime/'python313._pth').write_text('python313.zip\n.\nLib/site-packages\n..\nimport site\n',encoding='ascii')
    site=runtime/'Lib/site-packages';site.mkdir(parents=True)
    dependencies=json.loads((downloads/'windows-dependencies.json').read_text(encoding='utf-8'))
    launcher=None;licenses=package/'licenses';licenses.mkdir()
    for row in dependencies:
        wheel=downloads/'windows-wheels'/row['file']
        assert sha(wheel)==row['sha256'], 'Wheel checksum mismatch: '+wheel.name
        with zipfile.ZipFile(wheel) as z:
            if row['package']=='distlib':
                launcher=z.read('distlib/w64.exe')
                license=next(n for n in z.namelist() if n.endswith('.dist-info/LICENSE.txt'))
                (licenses/'distlib-LICENSE.txt').write_bytes(z.read(license));continue
            for item in z.infolist():
                if item.is_dir():continue
                parts=Path(item.filename).parts
                assert '..' not in parts and not Path(item.filename).is_absolute()
                if '.data' in parts[0]:
                    # Only the optional Numba command-line script uses this.
                    if parts[1] in ('purelib','platlib'):destination=site.joinpath(*parts[2:])
                    elif parts[1]=='scripts':destination=runtime/'Scripts'/Path(*parts[2:])
                    else:raise ValueError('Unsupported wheel data: '+item.filename)
                else:destination=site/item.filename
                destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(z.read(item))
    assert launcher is not None
    # NumPy ships Microsoft's redistributable runtime under a wheel-local name.
    # Numba imports the standard name. Preserve the binary and its bundled license.
    msvcp=next((site/'numpy.libs').glob('msvcp140-*.dll'))
    shutil.copy2(msvcp,runtime/'msvcp140.dll')
    entry=io.BytesIO()
    with zipfile.ZipFile(entry,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('__main__.py','from desktop_start import run\nif __name__ == "__main__":\n    raise SystemExit(run())\n')
    (package/'2048.exe').write_bytes(launcher+b'#!<launcher_dir>\\runtime\\pythonw.exe\n'+entry.getvalue())
    for name in FILES:
        assert (source/name).is_file(),name
        if name.endswith('.bat'):
            (package/name).write_bytes((source/name).read_text(encoding='utf-8').replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
        else:shutil.copy2(source/name,package/name)
    shutil.copytree(source/'fonts',package/'fonts')
    shutil.copy2(runtime/'LICENSE.txt',licenses/'Python-LICENSE.txt')
    assert not any((package/name).exists() for name in ('data','.venv','exports'))

    # Architecture and imported-DLL audit across the entire packaged runtime.
    pe_files=[p for p in package.rglob('*') if p.suffix.lower() in ('.dll','.pyd','.exe')]
    available={p.name.lower() for p in pe_files};system=set();checked=[]
    known={'kernel32.dll','user32.dll','advapi32.dll','ole32.dll','oleaut32.dll','shell32.dll','shlwapi.dll','gdi32.dll','comdlg32.dll','comctl32.dll','winmm.dll','version.dll','ws2_32.dll','bcrypt.dll','crypt32.dll','ntdll.dll','msvcrt.dll','ucrtbase.dll','secur32.dll','iphlpapi.dll','setupapi.dll','imm32.dll','dwmapi.dll','dxgi.dll','d3d11.dll','d3d9.dll','powrprof.dll','hid.dll','cfgmgr32.dll','rpcrt4.dll','normaliz.dll','psapi.dll','wtsapi32.dll','avrt.dll','dbghelp.dll','wintrust.dll','mswsock.dll','dinput8.dll','ddraw.dll','dxguid.dll'}
    known.update(('propsys.dll','mfplat.dll','mf.dll','mfreadwrite.dll'))
    missing={};optional={};details={path:pe_details(path.read_bytes()) for path in pe_files}
    for path in pe_files:
        machine,imports,symbols,exports=details[path];assert machine==0x8664,(path,machine)
        for dll in imports:
            if dll not in available:
                if dll in known or dll.startswith(('api-ms-win-','ext-ms-win-')):system.add(dll)
                elif (dll=='tbb12.dll' and path.name.startswith('tbbpool.')) or (dll=='vcomp140.dll' and path.name.startswith('omppool.')):
                    optional.setdefault(dll,[]).append(str(path.relative_to(package)))
                else:missing.setdefault(dll,[]).append(str(path.relative_to(package)))
        checked.append(str(path.relative_to(package)))
    exports=details[runtime/'msvcp140.dll'][3];required=set()
    for _,_,symbols,_ in details.values():required.update(symbols.get('msvcp140.dll',set()))
    absent=sorted(required-exports)
    assert not absent, 'Missing Microsoft runtime exports: '+str(absent)
    report=dict(python=PYTHON,python_sha256=expected,dependencies=dependencies,pe_files=len(checked),architecture='Windows x86-64',unresolved_imports=missing,optional_unused_backends=optional,msvcp_source=str(msvcp.relative_to(package)),msvcp_sha256=sha(msvcp),msvcp_symbols_verified=len(required),system_dlls=sorted(system),windows_execution_tested=False)
    (package/'build-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not missing,missing
    return package,report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--downloads',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='2048-win-build-') as folder:
        package,report=assemble(source,args.downloads.resolve(),Path(folder))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for path in sorted(package.rglob('*')):
                if path.is_file():z.write(path,str(Path(package.name)/path.relative_to(package)))
        with zipfile.ZipFile(args.output) as z:assert z.testzip() is None
        (source/'validation/v12/windows-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(dict(output=str(args.output),bytes=args.output.stat().st_size,sha256=sha(args.output),pe_files=report['pe_files'],unresolved_imports=report['unresolved_imports'])))

if __name__=='__main__':main()
