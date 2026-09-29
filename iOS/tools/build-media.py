#!/usr/bin/env python3
"""Assemble sampled native gameplay as MJPEG AVI, then decode that AVI into GIF.
Requires Pillow and FFmpeg (FFMPEG environment variable or imageio-ffmpeg).
Uses software H.264; never modifies game code.
Usage: python3 tools/build-media.py CAPTURE_DIRECTORY [OUTPUT_DIRECTORY]
"""
from pathlib import Path
import hashlib, io, json, os, shutil, struct, subprocess, sys
from PIL import Image

def chunk(tag, data):
    return tag + struct.pack('<I', len(data)) + data + (b'\0' if len(data) & 1 else b'')

def make_avi(jpegs, width, height, fps=12):
    count = len(jpegs); biggest = max(map(len, jpegs))
    avih = struct.pack('<14I', round(1e6/fps), biggest*fps, 0, 0x10, count, 0, 1, biggest, width, height, 0, 0, 0, 0)
    strh = struct.pack('<4s4sIHHIIIIIIIIhhhh', b'vids', b'MJPG', 0, 0, 0, 0, 1, fps, 0, count, biggest, 0xffffffff, 0, 0, 0, width, height)
    strf = struct.pack('<IiiHH4sIiiII', 40, width, height, 1, 24, b'MJPG', width*height*3, 0, 0, 0, 0)
    header = chunk(b'LIST', b'hdrl' + chunk(b'avih', avih) + chunk(b'LIST', b'strl' + chunk(b'strh', strh) + chunk(b'strf', strf)))
    movi = bytearray(b'movi'); index = bytearray()
    for data in jpegs:
        index.extend(struct.pack('<4sIII', b'00dc', 0x10, len(movi), len(data)))
        movi.extend(chunk(b'00dc', data))
    return chunk(b'RIFF', b'AVI ' + header + chunk(b'LIST', movi) + chunk(b'idx1', index))

def read_avi_jpegs(path):
    data = path.read_bytes(); assert data[:4] == b'RIFF' and data[8:12] == b'AVI '
    assert struct.unpack_from('<I', data, 4)[0] + 8 == len(data)
    at=12
    while at+8 <= len(data):
        tag=data[at:at+4]; size=struct.unpack_from('<I',data,at+4)[0]; start=at+8
        if tag == b'LIST' and data[start:start+4] == b'movi':
            pos=start+4
            while pos < start+size:
                n=struct.unpack_from('<I',data,pos+4)[0]
                assert data[pos:pos+4] == b'00dc'
                yield data[pos+8:pos+8+n]
                pos += 8+n+(n&1)
        at += 8+size+(size&1)

ffmpeg=os.environ.get('FFMPEG') or shutil.which('ffmpeg')
if not ffmpeg:
 import imageio_ffmpeg
 ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
source=Path(sys.argv[1]); output=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parents[1]/'docs/media'
output.mkdir(parents=True,exist_ok=True)
manifest=[]
for log in sorted(source.glob('[0-9][0-9]-*.json')):
    meta=json.loads(log.read_text()); name=meta['name']
    frames=sorted((source/name).glob('*.jpg')); assert len(frames)==meta['frames']
    width,height=Image.open(frames[0]).size
    avi=source/(name+'.avi'); avi.write_bytes(make_avi([p.read_bytes() for p in frames],width,height,meta['fps']))
    assert len(list(read_avi_jpegs(avi))) == len(frames)
    mp4=output/(name+'.mp4')
    subprocess.run([ffmpeg,'-v','error','-y','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],check=True)
    # Decode the delivered video with FFmpeg before making the GIF.
    reader=subprocess.Popen([ffmpeg,'-v','error','-i',str(mp4),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    decoded=[]
    while True:
        data=reader.stdout.read(width*height*3)
        if not data: break
        assert len(data)==width*height*3
        decoded.append(Image.frombytes('RGB',(width,height),data))
    assert reader.wait()==0 and len(decoded)==len(frames)
    legacy=output/(name+'.avi')
    if legacy.exists(): legacy.unlink()
    # One palette across the entire clip limits distracting colour shimmer.
    contact=Image.new('RGB',(1000,700*3))
    for i,p in enumerate([decoded[0],decoded[len(decoded)//2],decoded[-1]]): contact.paste(p.resize((1000,700)),(0,i*700))
    palette=contact.quantize(colors=160,method=Image.Quantize.MEDIANCUT)
    gifs=[p.quantize(palette=palette,dither=Image.Dither.NONE) for p in decoded]
    gif=output/(name+'.gif')
    # GIF centiseconds approximate 12 fps with an 80/80/90 ms pattern.
    duration=[80,80,90]*(len(gifs)//3)+[80,80,90][:len(gifs)%3]
    gifs[0].save(gif,save_all=True,append_images=gifs[1:],duration=duration,loop=0,optimize=True,disposal=1)
    shutil.copyfile(source/(name+'-poster.png'),output/(name+'-poster.png'))
    image=Image.open(gif); total=0
    for i in range(image.n_frames): image.seek(i); total+=image.info['duration']
    assert abs(total/1000-meta['duration'])<0.1
    assert image.n_frames>1
    meta.update({'video_codec':'H.264 / yuv420p', 'decoded_video_frames':len(decoded), 'gif_source':'decoded delivered MP4', 'size':[width,height],'gif_frames':image.n_frames,'gif_duration_ms':total,'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [mp4,gif,output/(name+'-poster.png')]}})
    manifest.append(meta); print(name, 'MP4',mp4.stat().st_size,'GIF',gif.stat().st_size,'frames',image.n_frames,flush=True)
(output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
