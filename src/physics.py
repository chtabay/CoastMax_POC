import math

def step_velocity(v, slope_sin, slope_cos, p, dt, v_cap_local=None):
    a = -p.g*slope_sin - p.crr*p.g*slope_cos - (p.rho*p.cda/(2*p.mass))*v*v
    v_new = max(0.0, v + a*dt)
    # Cap vitesse global et local (courbure)
    cap = p.vmax_cap if v_cap_local is None else min(p.vmax_cap, v_cap_local)
    if v_new > cap:
        v_new = cap
    return v_new, a

def simulate_segment(profile, v0, p, radii=None):
    v=v0; t=0.0; s_acc=0.0; vmax_seen=v0
    for idx,(ds,s_sin,s_cos) in enumerate(profile):
        # Cap local de vitesse depuis le rayon de courbure (si fourni)
        v_cap_curve=None
        if radii is not None:
            r = radii[idx] if idx < len(radii) else None
            if r is not None and math.isfinite(r) and r>0.0:
                v_cap_curve = math.sqrt(max(0.0, p.mu_curve * p.g * r))
        s_local=0.0
        while s_local<ds and v>0.0:
            v,a=step_velocity(v,s_sin,s_cos,p,p.dt,v_cap_local=v_cap_curve)
            ds_step=v*p.dt
            if ds_step<=1e-6:
                v=0.0; break
            s_local+=ds_step; s_acc+=ds_step; t+=p.dt; vmax_seen=max(vmax_seen,v)
            if s_local>ds:
                surplus=s_local-ds
                t-=surplus/max(v,1e-6)
                s_acc-=surplus
                s_local=ds
        if v<=0: break
    return s_acc,t,v,vmax_seen
