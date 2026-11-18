"""Narration lint (PIPELINE phase 0 / step 1). Checks a script against the story shape in CHANNEL_PROMPT.md before any
rendering. Observations only; every line is a hint, the exit code is always 0.
  python tools/qa/script_lint.py tools/tts/scripts/v3.json        (list of [key, t0, text, dur, voice] as written by the TTS scripts)
  python tools/qa/script_lint.py narration.txt [--seconds 30]      (plain text, one sentence per line)
Reports: words, words/second (target 3.2-4.1 for a story, from the narration's own timing or --seconds), hook length
(first sentence 6-16 words), longest sentence (> 18 words is hard to follow), pivot ('You see', 'But', 'Then', 'Turns out'),
a question or 'wait' beat, short last sentence (<= 9 words), longest gap between lines and voices used (json only)."""
import sys, json, re, argparse
def load(p):
    if p.endswith('.json'):
        L=json.load(open(p)); return [(x[2],float(x[1]),float(x[3])) for x in L if len(x)>=4]
    return [(l.strip(),None,None) for l in open(p,encoding='utf-8') if l.strip()]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--seconds',type=float); a=ap.parse_args()
    L=load(a.file); sents=[]
    for t,_,_ in L: sents+= [s.strip() for s in re.split(r'(?<=[.!?])\s+',t) if s.strip()]
    wc=lambda s:len(re.findall(r"[A-Za-z0-9']+",s)); words=sum(wc(s) for s in sents)
    out=[]; tip=lambda ok,msg,hint='': out.append(('ok  ' if ok else 'HINT')+'  '+msg+('' if ok else '  -> '+hint))
    timed=[x for x in L if x[1] is not None]
    if timed: end=max(t0+d for _,t0,d in timed); span=end-min(t0 for _,t0,_ in timed)
    else: span=a.seconds
    if span:
        r=words/span; tip(3.2<=r<=4.1,f'pace {r:.2f} words/s ({words} words, {span:.1f} s)','3.5-4 w/s keeps a story moving; below 3 feels slow, above 4.2 is hard to follow')
    else: out.append(f'info  {words} words (give --seconds for pace)')
    h=wc(sents[0]); tip(6<=h<=16,f'hook: {h} words: "{sents[0]}"','state the paradox in one sentence of about 10-16 words')
    lg=max(sents,key=wc); tip(wc(lg)<=18,f'longest sentence {wc(lg)} words','split anything over 18 words')
    full=' '.join(sents).lower()
    tip(bool(re.search(r"\byou see\b|\bturns out\b|\bhere's the thing\b|\bthe reason\b|\bbecause\b",full)),'has a pivot to the reason (you see / turns out / because)','add one line that explains the real mechanism, ideally via an everyday analogy')
    tip(('?' in ' '.join(sents[1:])) or 'wait' in full,'has a question / wait beat after the hook','one "Wait, ...?" or question keeps curiosity up')
    tip(wc(sents[-1])<=9,f'last sentence {wc(sents[-1])} words: "{sents[-1]}"','end on a short ironic payoff, then stop')
    if timed:
        gaps=[timed[i+1][1]-(timed[i][1]+timed[i][2]) for i in range(len(timed)-1)]
        if gaps: m=max(gaps); k=gaps.index(m); tip(m<=1.2,f'longest gap between voice lines {m:.2f} s (after "{timed[k][0][:40]}")','a quiet stretch over ~1.2 s needs a sound or action to carry it')
        first=min(t0 for _,t0,_ in timed); tip(first<=0.6,f'voice starts at {first:.2f} s','start talking within the first second')
    print('\n'.join(out))
if __name__=='__main__': main()
