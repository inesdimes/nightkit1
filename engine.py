"""Minimal software 3D renderer (painter's algorithm) for low-poly PS1-style frames.
Coordinates in metres, y up. A camera is (x, y, z, yaw, pitch); yaw 0 looks toward +z, pitch >0 looks up."""
import math
import numpy as np
from PIL import Image, ImageDraw

def clamp(v,a,b): return max(a,min(b,v))
def lerpc(a,b,u): u=clamp(u,0,1); return tuple(a[i]+(b[i]-a[i])*u for i in range(3))

def quad(p,col,emit=False):
    """A face: list of 3D points (ordered), colour, emissive flag (emissive faces ignore lighting)."""
    q=dict(p=[tuple(map(float,v)) for v in p],col=col,emit=emit)
    a=np.subtract(q['p'][1],q['p'][0]); b=np.subtract(q['p'][2],q['p'][0]); n=np.cross(a,b)
    q['n']=n/(np.linalg.norm(n)+1e-9); q['c']=np.mean(q['p'],axis=0); return q
def refresh(q):
    a=np.subtract(q['p'][1],q['p'][0]); b=np.subtract(q['p'][2],q['p'][0]); n=np.cross(a,b)
    q['n']=n/(np.linalg.norm(n)+1e-9); q['c']=np.mean(q['p'],axis=0); return q
def box(x0,x1,y0,y1,z0,z1,col,xf=None,emit=False):
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    if xf: v=[xf(p) for p in v]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([v[i] for i in f],col,emit) for f in F]
def transform(qs,fn):
    for q in qs: q['p']=[fn(v) for v in q['p']]; refresh(q)
    return qs
def rx(p,a,c=(0,0,0)):
    x,y,z=p[0]-c[0],p[1]-c[1],p[2]-c[2]; ca,sa=math.cos(a),math.sin(a); return (c[0]+x,c[1]+ca*y-sa*z,c[2]+sa*y+ca*z)
def ry(p,a,c=(0,0,0)):
    x,y,z=p[0]-c[0],p[1]-c[1],p[2]-c[2]; ca,sa=math.cos(a),math.sin(a); return (c[0]+ca*x+sa*z,c[1]+y,c[2]-sa*x+ca*z)
def rz(p,a,c=(0,0,0)):
    x,y,z=p[0]-c[0],p[1]-c[1],p[2]-c[2]; ca,sa=math.cos(a),math.sin(a); return (c[0]+ca*x-sa*y,c[1]+sa*x+ca*y,c[2]+z)
def tiled_plane(x0,x1,z0,z1,y,step,colfn):
    """Horizontal plane split into tiles (tiling keeps the painter's sort stable). colfn(ix,iz)->colour."""
    Q=[]; xs=list(np.arange(x0,x1,step))+[x1]; zs=list(np.arange(z0,z1,step))+[z1]
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            a,b,c,d=xs[i],min(xs[i+1],x1),zs[j],min(zs[j+1],z1)
            if b-a<1e-6 or d-c<1e-6: continue
            Q.append(quad([(a,y,c),(b,y,c),(b,y,d),(a,y,d)],colfn(i,j)))
    return Q
def wall_region(plane,fixed,u0,u1,v0,v1,du,dv,colfn,facing=1):
    """Vertical wall tiled into rectangles. plane 'x' (wall at x=fixed, spans z=u, y=v) or 'z' (wall at z=fixed, spans x=u, y=v).
    Built exactly to the given bounds, so openings can be framed precisely."""
    Q=[]; us=list(np.arange(u0,u1,du))+[u1]; vs=list(np.arange(v0,v1,dv))+[v1]
    for i in range(len(us)-1):
        for j in range(len(vs)-1):
            a,b,c,d=us[i],min(us[i+1],u1),vs[j],min(vs[j+1],v1)
            if b-a<1e-6 or d-c<1e-6: continue
            col=colfn(i,j,c)
            if plane=='z': pts=[(a,c,fixed),(b,c,fixed),(b,d,fixed),(a,d,fixed)]
            else: pts=[(fixed,c,a),(fixed,c,b),(fixed,d,b),(fixed,d,a)]
            if facing<0: pts=pts[::-1]
            Q.append(quad(pts,col))
    return Q

class Camera:
    @staticmethod
    def look(pos,target):
        dx,dy,dz=target[0]-pos[0],target[1]-pos[1],target[2]-pos[2]
        return (pos[0],pos[1],pos[2],math.atan2(dx,dz),math.atan2(dy,math.sqrt(dx*dx+dz*dz)))
    @staticmethod
    def direction(yaw,pitch): return np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch)])

class Renderer:
    """Renders layers of faces. Layers are drawn in order (each one depth-sorted on its own):
    put geometry that is always behind something (rooms behind openings, things inside an elevator) in an earlier layer."""
    def __init__(self,W=180,H=320,fog=(10,13,18)):
        self.W,self.H,self.fog=W,H,fog
    def view(self,cam,fov):
        cx,cy,cz,yaw,pitch=cam; fpx=self.W/(2*math.tan(math.radians(fov)/2))
        return (cx,cy,cz,math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch),fpx)
    def project(self,P,vi,shake=(0,0)):
        cx,cy,cz,ca,sa,cp,sp,fpx=vi
        px,py,pz=P[0]-cx,P[1]-cy,P[2]-cz
        X=ca*px-sa*pz; Z=sa*px+ca*pz; Y=cp*py-sp*Z; Z2=sp*py+cp*Z
        if Z2<0.05: return None
        return (self.W/2+fpx*X/Z2+shake[0],self.H/2-fpx*Y/Z2+shake[1],Z2)
    def render(self,cam,layers,lights=(),flash=None,fov=70,fog_start=4,fog_end=24,ambient=0.06,shake=(0,0),spot=(0.86,0.97)):
        """lights: [((x,y,z),(r,g,b),intensity)], flash: ((x,y,z), direction ndarray, intensity) cone light."""
        W,H=self.W,self.H; img=Image.new('RGB',(W,H),self.fog); d=ImageDraw.Draw(img)
        vi=self.view(cam,fov); cx,cy,cz,ca,sa,cp,sp,fpx=vi
        for Q in layers:
            polys=[]
            for q in Q:
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
                pts=[(round(W/2+fpx*X/Z+shake[0]),round(H/2-fpx*Y/Z+shake[1])) for (X,Y,Z) in out]
                if max(p[0] for p in pts)<0 or min(p[0] for p in pts)>W or max(p[1] for p in pts)<0 or min(p[1] for p in pts)>H: continue
                depth=sum(c[2] for c in out)/len(out)-(0.08 if q['emit'] else 0.0)
                wc,nrm=q['c'],q['n']
                if q['emit']: col=q['col']
                else:
                    lr=lg=lb=ambient
                    for (lp,lc,li) in lights:
                        dv=np.array(lp)-wc; dd=float(dv@dv); ld=dv/math.sqrt(dd+1e-9)
                        k=li/(1+dd*0.18)*(0.3+0.7*abs(float(nrm@ld))); lr+=k*lc[0]/255; lg+=k*lc[1]/255; lb+=k*lc[2]/255
                    if flash:
                        fp,fd,fi=flash; dv=wc-np.array(fp); dist=math.sqrt(float(dv@dv))+1e-6; cosang=float(dv@fd)/dist
                        s=clamp((cosang-spot[0])/(spot[1]-spot[0]),0,1); k=fi*s/(1+dist*dist*0.06)*(0.35+0.65*abs(float(nrm@(dv/dist))))
                        lr+=k; lg+=k*0.95; lb+=k*0.82
                    col=(q['col'][0]*min(1.6,lr),q['col'][1]*min(1.6,lg),q['col'][2]*min(1.6,lb))
                dist=math.sqrt((wc[0]-cx)**2+(wc[1]-cy)**2+(wc[2]-cz)**2)
                fg=clamp((dist-fog_start)/(fog_end-fog_start),0,1)*(0.5 if q['emit'] else 1)
                col=lerpc(col,self.fog,fg); polys.append((depth,pts,tuple(int(clamp(c,0,255)) for c in col)))
            polys.sort(key=lambda p:-p[0])
            for _,pts,col in polys: d.polygon(pts,fill=col)
        return img,vi
