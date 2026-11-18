"""Easing, keyframed tracks and camera templates. All periodic helpers take the loop length so they close perfectly."""
import math
def smooth(u): u=max(0.0,min(1.0,u)); return u*u*(3-2*u)
def ease_in(u): u=max(0.0,min(1.0,u)); return u*u
def ease_out(u): u=max(0.0,min(1.0,u)); return 1-(1-u)*(1-u)
def ease_in_out(u): return smooth(u)
def lerp(a,b,u): return a+(b-a)*u
def lerpv(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(len(a)))
class Track:
    """Piecewise keyframes [(time, value_tuple), ...] with an easing between neighbours; holds before/after."""
    def __init__(self,keys,ease=smooth): self.keys=sorted(keys,key=lambda k:k[0]); self.ease=ease
    def __call__(self,t):
        k=self.keys
        if t<=k[0][0]: return k[0][1]
        for (t0,v0),(t1,v1) in zip(k,k[1:]):
            if t0<=t<=t1: return lerpv(v0,v1,self.ease((t-t0)/(t1-t0) if t1>t0 else 1))
        return k[-1][1]
def slow_approach(start,end,t0,t1,ease=smooth):
    """Camera position moving from start to end between t0 and t1, resting before and after."""
    return Track([(t0,start),(t1,end)],ease)
def approach_and_return(start,end,t_go,t_arrive,t_back,t_home):
    """Loop-friendly path: rest at start, approach, hold, return home, rest (zero velocity at every turn)."""
    return Track([(t_go,start),(t_arrive,end),(t_back,end),(t_home,start)])
def handheld(t,loop,amp=1.0,seed=0):
    """Small breathing sway; every term completes whole cycles per loop, so frame 0 and frame N match."""
    w=2*math.pi/loop; s=seed
    dx=amp*(0.02*math.sin(w*3*t+s)+0.01*math.sin(w*7*t+1+s)+0.006*math.sin(w*13*t+0.5+s))
    dy=amp*(0.012*math.sin(w*5*t+2+s)+0.006*math.sin(w*11*t+s))
    dyaw=amp*(0.006*math.sin(w*4*t+s)+0.003*math.sin(w*9*t+s)); dpitch=amp*0.004*math.sin(w*6*t+s)
    return dx,dy,dyaw,dpitch
def sudden_turn(t,t0,dur,yaw_from,yaw_to):
    """Fast head turn with a short overshoot."""
    if t<=t0: return yaw_from
    u=min(1.0,(t-t0)/dur); e=1-(1-u)**3; over=math.sin(math.pi*u)*0.06*(yaw_to-yaw_from)
    return yaw_from+(yaw_to-yaw_from)*e+over*(1-u)
def walk_bob(t,speed=1.0,amp=0.035): return amp*math.sin(t*8.0*speed)

# ---- camera grammar helpers (added 18 Nov 2026; idea from an outside short pipeline, see PIPELINE.md) ----
def glide(u):
    """Symmetric smootherstep: zero speed at both ends, gentler than smooth(). Use for reframes of 0.75-1.7 s."""
    u=max(0.0,min(1.0,u)); return u*u*u*(u*(6*u-15)+10)
def creep(t,t0,rate=0.002,fps=24.0,punch=0.0,punch_s=1.4):
    """Push-in factor for a hold: 1.0 at t0, then shrinks by `rate` per frame (0.15-0.35 %/frame is a gentle push).
    `punch` (extra rate per frame, e.g. 0.004) is added for the first `punch_s` seconds on a punch word. Multiply the
    camera-to-subject distance by it: pos = target + (pos - target) * creep(...)."""
    f=max(0.0,(t-t0)*fps); s=rate*f
    if punch>0:
        n=min(f,punch_s*fps)
        for i in range(int(n)): s+=punch*max(0.0,min(1.0,(i+0.5)/6,(n-i-0.5)/6))
    return math.exp(-s)
def dolly(pos,target,k):
    """Move the camera toward `target` so its distance shrinks to k times (k from creep())."""
    return tuple(target[i]+(pos[i]-target[i])*k for i in range(3))
def kick(t,t0,amp=2.0,frames=7,fps=24.0):
    """Impact shake in pixels: the sign flips every frame and decays over `frames`. Returns 0 outside. Feed to render(shake=(0,kick(..)))."""
    f=(t-t0)*fps
    if f<0 or f>=frames: return 0.0
    i=int(f); return amp*(1-i/frames)*(1 if i%2==0 else -1)
