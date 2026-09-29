"""Restrained, opaque game pieces with soft contact shadows."""
import numpy as np
import pygame as pg
from PIL import Image,ImageDraw,ImageFilter


def rounded_surface(width,height,colour,radius,grain=.22,lift=1.5):
    y=np.linspace(0,1,height)[:,None]
    c=np.asarray(pg.Color(colour)[:3],float)
    rgb=np.broadcast_to(c,(height,width,3)).copy()
    rgb+=(.5-y[:,:,None])*lift
    rgb+=np.random.default_rng(29).normal(0,grain,(height,width,1))
    mask=Image.new('L',(width,height))
    ImageDraw.Draw(mask).rounded_rectangle((0,0,width-1,height-1),radius,fill=255)
    rgba=np.concatenate((np.clip(rgb,0,255).astype('uint8'),np.asarray(mask)[:,:,None]),axis=2)
    result=pg.image.frombytes(rgba.tobytes(),(width,height),'RGBA')
    return result.convert_alpha()


def shadow(width,height,radius,blur=18,opacity=22):
    pad=blur*3
    im=Image.new('RGBA',(width+pad*2,height+pad*2))
    ImageDraw.Draw(im).rounded_rectangle((pad,pad,pad+width,pad+height),radius,fill=(23,34,25,opacity))
    im=im.filter(ImageFilter.GaussianBlur(blur))
    return pg.image.frombytes(im.tobytes(),im.size,'RGBA').convert_alpha(),pad
