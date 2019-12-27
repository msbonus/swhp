"""
Water properties
"""

from iapws import iapws97
from . import env as e

def WaterCp(T):
    return (iapws97._Region1(T, e.pa))["cp"] * 1000  # J/(kg*K)


def SpecificEnthalpy(T):
    return (iapws97._Region1(T, e.p))["h"] * 1000  # J/(kg)


def WaterDensity(T):
    return 1 / iapws97._Region1(T, e.pa)["v"]  # kg/m3
