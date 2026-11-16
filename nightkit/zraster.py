"""Z-buffered flat-shaded rasterizer that is a drop-in for Renderer.render().

The stock renderer uses the painter's algorithm (faces sorted by average depth). With
interpenetrating low-poly parts (legs inside a body, a jaw inside a skull) that ordering
breaks and you "see inside" models. This one keeps a per-pixel depth (1/Z), so every pixel
shows the nearest surface. Same projection, lighting and fog maths as engine.Renderer.
layers: list of face lists. bias: optional list of per-layer depth multipliers (>1 pulls a
layer slightly towards the camera, used for decals that sit 0.5 cm above a surface)."""
import math
import numpy as np
from PIL import Image

def clamp(v,a,b): return a if v<a else (b if v>b else v)

def zrender(R,cam,layers,lights=(),fov=70,fog_start=4,fog_end=24,ambient=0.06,shake=(0,0),bias=None,cull=True,return_z=False):
    """return_z=True also returns the 1/Z buffer (0 = nothing drawn), for compositing transparent effects."""
    W,H=R.W,R.H; vi=R.view(cam,fov); cx,cy,cz,ca,sa,cp,sp,fpx=vi
    fog=np.array(R.fog,float)
    img=np.empty((H,W,3)); img[:]=fog
    zb=np.zeros((H,W))                                 # stores 1/Z (0 = infinitely far)
    camp=np.array([cx,cy,cz])
    LP=[(np.array(lp,float),np.array(lc,float)/255.0,li) for lp,lc,li in lights]
    for li_,Q in enumerate(layers):
        lb=bias[li_] if bias else 1.0
        for q in Q:
            w=q.get('wind')
            if cull and w is not None and w*float(np.dot(q['n'],camp-q['c']))<=0: continue
            cs=[]
            for (x,y,z) in q['p']:
                px,py,pz=x-cx,y-cy,z-cz; X=ca*px-sa*pz; Z=sa*px+ca*pz; Y=cp*py-sp*Z; Z2=sp*py+cp*Z; cs.append((X,Y,Z2))
            out=[]; n=len(cs); zn=0.04
            for i in range(n):
                a=cs[i]; b=cs[(i+1)%n]; ina=a[2]>zn; inb=b[2]>zn
                if ina: out.append(a)
                if ina!=inb:
                    u=(zn-a[2])/(b[2]-a[2]); out.append((a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u,zn))
            if len(out)<3: continue
            sx=np.array([W/2+fpx*X/Z+shake[0] for (X,Y,Z) in out]); sy=np.array([H/2-fpx*Y/Z+shake[1] for (X,Y,Z) in out])
            x0=max(0,int(math.floor(sx.min()))); x1=min(W,int(math.ceil(sx.max()))+1)
            y0=max(0,int(math.floor(sy.min()))); y1=min(H,int(math.ceil(sy.max()))+1)
            if x0>=x1 or y0>=y1: continue
            iz=np.array([1.0/(Z-(0.08 if q['emit'] else 0.0)) if Z>0.12 else 1.0/Z for (X,Y,Z) in out])*lb
            # colour (identical to engine.Renderer)
            wc,nrm=q['c'],q['n']
            if q['emit']: col=np.array(q['col'],float)
            else:
                lr=lg=lb_=ambient
                for (lp,lc,li) in LP:
                    dv=lp-wc; dd=float(dv@dv); ld=dv/math.sqrt(dd+1e-9)
                    k=li/(1+dd*0.18)*(0.3+0.7*abs(float(nrm@ld))); lr+=k*lc[0]; lg+=k*lc[1]; lb_+=k*lc[2]
                col=np.array((q['col'][0]*min(1.6,lr),q['col'][1]*min(1.6,lg),q['col'][2]*min(1.6,lb_)))
            dist=math.sqrt((wc[0]-cx)**2+(wc[1]-cy)**2+(wc[2]-cz)**2)
            fg=clamp((dist-fog_start)/(fog_end-fog_start),0,1)*(0.5 if q['emit'] else 1)
            col=np.clip(col+(fog-col)*fg,0,255)
            # rasterize the convex polygon: edge tests + affine 1/Z (planar polygon)
            gx,gy=np.meshgrid(np.arange(x0,x1)+0.5,np.arange(y0,y1)+0.5)
            area=0.0
            for i in range(len(sx)):
                j=(i+1)%len(sx); area+=sx[i]*sy[j]-sx[j]*sy[i]
            if abs(area)<1e-9: continue
            sg=1.0 if area>0 else -1.0
            inside=np.ones(gx.shape,bool)
            for i in range(len(sx)):
                j=(i+1)%len(sx)
                e=(sx[j]-sx[i])*(gy-sy[i])-(sy[j]-sy[i])*(gx-sx[i])
                inside&=(e*sg>=-1e-6)
            if not inside.any(): continue
            # plane through the first three projected vertices with depth 1/Z
            (ax,ay,az),(bx,by,bz),(qx,qy,qz)=(sx[0],sy[0],iz[0]),(sx[1],sy[1],iz[1]),(sx[2],sy[2],iz[2])
            den=(bx-ax)*(qy-ay)-(qx-ax)*(by-ay)
            if abs(den)<1e-9:
                k2=max(range(2,len(sx)),key=lambda k:abs((bx-ax)*(sy[k]-ay)-(sx[k]-ax)*(by-ay)))
                qx,qy,qz=sx[k2],sy[k2],iz[k2]; den=(bx-ax)*(qy-ay)-(qx-ax)*(by-ay)
                if abs(den)<1e-9: continue
            A=((bz-az)*(qy-ay)-(qz-az)*(by-ay))/den; B=((qz-az)*(bx-ax)-(bz-az)*(qx-ax))/den
            d=az+A*(gx-ax)+B*(gy-ay)
            sub=zb[y0:y1,x0:x1]; m=inside&(d>sub)
            if not m.any(): continue
            sub[m]=d[m]; img[y0:y1,x0:x1][m]=col
    if return_z: return Image.fromarray(np.round(img).astype(np.uint8)),vi,zb
    return Image.fromarray(np.round(img).astype(np.uint8)),vi
