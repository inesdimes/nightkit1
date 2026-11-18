"""Word-level emphasis for Kokoro lines. Kokoro has no stress control, so we (1) synthesize the whole sentence for natural flow,
(2) estimate each word's span (standalone word lengths mapped onto the sentence's voiced time, boundaries snapped to energy valleys),
(3) re-shape only the marked words: slower, higher pitch (rubberband), louder, with short crossfades.
Mark words in the text with *word* (strong) or **word** (extra strong)."""
import re, subprocess, os, tempfile
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
SR=48000
def synth(k,text,voice,speed,lang):
    """Kokoro output (24 kHz) -> 48 kHz mono"""
    a,sr=k.create(text,voice=voice,speed=speed,lang=lang); return resample_poly(a,SR,sr) if sr!=SR else a
def parse(text):
    """'The *lightning* is **here**.' -> (plain text, [(word index, level)])"""
    words=[]; marks=[]
    for tok in text.split():
        lvl=2 if tok.startswith('**') else (1 if tok.startswith('*') else 0)
        w=tok.replace('*','')
        if lvl: marks.append((len(words),lvl))
        words.append(w)
    return ' '.join(words),words,marks
def trim(a,thr=0.01,pre=240,post=480):
    nz=np.where(np.abs(a)>thr)[0]; return a[max(0,nz[0]-pre):nz[-1]+post] if len(nz) else a
def env(a,w=0.01):
    n=max(1,int(w*SR)); return np.sqrt(np.convolve(a**2,np.ones(n)/n,'same'))
def word_bounds(k,voice,speed,lang,words,full):
    """returns [(start,end) sample] per word inside `full` (the synthesized sentence at SR)"""
    clean=[re.sub(r"[^A-Za-z0-9' -]",'',w) for w in words]
    lens=[]
    for w in clean:
        a=trim(synth(k,w,voice,speed,lang),0.02,0,0); lens.append(len(a)/SR)
    e=env(full); thr=max(e.max()*0.03,1e-4); on=e>thr
    idx=np.where(on)[0]; s0,s1=idx[0],idx[-1]
    # voiced clusters separated by silences >= 120 ms; words are grouped at punctuation (the comma / full stop pauses)
    clusters=[]; st=idx[0]; prev=idx[0]
    for x in idx[1:]:
        if x-prev>0.12*SR: clusters.append((st,prev)); st=x
        prev=x
    clusters.append((st,prev))
    groups=[[]]
    for wi,w in enumerate(words):
        groups[-1].append(wi)
        if w[-1:] in ',.;:!?' and wi<len(words)-1: groups.append([])
    if len(clusters)!=len(groups): clusters=[(s0,s1)]; groups=[list(range(len(words)))]
    gap=0.03*SR; b=[None]*len(words)
    for (c0,c1),g in zip(clusters,groups):
        wl=[lens[i] for i in g]; avail=(c1-c0)-gap*(len(g)-1); sc=avail/(sum(wl)*SR); x=c0
        for i,l in zip(g,wl): b[i]=[x,x+l*SR*sc]; x+=l*SR*sc+gap
    # snap each boundary inside a cluster to the lowest-energy point within +-70 ms
    edges=[b[0][0]]
    for i in range(len(b)-1):
        if i in [g[-1] for g in groups]: edges.append(b[i][1]); edges.append(b[i+1][0]); continue
        m=(b[i][1]+b[i+1][0])/2; lo=int(max(s0,m-0.07*SR)); hi=int(min(s1,m+0.07*SR)); v=lo+int(np.argmin(e[lo:hi])); edges.append(v)
    edges.append(b[-1][1])
    # edges list: start, then per internal boundary either one point or two (end of group, start of next)
    res=[]; k_=1; cur=int(edges[0])
    for i in range(len(b)):
        if i==len(b)-1: res.append((cur,int(edges[-1]))); break
        if i in [g[-1] for g in groups]: res.append((cur,int(edges[k_]))); cur=int(edges[k_+1]); k_+=2
        else: res.append((cur,int(edges[k_]))); cur=int(edges[k_]); k_+=1
    return res
def shape(x,pitch_st,tempo,gain_db):
    p=os.path.join(tempfile.gettempdir(),'nk_emph_in.wav'); q=os.path.join(tempfile.gettempdir(),'nk_emph_out.wav'); sf.write(p,x,SR)
    af=f"rubberband=pitch={2**(pitch_st/12):.4f}:tempo={tempo:.4f}" if (abs(pitch_st)>0.01 or abs(tempo-1)>0.01) else 'anull'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',p,'-af',af,'-ar',str(SR),'-ac','1',q],check=True)
    y,_=sf.read(q); return y*10**(gain_db/20)
LEVELS={1:(2.0,0.97,3.5),2:(3.0,0.9,5.0)}
FILL=1.18                                   # unmarked runs are spoken faster so the stressed words stand out and the line stays short      # level -> (pitch semitones, tempo, gain dB)
def apply(full,bounds,marks,xf=int(0.02*SR)):
    """re-shape the marked words (shaped slice crossfaded in and out of the original audio)"""
    res=[]; pos=0; fi=np.linspace(0,1,xf); fo=1-fi
    for wi,lvl in sorted(marks):
        a,b=bounds[wi]; st,tp,g=LEVELS[lvl]
        pre=max(pos,a-xf); post=min(len(full)-xf,b+xf)
        seg=shape(full[pre:post],st,tp,g)
        if len(seg)<3*xf: continue
        res.append(full[pos:pre])
        res.append(full[pre:pre+xf]*fo+seg[:xf]*fi)                    # fade the word in
        res.append(seg[xf:-xf])
        res.append(seg[-xf:]*fo+full[post:post+xf]*fi)                 # fade back to the original flow
        pos=post+xf
    res.append(full[pos:]); return np.concatenate(res)

# ---------------- chunked mode (used by lm.py): exact placement, no alignment guessing ----------------
def render_chunks(k,voice,speed,lang,text,pitch=0.0,gain=0.0,gap=0.0,comma_gap=0.04):
    """Synthesize the sentence as chunks split at the marked words, so the stressed word is exactly where we want it.
    Unmarked runs keep the base speed/pitch/gain; a marked word is slower, higher and louder (LEVELS). Chunks end in a comma
    (continuation intonation) except the last one, which keeps the sentence's own punctuation."""
    plain,words,marks=parse(text); lv=dict(marks); chunks=[]; cur=[]; cur_l=0
    for i,w in enumerate(words):
        l=lv.get(i,0)
        if cur and l!=cur_l: chunks.append((cur,cur_l)); cur=[]
        cur.append(w); cur_l=l
    chunks.append((cur,cur_l)); parts=[]; xf=int(0.012*SR)
    for ci,(ws,l) in enumerate(chunks):
        last=ci==len(chunks)-1; t=' '.join(ws)
        if not last and t[-1] not in ',.;:!?': t+=','
        if l==0: sp,st,g=speed*FILL,pitch,gain
        else: dst,tp,dg=LEVELS[l]; sp,st,g=speed*tp,pitch+dst,gain+dg
        a=trim(synth(k,t,voice,sp,lang),0.01,120,360)
        if abs(st)>0.01: a=shape(a,st,1.0,0)
        a=a*10**(g/20)
        parts.append((a,comma_gap if (not last and t.endswith(',') and ws[-1].endswith(',')) else gap))
    out=parts[0][0]
    for (a,_),(_,gp) in zip(parts[1:],parts[:-1]):
        sil=np.zeros(int(gp*SR)); out=np.concatenate([out,sil]);
        n=min(xf,len(out),len(a)); out[-n:]=out[-n:]*np.linspace(1,0,n)+a[:n]*np.linspace(0,1,n); out=np.concatenate([out,a[n:]])
    return out
