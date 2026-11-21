"""LITHO PILOT - 6 s style test for the 2D vintage lithograph / 1940s newspaper look (nightkit/litho.py, style 'litho44').
A newspaper-front header (masthead, headline, italic deck), and below it a printed world: drifting clouds, a far castle with a
waving banner (gold disc emblem), a laurel medallion with a halftone 'photo' of the boss, and a knight puppet walking along a path.
Animated on twos with boiling outlines; slow push-in on the world. No voice.
Run: TEST=0,3 python examples/litho_pilot.py -> test.png | python examples/litho_pilot.py -> out/litho_pilot.mp4"""
import os, sys, math, subprocess
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import numpy as np
from PIL import Image
from nightkit import litho

W,H,FPS,DUR=1080,1920,24,6.0; N=int(DUR*FPS)
PAPER=litho.make_paper(W,H)
F_MAST=litho.font('Oswald[wght].ttf',92,'Bold'); F_HEAD=litho.font('LeagueGothic[wdth].ttf',124); F_DECK=litho.font('PlayfairDisplay-Italic[wght].ttf',34,'Bold Italic')
F_SMALL=litho.font('OldStandard-Regular.ttf',22); F_SMALLB=litho.font('OldStandard-Bold.ttf',27); F_CAP=litho.font('PlayfairDisplay-Italic[wght].ttf',28,'Italic')
HEADER_BOTTOM=640

def rot(pts,a,px,py):
    c,s=math.cos(a),math.sin(a); return [(px+(x-px)*c-(y-py)*s,py+(x-px)*s+(y-py)*c) for x,y in pts]
def header(pg):
    pg.d['ink'].rectangle([40,36,W-40,42],fill=255); pg.d['ink'].rectangle([40,48,W-40,50],fill=255)
    pg.text('Insert Disc 2',(W//2,66),F_MAST,'mast','ma')
    for x0,lines in ((48,['TINY STORIES','from retro games','that never existed']),(W-278,['TONIGHT','THE FINAL BOSS','a tragedy in 3 phases'])):
        pg.d['ink'].rounded_rectangle([x0,64,x0+230,188],radius=10,outline=255,width=3)
        pg.text(lines[0],(x0+115,74),F_SMALLB,'ink','ma'); pg.text(lines[1],(x0+115,112),F_SMALL,'ink','ma'); pg.text(lines[2],(x0+115,146),F_SMALL,'ink','ma')
    pg.text('Vol. 2  —  No. 7201',(60,214),F_SMALL,'ink','la'); pg.text('Wednesday, 30 August',(W-60,214),F_SMALL,'ink','ra')
    pg.d['ink'].rectangle([40,252,W-40,259],fill=255); pg.d['ink'].rectangle([40,265,W-40,267],fill=255)
    pg.text('WHY DO FINAL BOSSES',(W//2,284),F_HEAD,'ink','ma'); pg.text('NEVER LEAVE THEIR ROOMS?',(W//2,408),F_HEAD,'ink','ma')
    pg.text('The knight came for the fight. The boss came for the door.',(W//2,560),F_DECK,'ink','ma')
    pg.d['ink'].rectangle([40,HEADER_BOTTOM-8,W-40,HEADER_BOTTOM-5],fill=255)

def world(pg,t,g):
    k=1.0+0.06*(t/DUR); cx,cy=540,1350                                   # slow push-in on the world
    T=lambda pts:[(cx+(x-cx)*k,cy+(y-cy)*k) for x,y in pts]
    # clouds (blue plate, dark-blue halftone underside, ink outline), drifting
    for i,(x0,y0,s,v) in enumerate(((150,800,1.0,14),(640,760,1.3,9),(1000,700,0.8,18))):
        x=x0-v*t; blobs=[(-70,10,70,48),(-10,-20,85,62),(70,5,72,50),(10,25,110,40)]
        E=[]
        for bx,by,rx,ry in blobs:
            P=T([(x+bx*s,y0+by*s)])[0]; E.append((P[0],P[1],rx*s*k,ry*s*k))
        pg.blob(E,'blue','blue_dark',0.55,'ink',4,seed=g*31+i)
    # far hills (sepia halftone) + castle
    hill=T([(0,1180),(220,1080),(480,1130),(760,1050),(1080,1120),(1080,1500),(0,1500)])
    hm=Image.new('L',(W,H),0); from PIL import ImageDraw as _D; _D.Draw(hm).polygon(pg.wobble(hill,seed=g),fill=255); pg.tone('sepia',hm,0.35,angle=15)
    pg.shape(hill,None,'ink',3,seed=g+1)
    cast=[(230,1095),(230,980),(255,980),(255,960),(280,960),(280,980),(330,980),(330,900),(352,900),(352,880),(374,880),(374,900),(396,900),(396,980),(430,980),(430,1095)]
    pg.shape(T(cast),'sepia','ink',3,seed=g+2,solid=True)
    # banner on the tower: waves, gold disc emblem
    px,py=385,880; pole=T([(px,py),(px,py-120)]); pg.line(pole,'ink',4,seed=g+3)
    top=[(px+i*12,py-118+6*math.sin(i*0.7-t*4)) for i in range(11)]; bot=[(px+i*12,py-62+6*math.sin(i*0.7-t*4+0.4)) for i in range(10,-1,-1)]
    pg.shape(T(top+bot),'red','ink',3,seed=g+4,solid=True)
    ec=T([(px+60,py-90+6*math.sin(5*0.7-t*4))])[0]; pg.ellipse(ec[0],ec[1],15*k,15*k,'gold','ink',2,seed=g+5); pg.ellipse(ec[0],ec[1],4*k,4*k,None,'ink',2,seed=g+6)
    # near ground: green with halftone shading + a path
    gnd=T([(0,1460),(300,1400),(700,1430),(1080,1380),(1080,1920),(0,1920)])
    gm=Image.new('L',(W,H),0); _D.Draw(gm).polygon(pg.wobble(gnd,seed=g+7),fill=255); pg.tone('green',gm,0.55,angle=75)
    pg.shape(gnd,None,'ink',4,seed=g+8)
    path=T([(0,1690),(400,1640),(800,1660),(1080,1610),(1080,1730),(800,1770),(400,1760),(0,1810)])
    pg.shape(path,None,'ink',3,seed=g+9); pm=Image.new('L',(W,H),0); _D.Draw(pm).polygon(pg.wobble(path,seed=g+9),fill=255)
    pg.m['green']=Image.fromarray(np.where(np.asarray(pm)>0,0,np.asarray(pg.m['green'])).astype(np.uint8)); pg.d['green']=_D.Draw(pg.m['green'])
    pg.tone('sepia',pm,0.18,angle=45)
    # laurel medallion with a halftone 'photo' of the boss
    mx,my,mr=800,980,150; ko=Image.new('L',(W,H),0); _D.Draw(ko).ellipse([mx-mr-20,my-mr-20,mx+mr+20,my+mr+20],fill=255); pg.knockout(ko)
    mm=Image.new('L',(W,H),0); _D.Draw(mm).ellipse([mx-mr+18,my-mr+18,mx+mr-18,my+mr-18],fill=255)
    yy,xx=np.mgrid[0:H,0:W]; lev=np.clip(0.25+0.35*((yy-my)/mr),0,0.8)
    boss=[(mx-60,my+mr-30),(mx-55,my-20),(mx-40,my-60),(mx-75,my-120),(mx-30,my-80),(mx,my-95),(mx+30,my-80),(mx+75,my-120),(mx+40,my-60),(mx+55,my-20),(mx+60,my+mr-30)]
    bm=Image.new('L',(W,H),0); _D.Draw(bm).polygon(boss,fill=255); lev=np.where(np.asarray(bm)>0,0.85,lev)
    pg.tone('sepia',mm,lev,angle=45,cell=7); pg.d['red'].ellipse([mx-22,my-72,mx-8,my-60],fill=255); pg.d['red'].ellipse([mx+8,my-72,mx+22,my-60],fill=255)
    pg.ellipse(mx,my,mr-18,mr-18,None,'ink',4,seed=g+10)
    for i in range(26):                                                    # laurel leaves around the ring
        a=-math.pi/2+i*2*math.pi/26; lx,ly=mx+(mr-4)*math.cos(a),my+(mr-4)*math.sin(a)
        pg.ellipse(lx,ly,22,9,'green','ink',2,seed=g*3+i,rot=a+math.pi/2+0.5,n=14)
    for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4):                # red ribbon ties
        rx,ry=mx+mr*math.cos(a),my+mr*math.sin(a)
        for d in (-1,1): pg.shape([(rx-14,ry-14*d),(rx+14,ry+14*d),(rx+10,ry+18*d),(rx-18,ry-10*d)],'red','ink',2,seed=g+20+int(a*10)+d)
    cap='Fig. 1 — The boss, waiting in the last room.'; cw=F_CAP.getlength(cap); kb=Image.new('L',(W,H),0); _D.Draw(kb).rectangle([mx-cw/2-12,my+mr+10,mx+cw/2+12,my+mr+52],fill=255); pg.knockout(kb)
    pg.text(cap,(mx,my+mr+16),F_CAP,'ink','ma')
    # the knight (puppet), walking right along the path
    hx=180+60*t; hy=1660-20*math.sin(hx/260)-8*abs(math.sin(t*2*math.pi*1.1)); s=1.15
    def P(pts): return T([(hx+x*s,hy+y*s) for x,y in pts])
    ph=math.sin(t*2*math.pi*1.1)*0.45
    for sgn,plate in ((-1,'ink'),(1,'ink')):
        leg=rot([(-20,0),(20,0),(18,165),(-18,165)],sgn*ph,0,0); foot=rot([(-18,150),(40,150),(40,175),(-18,175)],sgn*ph,0,0)
        pg.shape(P(leg),None,'ink',4,seed=g*5+sgn+7,solid=True); pg.shape(P(foot),None,'ink',4,seed=g*5+sgn+9,solid=True)
    cape=[(-40,-175),(-55,-170),(-110+10*math.sin(t*5),20),(-40,10)]; pg.shape(P(cape),'red','ink',4,seed=g+30,solid=True)
    torso=[(-48,5),(48,5),(42,-180),(-42,-180)]; pg.shape(P(torso),None,'ink',4,seed=g+31,solid=True)
    tm=Image.new('L',(W,H),0); _D.Draw(tm).polygon(P([(-48,5),(0,5),(0,-180),(-42,-180)]),fill=255); pg.tone('ink',tm,0.22,angle=45,cell=7)
    pg.d['ink'].polygon(P([(-48,-10),(48,-10),(48,8),(-48,8)]),fill=255)                    # belt
    helm=[(-36,-285),(36,-285),(40,-180),(-40,-180)]; pg.shape(P(helm),None,'ink',4,seed=g+32,solid=True); pg.line(P([(-5,-238),(40,-238)]),'ink',7,seed=g+33)
    plume=[(-10,-285),(-30,-330),(10,-345),(25,-300),(10,-285)]; pg.shape(P(plume),'red','ink',3,seed=g+34,solid=True)
    arm=rot([(-12,0),(12,0),(10,120),(-10,120)],-ph,0,0); arm=[(x+30,y-165) for x,y in arm]; pg.shape(P(arm),None,'ink',4,seed=g+35,solid=True)
    hand=(30+math.sin(-ph)*-120,-165+math.cos(-ph)*120); blade=[(hand[0]-5,hand[1]),(hand[0]+5,hand[1]),(hand[0]+60,hand[1]+150),(hand[0]+50,hand[1]+155)]
    pg.shape(P(blade),None,'ink',3,seed=g+36,solid=True); pg.shape(P([(hand[0]-20,hand[1]-6),(hand[0]+20,hand[1]-6),(hand[0]+20,hand[1]+6),(hand[0]-20,hand[1]+6)]),'gold','ink',2,seed=g+37)

def frame(f):
    g=f//2; t=g*2/FPS                                                      # on twos: a new drawing every 2 frames
    pg=litho.Page(W,H,seed=g); world(pg,t,g)
    # the header is printed on top of the world (paper-white box behind it)
    for k_ in pg.m:
        a=np.asarray(pg.m[k_]).copy(); a[:HEADER_BOTTOM]=0; pg.m[k_]=Image.fromarray(a); pg.d[k_]=__import__('PIL.ImageDraw',fromlist=['x']).Draw(pg.m[k_])
    header(pg)
    return pg.print(PAPER,frame_seed=g)

if __name__=='__main__':
    TEST=os.environ.get('TEST')
    if TEST:
        ims=[frame(int(float(x)*FPS)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*W//2,H//2))
        for i,im in enumerate(ims): sh.paste(im.resize((W//2,H//2),Image.LANCZOS),(i*W//2,0))
        sh.save('test.png'); sys.exit()
    os.makedirs('out',exist_ok=True)
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','out/litho_pilot.mp4'],stdin=subprocess.PIPE)
    last=None
    for f in range(N):
        if f%2==0: last=np.asarray(frame(f)).tobytes()
        p.stdin.write(last)
    p.stdin.close(); p.wait(); print('out/litho_pilot.mp4')
