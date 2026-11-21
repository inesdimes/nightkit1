"""Voice for "Why don't enemies ever attack all at once?" (eq2) - NEW story (21 Nov, Enes: give it a new story): the Goblin rule written after the first hero. 11 lines.
  python tools/tts/eq2.py src ; <chatterbox python> tools/tts/vc.py eq2 ; python tools/tts/eq2.py build vc ; python tools/tts/sc_check.py eq2"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ss
S=1.18
D=[('1',[("Why don't enemies ever attack all at *once*?",S,0.3,1.5,0)]),
   ('2',[("Because of a *rule*.",S,0.1,0.5,0)]),
   ('3',[("It was written after the *first* hero came.",S,0,0.5,0)]),
   ('4',[("Nine goblins rushed him at *once*.",S,-0.1,0.5,0)]),
   ('5',[("He never came *back*.",S*0.95,-0.3,0.5,0)]),
   ('6',[("The goblins stood in the dark for a long time.",S*0.95,-0.2,0.5,0)]),
   ('7',[("Then the oldest one carved a *rule*...",S*0.95,-0.1,0.5,0),("one at a time.",S*0.95,-0.2,0.5,0.15)]),
   ('8',[("So the next hero *lived*.",S,0.1,0.5,0),("And the next.",S,0.0,0.5,0.12)]),
   ('9',[("Every goblin in this line knows he will *lose*.",S,-0.1,0.5,0)]),
   ('10',[("He steps up anyway.",S,0,0.5,0),("So you can reach level *two*.",S,0.1,0.5,0.15)]),
   ('11',[("It was never a fight.",S,-0.1,0.5,0),("It was a *welcome*.",S*0.92,-0.4,1.0,0.2)])]
D=[(k,[(sx,sp,st-0.6-(0.2 if k=='1' else 0),g,pause) for sx,sp,st,g,pause in s_]) for k,s_ in D]
if __name__=='__main__':
    if sys.argv[1]=='src': ss.src(D,'eq2')
    else: ss.build(D,'eq2',sys.argv[2])
