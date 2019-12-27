"""
Heat-transfer fluid
"""

from ..ios.vars import isNone, dropNone
from ..ios.logger import SimpleLogger as log

from .wp import WaterCp, WaterDensity
from . import env as e

class HTF:
    def __init__(self, temperature = None, massflow = None, type = 'water'):
        self.temperature = temperature
        self.massflow = massflow
        self.type = type.lower()

    # Temperature is stored in Kelvin, but we are printing Celsius
    def __str__(self, short = False):
        if (short):
            return '%g °C, %g kg/s' % (self.temperature - e.TK0, self.massflow)
        else:
            return '%s at %g °C, %g kg/s' % (self.type, self.temperature - e.TK0, self.massflow)

    def __eq__(self, other):
        return ((self.type == other.type) and
                (self.temperature == other.temperature) and
                (self.massflow == other.massflow))

    def __gt__(self, other):
        return ((self.type == other.type) and
                (not isNone(self.temperature, other.temperature) and (self.temperature > other.temperature)) or
                (not isNone(self.massflow, other.massflow) and (self.massflow > other.massflow)))

    def __lt__(self, other):
        return ((self.type == other.type) and
                (not isNone(self.temperature, other.temperature) and (self.temperature < other.temperature)) or
                (not isNone(self.massflow, other.massflow) and (self.massflow < other.massflow)))

    def __add__(self, other):
        if isNone(self.temperature, self.massflow, strict = True):
            return HTF(other.temperature, other.massflow)
        elif isNone(other.temperature, other.massflow, strict = True):
            return HTF(self.temperature, self.massflow)
        else:
            log.inf("Mixing", self, "with", other)
            temperature = (self.temperature * self.massflow +
                           other.temperature * other.massflow) / (self.massflow + other.massflow)
            massflow = self.massflow + other.massflow
            htfout = HTF(temperature, massflow)
            log.inf(" ->", htfout)
            return htfout

    def __sub__(self, other):
        if (self.temperature != other.temperature):
            raise ValueError("temperatures should match to subtract the flows")
        return HTF(self.temperature, self.massflow - other.massflow)

    def min(self, other):
        return HTF(min(dropNone(self.temperature, other.temperature)), min(dropNone(self.massflow, other.massflow)))

    def max(self, other):
        return HTF(max(dropNone(self.temperature, other.temperature)), max(dropNone(self.massflow, other.massflow)))

    def getCp(self):
        if self.type == 'water':
            return(WaterCp(self.temperature))
        else:
            return 0

    def getDens(self):
        if self.type == 'water':
            return(WaterDensity(self.temperature))
        else:
            return 0
