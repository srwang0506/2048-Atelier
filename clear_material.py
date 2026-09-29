"""Translucent, lightly refracting surfaces for the spatial interface."""
import numpy as np
import pygame as pg

def image(rgb,alpha=None):
    if alpha is None:alpha=np.full(rgb.shape[:2],255.)
    arr=np.concatenate((np.clip(rgb,0,255),np.clip(alpha,0,255)[...,None]),axis=-1).astype('uint8')
    return pg.image.frombytes(arr.tobytes(),(arr.shape[1],arr.shape[0]),'RGBA').convert_alpha()

def environment(w,h,dark=False):
    y,x=np.mgrid[0:h,0:w].astype(np.float32);x/=w;y/=h
    if dark:
        base=np.array([35.,39.,49.]);a=np.array([2.,5.,11.]);b=np.array([9.,2.,8.])
    else:
        base=np.array([241.,243.,248.]);a=np.array([-20.,-12.,1.]);b=np.array([3.,-12.,-2.])
    rgb=np.broadcast_to(base,(h,w,3)).copy()
    cool=np.exp(-((x-.34)**2/.08+(y-.66)**2/.11))
    warm=np.exp(-((x-.70)**2/.055+(y-.70)**2/.12))
    rgb+=cool[...,None]*a+warm[...,None]*b
    rgb+=((1-y)*3)[...,None]
    rgb=np.clip(rgb,0,255).astype('uint8')
    return rgb,image(rgb).convert()

def panel(backdrop,x,y,w,h,radius,tint='#ffffff',tint_strength=.08,dark=False):
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    qx=np.abs(xx+.5-w/2)-(w/2-radius);qy=np.abs(yy+.5-h/2)-(h/2-radius)
    sdf=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius
    depth=np.maximum(0,-sdf)
    mask=np.clip(-sdf+.5,0,1)
    nx,ny=np.gradient(sdf,axis=1),np.gradient(sdf,axis=0)
    bend=np.clip(1-depth/13,0,1)**2*9
    sx=np.clip(np.round(x+xx+nx*bend).astype(int),0,backdrop.shape[1]-1)
    sy=np.clip(np.round(y+yy+ny*bend).astype(int),0,backdrop.shape[0]-1)
    rgb=backdrop[sy,sx].copy()
    white=np.array([147,157,181] if dark else [255,255,255])
    frost=.25 if dark else .50
    rgb=rgb*(1-frost)+white*frost
    colour=np.array(pg.Color(tint)[:3])
    rgb=rgb*(1-tint_strength)+colour*tint_strength
    v=yy/max(1,h-1);u=xx/max(1,w-1)
    light=np.exp(-((u-.16)**2+(v-.02)**2)/.35)
    rgb+=light[...,None]*(7 if dark else 5)
    rim=np.exp(-((depth-.75)/.85)**2)
    spec=.2+.60*light+.18*np.exp(-((u-.85)**2+(v-.99)**2)/.10)
    rgb=rgb*(1-rim[...,None]*spec[...,None]*.42)+np.array([255,255,255])*rim[...,None]*spec[...,None]*.42
    rgb-=np.exp(-((depth-3.8)/1.8)**2)[...,None]*v[...,None]*(5 if dark else 3)
    return image(rgb,mask*255)
