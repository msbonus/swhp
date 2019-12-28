"""
Water properties
"""

from iapws import iapws97
from . import const as c

def WaterCp(T):
    return (iapws97._Region1(T, c.pa))["cp"] * 1000  # J/(kg*K)


def SpecificEnthalpy(T):
    return (iapws97._Region1(T, c.p))["h"] * 1000  # J/(kg)


def WaterDensity(T):
    return 1 / iapws97._Region1(T, c.pa)["v"]  # kg/m3
