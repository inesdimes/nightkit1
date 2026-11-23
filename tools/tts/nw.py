"""Voice for "Why do NPCs repeat the same line?" (nw, day 2, Tone 2.0: fp pace: S=1.22, pauses 0-0.15 s). 13 lines (briefs/npc_well.md). Same pipeline as ss.py:
  python tools/tts/nw.py src ; <chatterbox python> tools/tts/vc.py nw ; python tools/tts/nw.py build vc ; python tools/tts/sc_check.py nw
Per sentence: (text, speed, pitch semitones, gain dB, pause before s). No stress marks (Tone 2.0)."""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ss
S=1.22; P=0.12
D=[('1',[("Why has this man said the same line for forty years?",S,0.3,1.5,0)]),
   ('2',[("It is the only thing he says.",S,0,0.5,0)]),
   ('3',[("To every hero.",S,0,0.5,0),("Every day.",S,-0.1,0.5,P),("The well is dry.",S,-0.2,0.5,P)]),
   ('4',[("Nobody ever asked him why.",S*0.95,-0.2,0.5,0)]),
   ('5',[("Forty years ago, his wife dropped her ring down this well.",S,0,0.5,0)]),
   ('6',[("She went down to find it.",S,-0.1,0.5,0),("She never came back up.",S*0.95,-0.3,0.5,P)]),
   ('7',[("So he stands here, and tells everyone it's dry.",S,-0.1,0.5,0)]),
   ('8',[("So nobody else goes down.",S*0.95,-0.2,0.5,0)]),
   ('9',[("Then one knight stopped.",S,0,0.5,0)]),
   ('10',[("He didn't talk.",S,0,0.5,0),("He climbed.",S*0.95,-0.1,0.5,P)]),
   ('11',[("When he came back up, he held out a ring.",S,0,0.5,0)]),
   ('12',[("For the first time in forty years, the old man said something new.",S,0,0.5,0),("Thank you.",S,0,0.5,0.3)]),
   ('13',[("He never said that line again.",S,-0.1,0.5,0),("The village was quieter.",S*0.95,-0.2,0.5,P),("So was he.",S*0.92,-0.4,1.0,0.15)])]
D=[(k,[(sx,sp,st-0.6-(0.2 if k=='1' else 0),g,pause) for sx,sp,st,g,pause in s_]) for k,s_ in D]
if __name__=='__main__':
    if sys.argv[1]=='src': ss.src(D,'nw')
    else: ss.build(D,'nw',sys.argv[2])
