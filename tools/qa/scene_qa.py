"""Scene-based preview + visual-error checks for nightkit shorts (PIPELINE.md, phases 2-4).

Usage:  python tools/qa/scene_qa.py examples/final_boss.py [--no-sheets] [--step 1]
The script must define QA = dict(...) (see examples/final_boss.py). Writes out/qa/<name>/report.md, one preview
contact sheet per scene (scene_XX.png, 180x320 per frame = internal resolution) and overview.png.

Automatic checks (every frame unless --step):
  teleport      character base moves > 0.3 m or turns > 0.7 rad between two frames inside one scene
  cut-jump      character position differs > 0.5 m across a scene cut (story-time continuity) unless allowed
  weapon        sword state changes ('hip'/'hand'/'back'/'floor'/...) that are not declared in QA['weapon_events']
  barrier       a body passes through the barrier plane outside the declared crossing windows
  wall/floor    geometry inside walls or under the floor
  intersect     knight and boss bodies interpenetrate
  camera        camera inside a wall, or closer than 0.25 m to a visible character (near-plane clipping)
  text          on-screen strings wider than the frame or using glyphs the font lacks
Things a script cannot judge (readability of the action, faces, morphing) are reviewed on the contact sheets."""
import os, sys, math, importlib.util, argparse
import numpy as np
from PIL import Image, ImageDraw
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); sys.path.insert(0,ROOT)
from nightkit import font

def load(path):
    sys.path.insert(0,os.path.dirname(os.path.abspath(path)))
    spec=importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0],path); m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m

def hexes(Q):
    """group the face list into closed 6-face blocks (boxes / limb segments); returns list of (verts(8,3), faces)"""
    out=[]; i=0
    while i+6<=len(Q):
        g=Q[i:i+6]; V=np.unique(np.round(np.array([p for q in g for p in q['p']]),5),axis=0)
        if len(V)==8: out.append((V,g)); i+=6
        else: i+=1
    return out
def inside_hex(P,V,faces,margin=0.02):
    """points P (n,3) strictly inside the convex block (shrunk by margin)"""
    c=V.mean(0); ok=np.ones(len(P),bool)
    for q in faces:
        n=np.array(q['n']); fc=np.array(q['c']); s=np.sign((c-fc)@n) or 1.0
        ok&=((P-fc)@n)*s>margin
    return ok
def verts(Q,skip_emit=True): return np.array([p for q in Q if not (skip_emit and q.get('emit')) for p in q['p']]) if Q else np.zeros((0,3))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--no-sheets',action='store_true'); ap.add_argument('--step',type=int,default=1)
    ap.add_argument('--scenes',default=''); a=ap.parse_args()
    m=load(a.script); QA=m.QA; name=os.path.splitext(os.path.basename(a.script))[0]
    outd=os.path.join(ROOT,'out','qa',name); os.makedirs(outd,exist_ok=True)
    FPS=QA['fps']; N=int(round(QA['dur']*FPS)); scenes=QA['scenes']; W=QA['W']
    def scene_of(t):
        for i,s in enumerate(scenes):
            if s['t0']<=t<s['t1']: return i
        return len(scenes)-1
    issues=[]; prev=None; weapons={}; derived={}
    allowed_w=QA.get('weapon_events',[]); allowed_cross=QA.get('crossings',[]); allowed_jump=QA.get('allow_jump',[])
    BZ=QA['barrier_z']; GW=QA['gate_w']; GH=QA['gate_h']
    def add(t,kind,msg): issues.append((t,scenes[scene_of(t)]['id'],kind,msg))
    for f in range(0,N,a.step):
        t=f/FPS; si=scene_of(t); sc=scenes[si]; ks=QA['knight'](t); bs=QA['boss'](t); cam=QA['camera'](t)
        st=dict(knight=ks,boss=bs)
        geo={}
        for who,s_ in st.items():
            if s_ is None: continue
            Q=QA['knight_fn' if who=='knight' else 'boss_fn'](**s_); geo[who]=Q
            sw=s_.get('sword','hip' if who=='knight' else 'hand')
            if who in weapons and weapons[who][1]!=sw:
                ok=any(w==who and abs(t-tw)<0.6 and fr==weapons[who][1] and to==sw for w,tw,fr,to in allowed_w)
                if not ok: add(t,'weapon',f"{who}'s sword changes {weapons[who][1]} -> {sw} without an on-screen action")
            weapons[who]=(t,sw)
            if sc.get('set','inside')=='outside': continue
            V=verts(Q); base=np.array(s_['base'],float)
            # barrier
            door=(np.abs(V[:,0])<GW)&(V[:,1]<GH)
            crossing=any(w==who and t0<=t<=t1 for w,t0,t1 in allowed_cross)
            if not crossing:
                if base[2]>BZ:
                    pen=BZ-V[door,2].min() if door.any() else -1
                    if pen>0.03: add(t,'barrier',f"{who} reaches through the barrier from inside ({pen*100:.0f} cm)")
                else:
                    pen=V[door,2].max()-BZ if door.any() else -1
                    if pen>0.03: add(t,'barrier',f"{who} reaches through the barrier from outside ({pen*100:.0f} cm)")
            # walls / floor
            if base[2]>0.3:
                if (np.abs(V[:,0])>7.97).any() or (V[:,2]>17.97).any(): add(t,'wall',f'{who} geometry inside an arena wall')
            elif base[2]<-0.3:
                if (np.abs(V[:,0])>QA['corridor_w']+0.02).any(): add(t,'wall',f'{who} geometry inside a corridor wall ({np.abs(V[:,0]).max():.2f} m)')
            if V[:,1].min()<-0.04: add(t,'floor',f'{who} under the floor ({-V[:,1].min()*100:.0f} cm)')
        # knight vs boss
        if 'knight' in geo and 'boss' in geo and sc.get('set','inside')!='outside':
            kb=np.array(ks['base']); bb=np.array(bs['base'])
            if np.linalg.norm(kb-bb)<3.5:
                KV=verts(geo['knight']); BV=verts(geo['boss']); hit=0
                for Vh,fc in hexes([q for q in geo['boss'] if not q.get('emit')]): hit+=int(inside_hex(KV,Vh,fc).sum())
                for Vh,fc in hexes([q for q in geo['knight'] if not q.get('emit')]): hit+=int(inside_hex(BV,Vh,fc).sum())
                if hit: add(t,'intersect',f'knight and boss interpenetrate ({hit} vertices)')
        # camera
        if cam is not None and sc.get('set','inside')!='outside':
            cp=np.array(cam,float)
            in_arena=(abs(cp[0])<7.8 and 0.15<cp[2]<17.8 and 0.05<cp[1]<9.5); in_corr=(abs(cp[0])<QA['corridor_w']-0.12 and -14.8<cp[2]<-0.1)
            in_door=(abs(cp[0])<GW-0.1 and -0.1<=cp[2]<=0.15)
            if not (in_arena or in_corr or in_door): add(t,'camera',f'camera inside a wall / outside the set ({tuple(np.round(cp,2))})')
            for who,Q in geo.items():
                if who=='knight' and sc.get('pov'): continue
                d=np.linalg.norm(verts(Q,False)-cp,axis=1).min()
                if d<0.25: add(t,'camera',f'camera clips the {who} ({d*100:.0f} cm)')
        # continuity
        if prev is not None:
            pt,psi,pst=prev
            for who in ('knight','boss'):
                a_,b_=pst.get(who),st.get(who)
                if a_ is None or b_ is None: continue
                if scenes[si].get('set')=='outside' or scenes[psi].get('set')=='outside': continue
                d=np.linalg.norm(np.array(a_['base'])-np.array(b_['base'])); dy=abs(((b_['yaw']-a_['yaw']+math.pi)%(2*math.pi))-math.pi)
                if psi==si:
                    if d>0.3*a.step: add(t,'teleport',f'{who} jumps in one frame ({d:.2f} m)')
                    if dy>0.7*a.step: add(t,'teleport',f'{who} turns too fast ({math.degrees(dy):.0f} deg/frame)')
                elif d>0.5 and not any(w==who and abs(t-tj)<0.1 for w,tj in allowed_jump):
                    add(t,'cut-jump',f'{who} moves {d:.2f} m across the cut {scenes[psi]["id"]} -> {scenes[si]["id"]}')
        prev=(t,si,st)
        for who,s_ in st.items():
            if s_ is None: continue
            d=derived.setdefault((si,who),{}); d.setdefault('start',(t,s_)); d['end']=(t,s_)
    # text
    for label,s_,scl in QA['texts']():
        try: font.check(s_)
        except ValueError as e: issues.append((0,'-','text',f'{label}: {e}'))
        if font.width(s_,scl)>W-6: issues.append((0,'-','text',f'{label}: "{s_}" is {font.width(s_,scl)} px wide (> {W-6})'))
    # merge identical issues (same check + same message stem) into time ranges
    merged=[]; gap=2.5/FPS*a.step
    for t,sid,k,msg in sorted(issues,key=lambda x:(x[2],x[3].split(' (')[0],x[0])):
        stem=msg.split(' (')[0]
        if merged and merged[-1][2]==k and merged[-1][3]==stem and t-merged[-1][1]<=gap: merged[-1][1]=t; merged[-1][4]+=1; merged[-1][6]=msg if msg>merged[-1][6] else merged[-1][6]
        else: merged.append([t,t,k,stem,1,sid,msg])
    merged.sort(key=lambda x:x[0])
    # report
    L=[f'# Scene QA - {name}','',f'{len(scenes)} scenes, {N} frames @ {FPS} fps, checked every {a.step} frame(s).','']
    L+=['## Scene manifest','','| # | id | time | main action | camera | knight start -> end | boss start -> end | held objects |','|---|---|---|---|---|---|---|---|']
    for i,s in enumerate(scenes):
        def fmt(who):
            d=derived.get((i,who))
            if not d: return '-'
            a0=np.round(d['start'][1]['base'],1); a1=np.round(d['end'][1]['base'],1); return f'({a0[0]:.1f},{a0[2]:.1f}) -> ({a1[0]:.1f},{a1[2]:.1f})'
        def held(who,default):
            d=derived.get((i,who))
            if not d: return ''
            s0=d['start'][1].get('sword',default); s1=d['end'][1].get('sword',default); return f'{who} sword {s0}'+('' if s0==s1 else f'->{s1}')
        c0=QA['camera'](s['t0']); c1=QA['camera'](max(s['t0'],s['t1']-1e-3))
        cs='outside' if c0 is None else f'({c0[0]:.1f},{c0[1]:.1f},{c0[2]:.1f})'+('' if c1 is None or np.allclose(c0,c1,atol=0.05) else f' -> ({c1[0]:.1f},{c1[1]:.1f},{c1[2]:.1f})')
        L.append(f"| {i} | {s['id']} | {s['t0']:.2f}-{s['t1']:.2f} | {s['action']} | {cs} | {fmt('knight')} | {fmt('boss')} | {held('knight','hip')}; {held('boss','hand')} |")
    L+=['','## Automatic checks','']
    if not merged: L.append('No issues found.')
    else:
        L+=['| time | scene | check | issue | frames |','|---|---|---|---|---|']
        for t0,t1,k,msg,cnt,sid,full in merged: L.append(f'| {t0:.2f}-{t1:.2f} | {sid} | {k} | {full} | {cnt} |')
    L+=['','## Manual review (contact sheets)','','For every scene sheet: faces/clothing unchanged, limbs and weapons correct, contact with doors/objects, the action readable without narration, text undistorted.','']
    open(os.path.join(outd,'report.md'),'w').write('\n'.join(L)+'\n')
    print('\n'.join(L[-(len(merged)+8):]) if merged else 'no issues'); print('report:',os.path.join(outd,'report.md'))
    if a.no_sheets: return
    only=set(a.scenes.split(',')) if a.scenes else None
    thumbs=[]
    for i,s in enumerate(scenes):
        if only and s['id'] not in only: continue
        ts=[s['t0']+(s['t1']-s['t0'])*u for u in (0.0,0.25,0.5,0.75)]+[s['t1']-1.0/FPS]
        ims=[QA['frame'](t) for t in ts]; sh=Image.new('RGB',(5*182,320+14),(0,0,0)); d=ImageDraw.Draw(sh)
        for k,(im,t) in enumerate(zip(ims,ts)): sh.paste(im,(k*182,14)); font.text(d,f'{t:.2f}',k*182+2,3,(255,255,255),1,None)
        lab=''.join(c if c in font.FONT else ' ' for c in f"{i}: {s['id']}".upper())[:28]
        font.text(d,lab,5*182-170,3,(255,210,60),1,None)
        sh.resize((sh.width*2,sh.height*2),Image.NEAREST).save(os.path.join(outd,f'scene_{i:02d}.png')); thumbs.append(ims[2])
    if thumbs and not only:
        ov=Image.new('RGB',(len(thumbs)*91,160))
        for k,im in enumerate(thumbs): ov.paste(im.resize((90,160),Image.NEAREST),(k*91,0))
        ov.save(os.path.join(outd,'overview.png'))
if __name__=='__main__': main()
