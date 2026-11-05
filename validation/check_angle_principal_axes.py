"""Independent B31E 70x70x8 angle cantilever principal-axis benchmark."""
import math, re, sys

def ref_displacements():
    b=h=0.07; t=0.008
    r=[(t,h,t/2,h/2),(b-t,t,t+(b-t)/2,t/2)]
    area=sum(w*d for w,d,y,z in r)
    yc=sum(w*d*y for w,d,y,z in r)/area
    zc=sum(w*d*z for w,d,y,z in r)/area
    iy=sum(w*d**3/12+w*d*(z-zc)**2 for w,d,y,z in r)
    iz=sum(d*w**3/12+w*d*(y-yc)**2 for w,d,y,z in r)
    iyz=sum(w*d*(y-yc)*(z-zc) for w,d,y,z in r)
    theta=-0.5*math.atan2(2*iyz,iy-iz)
    c,s=math.cos(theta),math.sin(theta)
    ip=c*c*iy+s*s*iz-2*c*s*iyz
    jp=s*s*iy+c*c*iz+2*c*s*iyz
    factor=1000*2**3/(3*210e9)
    return factor*(c*c/jp+s*s/ip),factor*s*c*(1/jp-1/ip)

def read_frd(path):
    disp=False
    for line in open(path,encoding="utf8",errors="replace"):
        if line.startswith(" -4") and "DISP" in line: disp=True; continue
        if disp and line.startswith(" -3"): disp=False
        if disp and line.startswith(" -1"):
            m=re.match(r"\s*(\d+)(.*)",line[3:])
            if m and int(m.group(1))==2:
                vals=re.findall(r"[+-]?\d+\.\d+E[+-]\d+",m.group(2),re.I)
                if len(vals)>=3:return [float(z) for z in vals[:3]]
    raise RuntimeError("No DISP field for node 2")

expected=ref_displacements()
actual=read_frd(sys.argv[1])[1:]
print("B31E 70x70x8 tip Uy,Uz",actual,"references",expected)
for val,target in zip(actual,expected):
    if not math.isfinite(val) or abs(val-target)>0.015*abs(target):
        raise SystemExit("FAIL: angle principal-axis coupling")
print("Angle principal-axis check PASS")
