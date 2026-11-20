"""Option 1 of the voice order: ChatterboxVC converts the Kokoro sentences ($TTS_DIR/sc_src) to Enes's timbre -> $TTS_DIR/sc_vc.
Run with the Chatterbox embedded python (web server stopped):
  D:\chatter\Chatterbox-TTS-Server-2.0.0\python_embedded\python.exe tools/tts/sc_vc.py"""
import os, sys, glob, torch, torchaudio
REPO=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(REPO,'tts')); REF=os.environ.get('ENES_REF',os.path.join(REPO,'voice','enes_ref_main.wav'))
from chatterbox.vc import ChatterboxVC
vc=ChatterboxVC.from_pretrained('cuda'); out=os.path.join(TTS_DIR,'sc_vc'); os.makedirs(out,exist_ok=True)
for f in sorted(glob.glob(os.path.join(TTS_DIR,'sc_src','*.wav'))):
    torch.manual_seed(3000); w=vc.generate(f,target_voice_path=REF)
    if w.dim()==1: w=w.unsqueeze(0)
    torchaudio.save(os.path.join(out,os.path.basename(f)),w.cpu(),vc.sr); print(os.path.basename(f),round(w.shape[-1]/vc.sr,2),flush=True)
