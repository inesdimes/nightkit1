"""Recurring silhouettes. The series figure: tall, thin, slightly hunched, head bowed, no detail."""
from .engine import box, transform, rx, ry, rz
def presence_colour(k,light=(62,46,34),dark=(12,11,11)):
    """k=0 almost blends into a lit wooden/wall surface, k=1 near black."""
    return tuple(int(a+(b-a)*k) for a,b in zip(light,dark))
def the_figure(px,pz,k=1.0,yaw=0.0,base=(62,46,34)):
    dk=presence_colour(k,base); Q=[]
    def W(p): p=ry(p,yaw); return (p[0]+px,p[1],p[2]+pz)
    Q+=transform(box(-0.13,-0.04,0,1.0,-0.05,0.05,dk),W); Q+=transform(box(0.04,0.13,0,1.0,-0.05,0.05,dk),W)
    Q+=transform(box(-0.2,0.2,1.0,1.68,-0.1,0.1,dk),lambda p:W(rx(p,0.18,(0,1.0,0))))
    for sx in (-1,1): Q+=transform(box(sx*0.24-0.035,sx*0.24+0.035,0.42,1.62,-0.04,0.04,dk),lambda p,sx=sx:W(rx(p,0.12,(0,1.6,0))))
    Q+=transform(box(-0.1,0.1,1.66,1.94,-0.11,0.09,dk),lambda p:W(rx(p,0.45,(0,1.66,-0.02))))
    return Q
def walker_profile(x,z,phase,col=(16,16,20)):
    """Dark figure walking along +x seen side-on; legs/arms swing in the x-y plane so the gait reads in silhouette."""
    import math
    Q=[]; sw=math.sin(phase)*0.45; bob=abs(math.sin(phase))*0.03
    def W(p): return (p[0]+x,p[1]+bob,p[2]+z)
    for sgn,dz in ((1,-0.07),(-1,0.07)):
        Q+=transform(box(-0.07,0.07,0.04,0.92,dz-0.06,dz+0.06,col),lambda p,sgn=sgn:W(rz(p,sgn*sw,(0,0.92,0))))
    Q+=transform(box(-0.13,0.11,0.92,1.5,-0.17,0.17,col),W)
    for sgn,dz in ((1,-0.2),(-1,0.2)): Q+=transform(box(-0.045,0.045,0.42,1.46,dz-0.04,dz+0.04,col),lambda p,sgn=sgn:W(rz(p,-sgn*sw*0.8,(0,1.44,0))))
    Q+=transform(box(-0.1,0.1,1.56,1.84,-0.095,0.095,col),lambda p:W(rz(p,0.52,(0.02,1.52,0))))
    return Q
