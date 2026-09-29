"""Native font faces, explicit weights, and a shared optical line box.

Read installed fonts in place; never bundle or redistribute system font files.
"""
from pathlib import Path
from functools import lru_cache
import struct,os,sys
import pygame as pg
import pygame.freetype as ft

def face_names(path):
    """Read PostScript face names from a TrueType collection without loading it."""
    with Path(path).open('rb') as handle:
        head=handle.read(12)
        count=struct.unpack('>I',head[8:12])[0] if head[:4]==b'ttcf' else 0
        offsets=struct.unpack('>'+str(count)+'I',handle.read(count*4)) if count else [0]
        result={}
        for index,start in enumerate(offsets):
            handle.seek(start);head=handle.read(12);tables={}
            for _ in range(struct.unpack('>H',head[4:6])[0]):
                tag,_,offset,length=struct.unpack('>4sIII',handle.read(16));tables[tag]=(offset,length)
            if b'name' not in tables:continue
            offset,length=tables[b'name'];handle.seek(offset);data=handle.read(length)
            _,records,storage=struct.unpack('>HHH',data[:6])
            for i in range(records):
                platform,_,language,key,length,offset=struct.unpack('>HHHHHH',data[6+i*12:18+i*12])
                if key==6 and platform in (0,3) and language in (0,1033):
                    try:result[data[storage+offset:storage+offset+length].decode('utf-16-be')]=index
                    except UnicodeError:pass
        return result

FONT_ROOT=Path(__file__).resolve().parent/'fonts'

def bundled_families():
    paths={weight:FONT_ROOT/('NotoSansSC-'+name+'.otf') for weight,name in
        [('regular','Regular'),('medium','Medium'),('semibold','Bold')]}
    return {weight:(str(path),0) for weight,path in paths.items()} if all(p.is_file() for p in paths.values()) else None

def windows_fonts():
    return Path(os.environ.get('WINDIR',os.environ.get('SystemRoot','C:/Windows')))/'Fonts'

@lru_cache(maxsize=1)
def families():
    bundled=bundled_families()
    if bundled and (sys.platform=='win32' or os.environ.get('ATELIER_FONT_SOURCE')=='bundled'):return bundled
    candidates=[Path('/System/Library/Fonts/PingFang.ttc')]
    candidates.extend(Path('/System/Library/AssetsV2').glob('com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc'))
    for path in candidates:
        if path.exists():
            try:names=face_names(path)
            except (OSError,ValueError,struct.error):continue
            if 'PingFangSC-Regular' in names:
                return {weight:(str(path),names.get('PingFangSC-'+name,names['PingFangSC-Regular']))
                    for weight,name in [('regular','Regular'),('medium','Medium'),('semibold','Semibold')]}
    win=windows_fonts()
    if (win/'msyh.ttc').is_file():
        return {weight:(str(win/('msyhbd.ttc' if weight=='semibold' and (win/'msyhbd.ttc').is_file() else 'msyh.ttc')),0)
            for weight in ('regular','medium','semibold')}
    if bundled:return bundled
    fallback=next((p for p in ['/System/Library/Fonts/Hiragino Sans GB.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'] if Path(p).exists()),None)
    return {weight:(fallback,0) for weight in ('regular','medium','semibold')}

class Face:
    """The render/size subset used by pygame.font callers in this renderer."""
    def __init__(self,size,kind):
        if not ft.get_init():ft.init()
        self.pixels=round(size*2);self.height=round(self.pixels*1.22);self.baseline=round(self.pixels*.94)
        if kind in ('latin','number','display','latin_medium'):
            win=windows_fonts();name='segoeuib.ttf' if kind=='display' else 'seguisb.ttf' if kind in ('number','latin_medium') else 'segoeui.ttf'
            forced=os.environ.get('ATELIER_FONT_SOURCE')=='bundled'
            paths=[] if forced else [str(win/name),str(win/'segoeui.ttf')] if sys.platform=='win32' else ['/System/Library/Fonts/HelveticaNeue.ttc']
            path=next((p for p in paths if Path(p).is_file()),None)
            index=(1 if kind=='display' else 10 if kind in ('number','latin_medium') else 0) if path and path.endswith('HelveticaNeue.ttc') else 0
            if not path:path,index=families()['semibold' if kind=='display' else 'medium' if kind in ('number','latin_medium') else 'regular']
        else:
            weight='semibold' if kind=='title' or size>=20 else 'medium' if kind=='body_medium' else 'regular'
            path,index=families()[weight]
        self.native=ft.Font(path,self.pixels,font_index=index);self.native.kerning=True
        self.path=path;self.index=index

    def size(self,text):
        bounds=self.native.get_rect(str(text))
        return max(1,bounds.width+max(0,bounds.x)),self.height

    def render(self,text,antialias,color):
        self.native.antialiased=antialias
        glyph,bounds=self.native.render(str(text),color)
        surface=pg.Surface(self.size(text),pg.SRCALPHA)
        surface.blit(glyph,(max(0,bounds.x),self.baseline-bounds.y))
        return surface
