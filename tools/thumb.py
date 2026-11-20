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
if __name__=='__main__':
    YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60)
    R=os.path.join(ROOT,'..','renders')
    fp=load('four_phases'); make(fp,0.35,[('WHY DO BOSSES',130,WHT,13),('HAVE 3 PHASES?',250,YEL,13)],os.path.join(R,'four_phases','thumbnail.png'),hud=False)
    sc=load('stolen_car'); make(sc,sc.PRE+3.0,[('HIS CAR WAS',120,WHT,17),('STOLEN',250,RED,30),('900 TIMES',1580,YEL,22)],os.path.join(R,'stolen_car','thumbnail.png'),hud=False)
