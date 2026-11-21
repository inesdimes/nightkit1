"""Voice for "Why don't enemies ever attack all at once?" (eq). 11 lines (v2, 21 Nov) (briefs/enemies_queue.md). Same pipeline as ss.py:
  python tools/tts/eq.py src ; <chatterbox python> tools/tts/vc.py eq ; python tools/tts/eq.py build vc ; python tools/tts/sc_check.py eq"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ss
S=1.18
D=[('1',[("Why don't enemies ever attack all at *once*?",S,0.3,1.5,0)]),
   ('2',[("Because they take a *number*.",S,0.1,0.5,0)]),
   ('3',[("Goblin forty-seven has been waiting for *three hours*.",S,0,0.5,0),("He practised one swing the whole time.",S,0,0.5,0.12)]),
   ('4',[("Forty-five got *hit*.",S,0.1,0.5,0),("Forty-six got *hit*.",S,0.1,0.5,0.1)]),
   ('5',[("Forty-seven stepped up...",S*0.95,0.1,0.5,0),("and the hero *saved and quit*.",S,-0.1,0.5,0.25)]),
   ('6',[("The dungeon went *dark*.",S,-0.1,0.5,0),("Forty-seven kept *waiting*.",S,-0.1,0.5,0.15)]),
   ('7',[("Forty-eight stood beside him.",S,-0.1,0.5,0),("Nobody *left* the queue.",S,-0.1,0.5,0.15)]),
   ('8',[("The next morning, the hero came *back*.",S,0.1,0.5,0),("Just for *him*.",S*0.95,0.1,0.5,0.15)]),
   ('9',[("Forty-seven lost in *one* hit.",S,0,0.5,0)]),
   ('10',[("He wasn't sad.",S,-0.1,0.5,0),("He had been *seen*.",S*0.95,-0.2,0.5,0.15)]),
   ('11',[("Now every goblin *frames* his ticket.",S*0.95,-0.3,1.0,0)])]
D=[(k,[(sx,sp,st-0.6,g,pause) for sx,sp,st,g,pause in s_]) for k,s_ in D]
if __name__=='__main__':
    if sys.argv[1]=='src': ss.src(D,'eq')
    else: ss.build(D,'eq',sys.argv[2])
