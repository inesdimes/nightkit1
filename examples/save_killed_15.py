"""ONE SMALL MISTAKE #01 - "The Save That Killed Him", TikTok cut (~20 s). Imports examples/save_killed.py and reuses
all of it (knight, hall, crystal, HUD, menus, cameras A-D, audio design); only the voice (tools/tts/sk.py --cut 15 ->
$TTS_DIR/sk15) and the beat times change. Frame 0: the knight is already saving at 1 HP (SAVING... bar fills while the
poison drains). Two deaths, then the delete-save payoff.
Run: TEST=1,8,15 python examples/save_killed_15.py -> test.png | PART=a:b (frames -> out/sk15_a.mp4) | PART=audio"""
import os, sys, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import save_killed as SK
from PIL import Image

SCR=json.load(open(os.path.join(SK.TTS_DIR,'sk15','script.json')))
GAPS={'3':0.55}                                       # after "Then died.": YOU DIED must be readable
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,10)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAPS.get(k,0.12)
    return out,t-GAPS.get('9',0.12)
LINES,_vend=_lines()
SK.SCR=SCR; SK.LINES=LINES; SK.T0=dict(LINES); SK.VOICE_DIR='sk15'
SK.DUR=round(_vend+0.4,2); SK.N=int(round(SK.DUR*SK.FPS))
ws,we,LEAD=SK.ws,SK.we,SK.LEAD
# ---- beats
SK.T_REACH=-1.0; SK.T_SAVING=0.0
SK.T_SAVE=ws('3',0)+0.25-LEAD                         # "He SAVED anyway."
SK.T_HOOK_END=we('1',0)
SK.D=[ws('3',1)+0.2-LEAD]                             # "Then DIED."
SK.R=[SK.T0['4']-LEAD]                                # "Respawned."
SK.D.append(ws('4',1)+0.1-LEAD); SK.R.append(SK.D[-1]+0.6)   # "Died again."
SK.R_LAST=SK.R[-1]
SK.PAUSE=SK.T0['7']-0.1
SK.LIFE=SK.PAUSE-SK.R_LAST+0.5                       # last life: the bar is still not empty when he pauses
SK.T_CUR=[SK.PAUSE+0.15,SK.PAUSE+0.45,SK.PAUSE+0.75,we('7',0)-0.65]   # lands on DELETE SAVE with the words
SK.T_CONF=we('7',0)-0.05; SK.T_WIPE=SK.T0['8']-LEAD; SK.T_WIPED=we('8',0)
SK.T_NEW=we('8',0)+0.05                               # wipe done -> NEW GAME, HP 100
SK.T_BOSS=ws('9',0)+0.55-LEAD                         # "And the final BOSS was alive again."
SK.T_LOOK=None; SK.T_STILL=None; SK.T_TOOSLOW=None; SK.T_RUN=None; SK.T_POT=None; SK.WALK_AWAY=False
SK.T_WAIT=(ws('5',0)-LEAD,we('5',0)+0.25)
SK.T_PANEL=SK.T0['6']-LEAD; SK.T_HL=ws('6',0)+1.35-LEAD      # "...saved his POISON too"
SK.CUTS=[0.0,ws('3',1)-0.05,ws('4',1)-0.15,SK.PAUSE,SK.DUR]  # the same 4 camera setups, 3 hard cuts
SK.SUBS=SK._subs()
DUR,N,FPS,W,H,S=SK.DUR,SK.N,SK.FPS,SK.W,SK.H,SK.S
frame=SK.frame; frame_final=SK.frame_final

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

QA=dict(SK.QA); QA.update(dur=DUR,frame=frame,
    allow_jump=[('knight',f/FPS) for c in SK.CUTS+SK.R for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    allow_teleport=[('knight',r) for r in SK.R],
    scenes=[dict(id=f's{i}',t0=SK.CUTS[i],t1=SK.CUTS[i+1],action=a) for i,a in enumerate((
        'frame 0: already saving at HP 1, poison draining, SAVE COMPLETE (CAM A)',
        'then died: YOU DIED, white flash respawn (CAM B)',
        'died again, WAIT, save file shows HP 1 + POISON (CAM C)',
        'pause: DELETE SAVE, 30 h wiped, NEW GAME HP 100, BOSS: ALIVE (CAM D)'))])

if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(SK.build_audio(os.path.join(SK.OUT,'save_killed_15.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    from nightkit import post
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(SK.OUT,f'sk15_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
