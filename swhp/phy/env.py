"""
Environment
"""

from .htf import HTF

pa = 101325 / 10 ** 6  # MPa
TK0 = 273.15
p = 1  # MPa

class Environment:
    def __init__(self):
        self.airTemp = 0
        self.waterIn = HTF()
        self.waterOut = HTF()
