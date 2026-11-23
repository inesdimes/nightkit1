"""Voice for "Why does the tutorial guy never come with you?" (tg, day 3, 22:00 slot, Format 3.0: several voices). Brief: briefs/tutorial_guy.md.
Narrator N = Kokoro bm_george S=1.22 -> ChatterboxVC (Enes timbre), same chain as four_phases / nw.  Characters = their own Kokoro voices, raw:
  G guide (bm_fable, warm, a little rushed) | H1 red hero (am_michael, bored) | H2 blue hero (af_nicole, quick) | H3 purple hero (am_adam, loud) | K knight (am_onyx, soft)
  python tools/tts/tg.py src ; <chatterbox python> tools/tts/vc.py tg ; python tools/tts/tg.py build vc ; python tools/tts/tg_check.py tg
  Enes's own takes: tts/tg_own/<key>_<i>.wav (list: briefs/ENES_VOICE_SCRIPTS.md), then python tools/tts/tg.py build own"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import multi
S=1.22; P=0.12
VOICES={'G':('bm_fable','en-gb'),'H1':('am_michael','en-us'),'H2':('af_nicole','en-us'),'H3':('am_adam','en-us'),'K':('am_onyx','en-us')}
# (text, speed, pitch st, gain dB, pause before s); narrator pitch is trimmed -0.6 st like nw.py (VC follows the source pitch)
_D=[('1','N',[("Why does the tutorial guy never come with you?",S,0.3-0.2,1.5,0)]),
    ('2','G',[("Press SPACE to jump!",1.14,1.0,1.0,0)]),
    ('3a','H1',[("Yeah, yeah!",0.98,-2.0,0.5,0)]),
    ('3b','H2',[("Is it safe?",1.15,0.0,0.5,0)]),
    ('3c','H3',[("Watch this!",1.12,4.5,1.0,0)]),
    ('4','N',[("Nobody ever looks back.",S*0.95,-0.2,0.5,0)]),
    ('5','N',[("Forty years ago, he tried it himself.",S,0,0.5,0)]),
    ('6','N',[("He saw the first slime, and froze.",S,-0.1,0.5,0)]),
    ('7','N',[("He walked back.",S*0.95,-0.1,0.5,0),("He has stood here ever since.",S*0.95,-0.3,0.5,P)]),
    ('8','G',[("Press SPACE to jump.",0.92,0.0,-3.0,0)]),
    ('9','N',[("Then one knight finished the lesson,",S,0,0.5,0),("and didn't leave.",S*0.95,-0.1,0.5,0.1)]),
    ('10','K',[("Just one step.",0.88,-1.0,-1.0,0)]),
    ('11','N',[("The old man looked at the grass on the other side.",S*0.95,-0.1,0.5,0)]),
    ('12','N',[("He took one step.",S*0.92,-0.3,0.5,0)]),
    ('13','N',[("Then he went back to his spot.",S,-0.1,0.5,0),("But now he leaves the gate open.",S*0.92,-0.4,1.0,P+0.05)])]
D=[(k,spk,[(tx,sp,(st-0.6) if spk=='N' else st,g,pause) for tx,sp,st,g,pause in ss]) for k,spk,ss in _D]
if __name__=='__main__': multi.main(D,VOICES,'tg')
