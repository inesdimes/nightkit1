"""Word-level emphasis for Kokoro lines. Kokoro has no stress control, so we (1) synthesize the WHOLE sentence (natural flow),
(2) read the exact phoneme timings from the model (needs tts/kokoro-dur.onnx, see make_dur_model()), which gives every word's span,
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
def shape(x,pitch_st,tempo,gain_db):
    p=os.path.join(tempfile.gettempdir(),'nk_emph_in.wav'); q=os.path.join(tempfile.gettempdir(),'nk_emph_out.wav'); sf.write(p,x,SR)
    af=f"rubberband=pitch={2**(pitch_st/12):.4f}:tempo={tempo:.4f}" if (abs(pitch_st)>0.01 or abs(tempo-1)>0.01) else 'anull'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',p,'-af',af,'-ar',str(SR),'-ac','1',q],check=True)
    y,_=sf.read(q); return y*10**(gain_db/20)
LEVELS={1:(1.8,0.9,3.0),2:(2.8,0.82,4.5)}      # level -> (pitch semitones, tempo, gain dB) applied to the stressed word only      # level -> (pitch semitones, tempo, gain dB)
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


def make_dur_model(src,dst):
    """Copy the Kokoro onnx model with an extra 'duration' output (per-token frame counts), which kokoro-onnx turns into phoneme timings."""
    import onnx
    from onnx import helper, TensorProto
    m=onnx.load(src); g=m.graph
    g.node.append(helper.make_node('Cast',['/encoder/Cast_output_0'],['duration'],to=TensorProto.INT64,name='/export/duration_cast'))
    g.output.append(helper.make_tensor_value_info('duration',TensorProto.INT64,None)); onnx.save(m,dst)
def word_spans(timings,n_words,sr_out):
    """exact (start, end) sample per word from the phoneme timings (words are separated by space tokens; punctuation is not part of a word)"""
    spans=[]; cur=None
    for t in timings:
        if t.phoneme==' ':
            if cur: spans.append(cur); cur=None
        elif t.phoneme in ',.;:!?-': continue
        else:
            if cur is None: cur=[t.start,t.end]
            else: cur[1]=t.end
    if cur: spans.append(cur)
    if len(spans)!=n_words: raise ValueError(f'{len(spans)} phoneme words vs {n_words} text words')
    return [(int(a*sr_out),int(b*sr_out)) for a,b in spans]
class _Tm:
    def __init__(s,p,a,b): s.phoneme,s.start,s.end=p,a,b
def create_timed(k,text,voice,speed,lang):
    """Fallback for kokoro-onnx 0.4.x (no create_timed): one pass over the duration model (kokoro-dur.onnx), which outputs
    per-token frame counts next to the audio. Returns (audio 24 kHz, sr, [phoneme timings in s]). One batch only (short sentences)."""
    ph=k.tokenizer.phonemize(text,lang)
    chars=[c for c in ph if k.tokenizer.tokenize(c)]
    toks=np.array(k.tokenizer.tokenize(ph),dtype=np.int64); assert len(toks)==len(chars) and len(toks)<=510
    style=k.get_voice_style(voice)[len(toks)]
    names=[i.name for i in k.sess.get_inputs()]
    if 'input_ids' in names: inp={'input_ids':[[0,*toks,0]],'style':np.array(style,dtype=np.float32),'speed':np.array([speed],dtype=np.int32)}
    else: inp={'tokens':[[0,*toks,0]],'style':style,'speed':np.ones(1,dtype=np.float32)*speed}
    outs=k.sess.run(None,inp); onames=[o.name for o in k.sess.get_outputs()]
    audio=outs[0].squeeze(); dur=outs[onames.index('duration')].squeeze().astype(float)
    sec=len(audio)/24000/dur.sum()                                   # seconds per duration frame
    edges=np.concatenate([[0],np.cumsum(dur)])*sec
    T=[_Tm(c,edges[i+1],edges[i+2]) for i,c in enumerate(chars)]   # token i+1 (0 = leading pad)
    return audio,24000,T
def render(k,voice,speed,lang,text,pitch=0.0,gain=0.0):
    """whole-sentence synthesis + local stress on the marked words (exact word spans). Returns 48 kHz audio (not trimmed)."""
    plain,words,marks=parse(text)
    a,sr,T=k.create_timed(plain,voice,speed,lang) if hasattr(k,'create_timed') else create_timed(k,plain,voice,speed,lang)
    full=resample_poly(a,SR,sr) if sr!=SR else a
    y=apply(full,word_spans(T,len(words),SR),marks) if marks else full
    if abs(pitch)>0.01: y=shape(y,pitch,1.0,0)
    return y*10**(gain/20)
