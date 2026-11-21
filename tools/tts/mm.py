"""Voice for "Why do mimics pretend to be chests?" (mm, day 2, Tone 2.0: fp pace: S=1.22, pauses 0-0.15 s). 7 lines (briefs/mimic.md). Pipeline as nw.py."""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ss
S=1.22; P=0.12
D=[('1',[("Why do mimics pretend to be chests?",S,0.3,1.5,0)]),
   ('2',[("This chest was opened by every hero for a hundred years.",S,0,0.5,0)]),
   ('3',[("They always took something.",S,-0.1,0.5,0),("Nobody ever put anything back.",S*0.95,-0.3,0.5,P)]),
   ('4',[("One day, it learned to bite.",S,0,0.5,0)]),
   ('5',[("Then a knight opened it,",S,0,0.5,0),("and didn't draw his sword.",S*0.95,-0.1,0.5,0.15)]),
   ('6',[("He took nothing.",S,-0.1,0.5,0),("He left a coin.",S*0.95,-0.2,0.5,P)]),
   ('7',[("For the first time in a hundred years,",S*0.95,-0.1,0.5,0),("something was given back.",S*0.92,-0.4,1.0,0.12)])]
D=[(k,[(sx,sp,st-0.6-(0.2 if k=='1' else 0),g,pause) for sx,sp,st,g,pause in s_]) for k,s_ in D]
if __name__=='__main__':
    if sys.argv[1]=='src': ss.src(D,'mm')
    else: ss.build(D,'mm',sys.argv[2])
