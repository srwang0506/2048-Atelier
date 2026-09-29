"""Optical game materials generated at render resolution, with true alpha."""
import numpy as np
import pygame as pg
from PIL import Image,ImageFilter


def surface(array):
    result=pg.image.frombytes(np.ascontiguousarray(array,dtype=np.uint8).tobytes(),(array.shape[1],array.shape[0]),'RGBA')
    return result.convert_alpha() if pg.display.get_surface() is not None else result


def crystal(size,color,radius=24,opacity=.25,height=None):
    """Rounded crystal with chromatic edge dispersion and a polished bevel."""
    height=height or size
    y,x=np.mgrid[0:height,0:size].astype(float)
    r=min(radius,size/2,height/2)
    qx=np.abs(x+.5-size/2)-(size/2-r);qy=np.abs(y+.5-height/2)-(height/2-r)
    sdf=np.sqrt(np.maximum(qx,0)**2+np.maximum(qy,0)**2)+np.minimum(np.maximum(qx,qy),0)-r
    mask=np.clip(-sdf,0,1)
    edge=np.exp(-(sdf/1.25)**2)*mask
    bevel=np.exp(-((sdf+6)/4)**2)*mask
    x=(x+.5)/size;y=(y+.5)/height
    light=np.clip(1.2-x*.55-y*.65,.04,1)
    sweep=np.exp(-((x+y-.34)/.105)**2)
    rng=np.random.default_rng(71)
    base=np.asarray(color[:3],float)[None,None,:]
    rgb=np.broadcast_to(base,(height,size,3)).copy()
    rgb=rgb*(.55+light[:,:,None]*.55)+sweep[:,:,None]*30
    rgb+=bevel[:,:,None]*np.stack([light*68,light*85,light*100],axis=-1)
    rainbow=np.stack([90+120*y,185-70*y,210-75*x],axis=-1)
    rgb=rgb*(1-edge[:,:,None]*.8)+rainbow*edge[:,:,None]*.8
    rgb+=rng.normal(0,.6,(height,size,1))
    alpha=(opacity+.08*light+.10*sweep+.16*bevel+edge*(.65*light+.1))*255*mask
    out=np.concatenate([np.clip(rgb,0,255),np.clip(alpha,0,255)[:,:,None]],axis=2)
    return surface(out)


def aura(size,color,power=1.8):
    y,x=np.mgrid[-1:1:complex(size),-1:1:complex(size)]
    strength=np.exp(-((x*x+y*y)*5)**power)
    data=np.zeros((size,size,4));data[:,:,:3]=color[:3];data[:,:,3]=strength*90
    return surface(data)


def blur_shadow(size,radius,color,spread=14):
    image=Image.new('RGBA',(size+spread*4,size+spread*4))
    from PIL import ImageDraw
    ImageDraw.Draw(image).rounded_rectangle((spread*2,spread*2,spread*2+size,spread*2+size),radius,fill=color)
    image=image.filter(ImageFilter.GaussianBlur(spread))
    return pg.image.frombytes(image.tobytes(),image.size,'RGBA')
