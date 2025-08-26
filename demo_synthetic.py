from src.params import PhysicalParams
import math
from src.physics import simulate_segment

def profile():
    prof=[]
    def add(seg_len, slope):
        sin_t = slope/(1+ slope*slope)**0.5
        cos_t = 1.0/(1+ slope*slope)**0.5
        for _ in range(int(seg_len/10)):
            prof.append((10.0, sin_t, cos_t))
    add(5000,-0.01)
    add(5000,-0.005)
    add(2000,0.0)
    return prof

p=PhysicalParams()
dist,t,vout,vmax=simulate_segment(profile(),v0=1.0,p=p,radii=None)
print(dist,t,vout,vmax)
