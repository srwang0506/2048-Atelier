"""Small optical surfaces. No image backgrounds; all materials are cached."""
import numpy as np
import pygame as pg
from PIL import Image,ImageDraw,ImageFilter


def surface(rgb,alpha):
    data=np.concatenate((np.clip(rgb,0,255),np.clip(alpha,0,255)[...,None]),axis=-1).astype('uint8')
    return pg.image.frombytes(data.tobytes(),(data.shape[1],data.shape[0]),'RGBA').convert_alpha()


def glass(size,tint,radius=32,light=False):
    yy,xx=np.mgrid[0:size,0:size].astype(float)
    x=(xx+.5)/size;y=(yy+.5)/size
    qx=np.abs(xx+.5-size/2)-(size/2-radius)
    qy=np.abs(yy+.5-size/2)-(size/2-radius)
    sdf=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius
    mask=np.clip(-sdf+.5,0,1)
    depth=np.maximum(0,-sdf)
    c=np.asarray(pg.Color(tint)[:3],float)
    # Broad interior light, a dark center, and a reflected light at the foot.
    illumination=.73+.20*np.exp(-((x-.12)**2+(y+.05)**2)/.7)+.14*y**4
    rgb=np.broadcast_to(c,(size,size,3)).copy()*illumination[...,None]
    sweep=np.exp(-((x*.64+y*.76-.16)/.26)**2)
    rgb+=sweep[...,None]*np.array([18,20,25])
    bottom=np.exp(-((y-.94)/.058)**2)*np.exp(-((x-.64)/.46)**2)
    rgb+=bottom[...,None]*np.array([10,13,19])
    # A narrow glass edge: brighter at the two reflected-light corners.
    rim=np.exp(-((depth-1.2)/1.25)**2)
    bevel=np.exp(-((depth-4.7)/2.9)**2)
    spec=.13+.68*np.exp(-((x-.08)**2+(y-.02)**2)/.13)+.30*np.exp(-((x-.88)**2+(y-.96)**2)/.12)
    rgb+=rim[...,None]*spec[...,None]*140
    rgb+=bevel[...,None]*spec[...,None]*25
    # A fine shadow inside the lower edge gives the slab a small apparent depth.
    rgb-=np.exp(-((depth-7)/2.6)**2)[...,None]*y[...,None]*7
    rgb+=np.random.default_rng(114).normal(0,.25,(size,size,1))
    alpha=mask*(245 if light else 240)
    return surface(rgb,alpha)


def soft_shadow(w,h,radius,blur=20,opacity=60):
    pad=blur*3
    im=Image.new('RGBA',(w+pad*2,h+pad*2))
    ImageDraw.Draw(im).rounded_rectangle((pad,pad,pad+w,pad+h),radius,fill=(0,0,0,opacity))
    im=im.filter(ImageFilter.GaussianBlur(blur))
    return pg.image.frombytes(im.tobytes(),im.size,'RGBA').convert_alpha(),pad


def glass_light(size):
    y,x=np.mgrid[-1:1:complex(size),-1:1:complex(size)]
    alpha=np.exp(-(x*x+y*y)*4)*19
    rgb=np.empty((size,size,3));rgb[:]=[206,224,255]
    return surface(rgb,alpha)
