"""Voice for "Why do heroes smash every pot?" (pt, day 3, 02:00 slot, Format 3.0: several voices). Brief: briefs/pots.md.
Narrator N = Kokoro bm_george S=1.22 -> ChatterboxVC (Enes timbre). Characters = own Kokoro voices, raw:
  W old woman (bf_emma, slow, warm) | H1 grey hero (am_adam, gruff) | H2 blue hero (bm_lewis, sneering) | H3 green hero (am_michael, in a hurry) | K knight (am_onyx, soft, same as tutorial_guy)
  python tools/tts/pt.py src ; <chatterbox python> tools/tts/vc.py pt ; python tools/tts/pt.py build vc ; python tools/tts/sc_check.py pt
  Enes's own takes: tts/pt_own/<key>_<i>.wav, then python tools/tts/pt.py build own"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import multi
S=1.22; P=0.12
VOICES={'W':('bf_emma','en-gb'),'H1':('am_adam','en-us'),'H2':('bm_lewis','en-gb'),'H3':('am_michael','en-us'),'K':('am_onyx','en-us')}
_D=[('1','N',[("Why do heroes smash every pot?",S,0.1,1.5,0)]),
    ('2','W',[("Come in, dear. Mind the step.",0.95,-1.5,0.5,0)]),
    ('3a','H1',[("Ha!",1.0,-3.0,1.5,0)]),
    ('3b','H2',[("Is that all?",1.05,3.0,0.5,0)]),
    ('3c','H3',[("Out of my way!",1.15,3.0,1.0,0)]),
    ('4','N',[("Forty years.",S*0.95,-0.1,0.5,0),("Nobody ever said thank you.",S*0.95,-0.2,0.5,P)]),
    ('5','N',[("Her son left to be a hero,",S,0,0.5,0),("and never wrote.",S*0.92,-0.3,0.5,0.1)]),
    ('6','N',[("So every hero leaves her house with a coin.",S,0,0.5,0),("Maybe someone is doing the same for him.",S*0.95,-0.1,0.5,P)]),
    ('7','N',[("One knight walked in,",S,0,0.5,0),("and didn't swing.",S*0.95,-0.1,0.5,0.1)]),
    ('8','K',[("I won't. Sorry.",0.88,-2.5,-1.0,0)]),
    ('9','W',[("Oh... sit, sit. Tea?",0.95,-1.0,0.5,0)]),
    ('10','N',[("That pot is still on the shelf.",S,-0.1,0.5,0),("The only one she never had to replace.",S*0.92,-0.4,1.0,P+0.05)])]
D=[(k,spk,[(tx,sp,(st-0.6) if spk=='N' else st,g,pause) for tx,sp,st,g,pause in ss]) for k,spk,ss in _D]
if __name__=='__main__': multi.main(D,VOICES,'pt')
