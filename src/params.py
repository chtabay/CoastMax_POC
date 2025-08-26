from dataclasses import dataclass
@dataclass
class PhysicalParams:
    mass: float = 85.0
    crr: float = 0.004
    cda: float = 0.30
    rho: float = 1.225
    mu_curve: float = 0.35
    g: float = 9.80665
    dt: float = 0.1
    vmax_cap: float = 35.0
