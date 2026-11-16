"""Parametric locations. Each builder returns a dict:
  main  - faces of the visible environment (drawn after 'pre')
  pre   - faces that are always behind an opening (rooms, cabins) - drawn first
  lamps - [(position, colour, intensity)] defaults; anchors - useful named points."""
import random
import numpy as np
from .engine import quad, box, tiled_plane, wall_region
def _var(R,col,amt=5):
    c=R.randint(-amt,amt); return (col[0]+c,col[1]+c,col[2]+c)
def elevator_hall(seed=21,width=4.0,depth=6.0,height=2.7,opening=1.2,door_h=2.1,
                  floor_a=(78,74,60),floor_b=(40,52,44),wain=(46,58,48),wall=(104,100,84),steel=(122,124,120)):
    R=random.Random(seed); hw=width/2; ho=opening/2; Q=[]
    Q+=tiled_plane(-hw,hw,-depth,0,0,0.5,lambda i,j:_var(R,floor_a if (i+j)%2 else floor_b))
    for x in (-hw,hw):
        Q+=wall_region('x',x,-depth,0,0,1.0,0.75,1.0,lambda i,j,v:_var(R,wain,6),facing=1 if x<0 else -1)
        Q+=wall_region('x',x,-depth,0,1.0,1.06,0.75,0.06,lambda i,j,v:_var(R,(90,84,62),6),facing=1 if x<0 else -1)
        Q+=wall_region('x',x,-depth,0,1.06,height,0.75,1.64,lambda i,j,v:_var(R,wall,6),facing=1 if x<0 else -1)
    Q+=tiled_plane(-hw,hw,-depth,0,height,0.75,lambda i,j:(44,44,40))
    col=lambda i,j,v:_var(R,wain if v<1.0 else wall)
    Q+=wall_region('z',0,-hw,-ho,0,height,0.35,0.45,col)+wall_region('z',0,ho,hw,0,height,0.35,0.45,col)+wall_region('z',0,-ho,ho,door_h,height,0.35,0.45,col)
    Q+=box(-ho-0.12,-ho,0,door_h+0.12,-0.06,0,steel)+box(ho,ho+0.12,0,door_h+0.12,-0.06,0,steel)+box(-ho-0.12,ho+0.12,door_h,door_h+0.12,-0.06,0,steel)
    Q+=box(-0.32,0.32,door_h+0.22,door_h+0.46,-0.05,0,(28,26,24))
    Q+=box(ho+0.32,ho+0.46,1.05,1.4,-0.03,0,(110,108,100))
    Q+=box(-hw+0.1,-hw+0.8,0,0.85,-0.55,-0.25,(60,40,32))
    Q+=box(hw-0.55,hw-0.1,0,0.55,-1.3,-0.8,(26,26,24))
    return dict(main=Q,lamps=[((0,height-0.1,-2.2),(190,205,200),1.25)],
                anchors=dict(indicator=(0,door_h+0.34,-0.055),call=(ho+0.39,1.22,-0.035),door_rect=(-ho,door_h,ho,0.0,0.02),hall_lamp=(0,height-0.02,-2.2)),
                params=dict(opening=opening,door_h=door_h,height=height))
def elevator_cabin(seed=22,opening=1.2,width=1.4,depth=1.7,height=2.3,light_on=True,wood=(74,54,40),floor=(52,48,42)):
    R=random.Random(seed); hw=width/2; z0,z1=0.06,depth+0.05; Q=[]
    Q+=tiled_plane(-hw,hw,z0,z1,0,0.35,lambda i,j:_var(R,floor,4))
    Q+=wall_region('z',z1,-hw,hw,0,height,0.35,0.46,lambda i,j,v:wood)
    Q+=wall_region('x',-hw,z0,z1,0,height,0.42,0.46,lambda i,j,v:wood,facing=1)
    Q+=wall_region('x',hw,z0,z1,0,height,0.42,0.46,lambda i,j,v:wood,facing=-1)
    Q.append(quad([(-hw,height,z0),(hw,height,z0),(hw,height,z1),(-hw,height,z1)],(34,32,28)))
    Q.append(quad([(-0.3,height-0.01,0.6),(0.3,height-0.01,0.6),(0.3,height-0.01,1.2),(-0.3,height-0.01,1.2)],(236,228,180) if light_on else (30,30,26),emit=light_on))
    Q+=box(-0.6,0.6,0.95,1.0,z1-0.08,z1-0.03,(150,146,130))
    Q+=box(0.48,0.66,1.0,1.4,0.1,0.14,(96,94,88))
    return dict(pre=Q,lamps=[((0,height-0.15,0.9),(230,220,160),1.4)] if light_on else [],anchors=dict(far_corner=(0.48,1.48),door_edge=(0.34,0.2)))
def sliding_doors(open_k,opening=1.2,height=2.1,steel=(118,122,124)):
    """open_k: 1 fully open (panels hidden in the wall pockets) .. 0 closed. Put in the 'pre' layer."""
    ho=opening/2; off=ho*open_k
    Q=box(-ho-off,0.0-off,0,height,0.02,0.05,steel)+box(0.0+off,ho+off,0,height,0.02,0.05,steel)
    Q+=box(-0.02-off,0.0-off,0,height,0.015,0.02,(96,100,104))+box(0.0+off,0.02+off,0,height,0.015,0.02,(96,100,104))
    return Q
def corridor(seed=5,length=40.0,width=3.2,height=3.0,lamp_every=6.0,wall_lo=(54,58,66),stripe=(70,60,40),wall_hi=(64,70,80),floor=(46,50,56)):
    R=random.Random(seed); hw=width/2; Q=[]
    Q+=tiled_plane(-hw,hw,0,length,0,1.0,lambda i,j:_var(R,floor,6))
    for x,f in ((-hw,1),(hw,-1)):
        for (y0,y1,c) in ((0,0.9,wall_lo),(0.9,1.0,stripe),(1.0,height,wall_hi)):
            Q+=wall_region('x',x,0,length,y0,y1,1.0,y1-y0,lambda i,j,v,c=c:_var(R,c,5),facing=f)
    Q+=tiled_plane(-hw,hw,0,length,height,1.0,lambda i,j:(40,43,48))
    Q.append(quad([(-hw,0,length),(hw,0,length),(hw,height,length),(-hw,height,length)],(30,32,38)))
    lamps=[((0,height-0.3,z),(200,215,235),1.6) for z in np.arange(lamp_every/2,length,lamp_every)]
    return dict(main=Q,lamps=lamps,anchors=dict(start=(0,1.6,1.0),end=(0,1.6,length-2)),params=dict(width=width,height=height,length=length))
def lamp_panel(pos,on,size=(0.7,1.2),col_on=(220,232,228)):
    x,y,z=pos; sx,sz=size[0]/2,size[1]/2
    return [quad([(x-sx,y,z-sz),(x+sx,y,z-sz),(x+sx,y,z+sz),(x-sx,y,z+sz)],col_on if on else (40,42,40),emit=on)]
def stairwell(seed=7,flights=3,step_h=0.17,step_d=0.28,steps=10,width=1.2):
    """Simple switch-back staircase going down from y=0; each landing is (flight_index)."""
    R=random.Random(seed); Q=[]; y=0.0; z=0.0; d=1
    for f in range(flights):
        for s in range(steps):
            y-=step_h; z+=step_d*d; c=_var(R,(70,68,64),5)
            Q+=box(-width/2 if d>0 else 0.05,0 if d>0 else width/2+0.05,y-0.05,y,min(z,z-step_d*d),max(z,z-step_d*d),c)
        Q+=box(-width/2,width/2+0.05,y-0.08,y,z-0.05 if d>0 else z-1.0,z+1.0 if d>0 else z+0.05,_var(R,(64,62,58),4))
        d=-d
    return dict(main=Q,lamps=[],anchors={})
def parking_garage(seed=9,width=16,depth=24,height=2.6,pillar_every=5.0):
    R=random.Random(seed); hw=width/2; Q=[]
    Q+=tiled_plane(-hw,hw,0,depth,0,2.0,lambda i,j:_var(R,(58,58,56),4))
    Q+=tiled_plane(-hw,hw,0,depth,height,2.0,lambda i,j:(40,40,40))
    for x in np.arange(-hw+2,hw,pillar_every):
        for z in np.arange(3,depth,pillar_every):
            Q+=box(x-0.3,x+0.3,0,height,z-0.3,z+0.3,(90,90,86)); Q+=box(x-0.31,x+0.31,0,0.9,z-0.31,z+0.31,(150,130,40))
    for k in range(6):
        x=-hw+1.5+k*2.6; z=R.uniform(6,18)
        Q+=box(x-0.9,x+0.9,0.15,0.9,z-2.1,z+2.1,_var(R,(50,52,60),12))+box(x-0.8,x+0.8,0.9,1.35,z-1.1,z+0.9,_var(R,(40,42,48),8))
    return dict(main=Q,lamps=[((0,height-0.1,z),(200,210,190),1.3) for z in (4,12,20)],anchors={})
def bus_stop(seed=11,road_len=40):
    R=random.Random(seed); Q=[]
    Q+=tiled_plane(-6,6,-road_len/2,road_len/2,0,2.0,lambda i,j:(36,36,38) if 2<i<4 else _var(R,(70,70,66),4))
    Q+=box(-3.2,-2.0,0,2.3,-1.5,1.5,(30,34,38))
    Q.append(quad([(-2.0,0.3,-1.5),(-2.0,0.3,1.5),(-2.0,2.2,1.5),(-2.0,2.2,-1.5)],(60,80,90)))     # glass (reflection surface)
    Q+=box(-3.0,-2.4,0.42,0.48,-1.2,1.2,(80,70,60))                                                  # bench
    Q+=box(-1.7,-1.6,0,4.2,2.5,2.6,(70,70,70))                                                       # street light pole
    return dict(main=Q,lamps=[((-1.0,4.1,2.55),(230,190,120),1.8)],anchors=dict(bench=(-2.7,0.48,0),glass_rect=(-2.0,0.3,2.2,-1.5,1.5)))
