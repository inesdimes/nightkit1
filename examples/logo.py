import sys,os,math
NK=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.insert(0,NK); os.chdir(os.path.join(NK,'examples'))
src=open('chest_scam.py').read(); src=src[:src.index('# ======================= PIRATE SHOP')]; __file__='chest_scam.py'; exec(src)
from nightkit.zraster import zrender
from nightkit import font, post
OUTD=os.path.join(NK,'out','logo')
def glyph(ch): return font.FONT[ch]
def disc(tilt_t=0.0,spin=0.3):
    """low-poly CD with an embossed pixel '2' on the label"""
    Q=[]; N=20; rr=[0.16,0.36,0.42,1.0]
    for i in range(N):
        a0=spin+i*2*PI/N; a1=spin+(i+1)*2*PI/N
        for k in range(3):
            r0,r1=rr[k],rr[k+1]
            if k==0: col=(150,170,190)
            elif k==1: col=(200,206,214)
            else:
                h=(i/N+0.15*math.sin(i*1.3))%1.0
                import colorsys; c=colorsys.hsv_to_rgb(h,0.35,0.95); col=tuple(int(255*x) for x in c)
            pts=[(r0*math.cos(a0),0.02,r0*math.sin(a0)),(r1*math.cos(a0),0.02,r1*math.sin(a0)),(r1*math.cos(a1),0.02,r1*math.sin(a1)),(r0*math.cos(a1),0.02,r0*math.sin(a1))]
            Q.append(quad(pts[::-1],col,emit=k==2))
        Q.append(quad([(math.cos(a0),-0.02,math.sin(a0)),(math.cos(a1),-0.02,math.sin(a1)),(math.cos(a1),0.02,math.sin(a1)),(math.cos(a0),0.02,math.sin(a0))],(150,156,166)))
    # label "2": red pixels on the disc, sitting over the iridescent ring
    G=glyph('2'); px=0.09
    for r,row in enumerate(G):
        for c,v in enumerate(row):
            if v=='1':
                x=(c-2)*px; z=(3-r)*px+0.62
                Q+=box(x-px/2,x+px/2,0.02,0.06,z-px/2,z+px/2,(226,34,40),emit=True)
    R_=Rx(-1.05)@Rz(0.22)
    return transform(Q,lambda p:tuple(np.array([0,0,0])+R_@np.array(p)))
def bg(w,h,top=(14,10,40),bot=(2,2,8)):
    y=np.linspace(0,1,h)[:,None,None]; a=np.array(top)*(1-y)+np.array(bot)*y; a=np.repeat(a,w,1); a[::2]*=0.85
    return a
def render_disc(w,h,cam=(0,0.15,-2.9),fov=46):
    R2=Renderer(w,h,fog=(0,0,0)); img,_=zrender(R2,Camera.look(cam,(0,0,0)),[disc()],[((1.5,2,-3),(255,255,255),3.0)],fov=fov,fog_start=30,fog_end=60,ambient=0.6)
    a=np.asarray(img).astype(np.float32); m=(a.sum(2)>0)[...,None]
    return np.where(m,a,bg(w,h)), m
def tx(d,s,y,col,sc,w,x=None):
    x=(w-font.width(s,sc))//2 if x is None else x
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(1,1),(-1,-1),(1,-1),(-1,1)): font.text(d,s,x+ox*max(1,sc//2),y+oy*max(1,sc//2),(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def finish(a,scale,name):
    img=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); img=post.ps1(img)
    img=img.resize((img.width*scale,img.height*scale),Image.NEAREST); img.save(f'{OUTD}/{name}'); return img
# --- A: the disc ---
a,_=render_disc(160,160); im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); A=finish(np.asarray(im).astype(np.float32),5,'A_disc_profile.png')
# --- B: the loading screen ---
img=Image.fromarray(bg(160,160,(8,8,20),(0,0,0)).astype(np.uint8)); d=ImageDraw.Draw(img)
tx(d,'PLEASE INSERT',38,(200,200,210),1,160); tx(d,'DISC',58,(255,255,255),3,160); tx(d,'2',86,(230,40,46),5,160)
d.ellipse([68,132,92,156],outline=(200,200,210)); d.ellipse([77,141,83,147],fill=(200,200,210))
B=finish(np.asarray(img).astype(np.float32),5,'B_loading_profile.png')
# --- C: Chester holding the disc ---
R3=Renderer(160,160,fog=(0,0,0)); Qc,Dc=chester((0,0,0),0.0,lid=0.45,eye=1.25,mouth='smile')
dq=transform(disc(),lambda p:tuple(np.array(p)*0.36+np.array([0,0.62,0.02])))
cp=np.array((0.0,0.55,-1.55)); Dc=[x for x in Dc if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
img,_=zrender(R3,Camera.look(tuple(cp),(0,0.4,0)),[Qc,Dc,dq],[((1,2,-2),(255,255,255),2.5)],fov=44,fog_start=30,fog_end=60,ambient=0.6,bias=[1,1.004,1])
a=np.asarray(img).astype(np.float32); m=(a.sum(2)>0)[...,None]; a=np.where(m,a,bg(160,160,(40,18,10),(6,2,2)))
C=finish(a,5,'C_chester_profile.png')
# --- banner (2560x1440, safe area centre 1546x423) from A ---
w,h=512,288; a,m=render_disc(150,150,fov=46); ban=bg(w,h); ban[69:219,110:260]=np.where(m,a,ban[69:219,110:260])
img=Image.fromarray(ban.astype(np.uint8))
d=ImageDraw.Draw(img); tx(d,'INSERT',112,(255,255,255),3,w,262); tx(d,'DISC 2',138,(230,40,46),3,w,262); tx(d,'TINY RETRO GAME STORIES',170,(150,150,170),1,w,262)
ban=finish(np.asarray(img).astype(np.float32),5,'banner_2560x1440.png')
sh=Image.new('RGB',(2400,800),(0,0,0))
for i,im in enumerate((A,B,C)): sh.paste(im,(i*800,0))
sh.save(f'{OUTD}/concepts.png'); print('ok')
