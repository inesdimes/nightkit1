"""Episode 01 - THE ELEVATOR, rebuilt entirely with nightkit (20 s seamless loop, 9:16).
Run:  python examples/elevator.py  -> out/the_elevator.mp4 (+ checks)"""
import os, sys, math
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit import scenes, figures, motion, scares, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS,DUR=24,20.0; N=int(FPS*DUR); W,H,S=180,320,6
START_FRAME=308                  # loop is played from the moment the light returns with the figure at the door
# ---------- schedule ----------
cab=scares.Outages([(0.30,0.42),(0.55,0.62),(7.00,7.18),(8.60,8.78),(10.00,10.20),(11.30,11.50),(12.60,12.85)])
hall=scares.Outages([(0.44,0.50),(16.60,16.70),(16.78,16.86),(16.95,17.22)])
creep=scares.CreepWhenDark(cab,scares.creeping_positions((0.48,1.48),(0.34,0.2),5,presence=(0.25,0.86))[:2]+[(-0.18,0.9,0.58),(0.06,0.52,0.74),(0.34,0.2,0.86)],appear_after=2,hide_at=15.6)
door=motion.Track([(14.0,(1.0,)),(15.6,(0.0,)),(18.0,(0.0,)),(19.6,(1.0,))])
cam_path=motion.approach_and_return((0.05,1.62,-4.6),(0.0,1.58,-1.9),1.0,14.0,15.6,18.5)
def floor_digit(t):
    d='4'
    for tt,v in ((16.0,'3'),(16.35,'2'),(16.7,'1'),(17.05,'B'),(17.6,'4')):
        if t>=tt: d=v
    return d
# ---------- world ----------
hall_scene=scenes.elevator_hall(seed=21)
R=Renderer(W,H,fog=(14,15,13))
vhs=post.VHS(W*S,H*S,S,grade='sick_green',chroma=2,band_period=DUR)
frames=[]
for f in range(N):
    t=f/FPS
    p=cam_path(t); dx,dy,dyaw,dpit=motion.handheld(t,DUR)
    c=Camera.look((p[0]+dx,p[1]+dy,p[2]),(0.0,1.15,1.0)); cam=(c[0],c[1],c[2],c[3]+dyaw,c[4]+dpit)
    cabin=scenes.elevator_cabin(light_on=cab.on(t))
    pre=cabin['pre']+scenes.sliding_doors(door(t)[0])
    st=creep.state(t)
    if st: pre+=figures.the_figure(st[0],st[1],k=st[2])
    lights=[]
    if hall.on(t): lights.append(((0,2.6,-2.2),(190,205,200),1.25*(0.93+0.07*math.sin(2*math.pi*37*t))))
    lights+=cabin['lamps']+[((0.99,1.2,-0.2),(220,140,40),0.12)]
    main=hall_scene['main']+scenes.lamp_panel((0,2.68,-2.2),hall.on(t),(0.7,0.8))+[scenes.quad([(0.96,1.18,-0.035),(1.02,1.18,-0.035),(1.02,1.26,-0.035),(0.96,1.26,-0.035)],(255,170,60),emit=True)]
    img,vi=R.render(cam,[pre,main],lights,fov=62,fog_start=3,fog_end=11,ambient=0.05)
    d=ImageDraw.Draw(img)
    q=R.project(hall_scene['anchors']['indicator'],vi)
    if q: font.text(d,floor_digit(t),int(q[0])-2,int(q[1])-3,(255,150,40),shadow=None)
    if 16.6<=t<17.3 and door(t)[0]<0.02:
        a=R.project((-0.6,2.1,0.02),vi); b=R.project((0.6,0.0,0.02),vi)
        if a and b: img=scares.reflection(img,(int(a[0]),int(a[1]),int(b[0]),int(b[1])),0.55 if not hall.on(t) else 0.25)
    frames.append(post.ps1(img))
# ---------- sound ----------
s=Sound(DUR,loop=True)
s.bed(s.mains_hum()+s.building_air()+s.drone(),1.0)
fl=s.fluorescent(); s.L+=fl*s.gate(hall.windows)*0.9; s.R+=fl*s.gate(hall.windows)
cabhum=(np.sin(2*np.pi*s.cyc(120)*s.t)*0.6+np.sin(2*np.pi*s.cyc(240)*s.t)*0.3)*0.012*s.gate(cab.windows); s.L+=cabhum; s.R+=cabhum
for a,b in cab.windows+hall.windows: s.crackle(a); s.crackle(b)
s.door_slide(14.0,seed=3); s.door_slide(18.0,seed=4); s.thud(15.6); s.motor(15.5)
for k,tt in enumerate((15.9,16.5,17.2)): s.creak(tt,pan=0.4-0.4*k)
for tt in (16.0,16.35,16.7,17.05,17.6): s.tick(tt)
s.ding(17.75); s.knock(10.6); s.breath(16.75)
s.music_box(8.9,[76,79,77,76,71,72,74,64])
s.poisson(0.45,avoid=[(6.15,7.05)])
s.reverb(0.35)
s.silence(6.2,7.0)
wav=s.save(os.path.join(OUT,'elevator.wav'),rotate_seconds=START_FRAME/FPS)
# ---------- encode (rotated start) ----------
mp4=os.path.join(OUT,'the_elevator.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for k in range(N):
        f=(k+START_FRAME)%N; enc.write(vhs(post.upscale(frames[f],S),f,f/FPS))
# ---------- verify ----------
print('probe',check.probe(mp4))
print('loop seam',check.loop_seam(mp4))
print('audio seam',check.audio_seam(mp4))
print('near-duplicates',check.near_duplicates(mp4))
