"""Thumbnails (1080x1920) for finished shorts: one hero frame (no subtitles) + big outlined pixel-font text.
  python tools/thumb.py            # writes ../renders/four_phases/thumbnail.png and ../renders/stolen_car/thumbnail.png"""
import os, sys, importlib.util
import numpy as np
from PIL import Image, ImageDraw
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,ROOT); sys.path.insert(0,os.path.join(ROOT,'examples'))
from nightkit import font, post
def load(name):
    spec=importlib.util.spec_from_file_location(name,os.path.join(ROOT,'examples',name+'.py')); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
def big(d,s,y,col,sc,W=1080,o=8):
    sc=min(sc,(W-60)//(len(s)*6-1)); o=max(4,sc//3)
    x=(W-font.width(s,sc))//2
    for ox in range(-o,o+1,4):
        for oy in range(-o,o+1,4): font.text(d,s,x+ox,y+oy,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def make(mod,t,lines,out,hud=True):
    img=mod.render3d(t)[0]
    if isinstance(img,tuple): img=img[0]
    low=img if isinstance(img,Image.Image) else Image.fromarray(img)
    if hud: d=ImageDraw.Draw(low); mod.hud(d,t)
    arr=post.upscale(low,6); im=Image.fromarray(np.asarray(arr).astype(np.uint8)); d=ImageDraw.Draw(im)
    for s,y,col,sc in lines: big(d,s,y,col,sc)
    os.makedirs(os.path.dirname(out),exist_ok=True); im.save(out); print(out)
if __name__=="__main__" and len(sys.argv)==1:
    YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60)
    R=os.path.join(ROOT,'..','renders')
    fp=load('four_phases'); make(fp,0.35,[('WHY DO BOSSES',130,WHT,13),('HAVE 3 PHASES?',250,YEL,13)],os.path.join(R,'four_phases','thumbnail.png'),hud=False)
    sc=load('stolen_car'); make(sc,sc.PRE+3.0,[('HIS CAR WAS',120,WHT,17),('STOLEN',250,RED,30),('900 TIMES',1580,YEL,22)],os.path.join(R,'stolen_car','thumbnail.png'),hud=False)
    # 21 Nov 2026: day-1 videos (the hook frame / the goblin rush, text-only overlay, no subtitles)
    ss=load('skip_speech'); make(ss,0.7,[('HIS SPEECH',150,WHT,13),('30 YEARS',265,YEL,17),('SKIPPED',395,RED,17)],os.path.join(R,'skip_speech','thumbnail.png'),hud=False)
    eq=load('enemies_queue'); make(eq,8.3,[('WHY GOBLINS',370,WHT,15),('NEVER',505,RED,30),('ATTACK TOGETHER',735,YEL,11)],os.path.join(R,'enemies_queue','thumbnail.png'),hud=False)

def make_hd(name,t,lines,out,tts_dir=None):
    """hd-figure shorts (dragon_taxes, forget_potion): frame_low + upscale, no subtitles / overlays. tts_dir = the posted voice's timing."""
    if tts_dir: os.environ['TTS_DIR']=tts_dir
    mod=load(name); img,_=mod.frame_low(t)
    im=Image.fromarray(np.clip(post.upscale(img,mod.S),0,255).astype(np.uint8)).resize((1080,1920),Image.LANCZOS); d=ImageDraw.Draw(im)
    for s,y,col,sc in lines: big(d,s,y,col,sc)
    os.makedirs(os.path.dirname(out),exist_ok=True); im.save(out); print(out)
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='hd':
    # 23 Nov 2026: the Betül versions Enes chose to post (times are 1x, Betül timing)
    YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); R=os.path.join(ROOT,'..','renders')
    which=sys.argv[2]
    DTL=[('THEY SENT HIM',110,WHT,15),('TO SLAY IT',235,YEL,17),('WRONG VILLAIN',1620,RED,15)]
    if which=='dt': make_hd('dragon_taxes',0.7,DTL,os.path.join(R,'dragon_taxes','thumbnail.png'),os.path.join(R,'dragon_taxes','betul_tts'))
    if which=='dt_b': make_hd('dragon_taxes',31.1,DTL,os.path.join(R,'dragon_taxes','thumbnail_b.png'),os.path.join(R,'dragon_taxes','betul_tts'))
    if which=='fpo': make_hd('forget_potion',26.75,[('ONE POTION',1380,WHT,17),('SAVES HER',1510,YEL,17),('HE FORGETS HER',1660,RED,12)],
                             os.path.join(R,'forget_potion','thumbnail.png'),os.path.join(R,'forget_potion','betul_tts'))

def make_v(name,t,lines,out,lang='en',hud=None):
    """24 Nov 2026: voiced EN / TR-subtitle shorts (boss_health_bar, the_last_echo). lang sets SUB_LANG so in-picture HUD / labels match; no subtitles."""
    os.environ['SUB_LANG']=lang; mod=load(name); r=mod.frame_low(t); img=r[0] if isinstance(r,tuple) else r
    im=Image.fromarray(np.clip(post.upscale(img,mod.S),0,255).astype(np.uint8)).resize((1080,1920),Image.LANCZOS)
    if hud: getattr(mod,hud)(im,t)
    d=ImageDraw.Draw(im)
    for s,y,col,sc in lines: big(d,s,y,col,sc)
    os.makedirs(os.path.dirname(out),exist_ok=True); im.save(out); print(out)
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='voiced':
    YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); R=os.path.join(ROOT,'..','renders')
    B=os.path.join(R,'boss_health_bar'); L=os.path.join(R,'the_last_echo')
    make_v('boss_health_bar',2.0,[('EVERY HIT',1360,WHT,17),('KILLS A',1500,YEL,17),('VILLAGER',1650,RED,19)],os.path.join(B,'thumbnail_en.png'),'en','hud_overlay')
    make_v('boss_health_bar',2.0,[('HER DARBE',1360,WHT,17),('BİR KÖYLÜYÜ',1500,YEL,15),('ÖLDÜRÜYOR',1650,RED,19)],os.path.join(B,'thumbnail_tr.png'),'tr','hud_overlay')
    make_v('the_last_echo',18.0,[('3 KNOCKS',150,YEL,24),('HIS BROTHER',1490,WHT,15),('WAS DYING',1650,RED,18)],os.path.join(L,'thumbnail_en.png'),'en')
    make_v('the_last_echo',18.0,[('3 VURUŞ',150,YEL,24),('KARDEŞİ',1490,WHT,18),('ÖLÜYORDU',1650,RED,18)],os.path.join(L,'thumbnail_tr.png'),'tr')
