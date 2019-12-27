"""
Definition of power classes
"""

from .si import SI
from .eff import Efficiency


class PowerType:
    def __init__(self, value=0, SIprefix='1'):
        self.value = value * SI.prefix(SIprefix)

    def __add__(self, other):
        return type(self)(self.value + other.value)

    def __sub__(self, other):
        return type(self)(self.value - other.value)

    def __mul__(self, other):
        return type(self)(self.value * other)

    def __str__(self):
        return "%s %sW" % (type(self).__name__, SI.fmt(self.value))


class ElecPower(PowerType):
    pass


class FuelPower(PowerType):
    pass


class Power:
    def __init__(self, *pwr_values):
        self.elecPower = ElecPower()
        self.fuelPower = FuelPower()
        for pwr in pwr_values:
            if type(pwr) is ElecPower:
                self.elecPower += pwr
            elif type(pwr) is FuelPower:
                self.fuelPower += pwr

    def all(self):
        return (self.elecPower.value + self.fuelPower.value)

    # Multiplying Power by efficiency in forward task
    def __mul__(self, other):
        if type(other) is Efficiency:
            return self.elecPower.value * other.elecEff + self.fuelPower.value * other.fuelEff
        else:
            return 0

    # Dividing Power by Power in reverse task
    # FIXME: what if types are different
    def __truediv__(self, other):
        if type(other) is Power:
            return (self.elecPower.value + self.fuelPower.value) / (other.elecPower.value + other.fuelPower.value)
        elif type(other) is ElecPower:
            return self.elecPower.value / other.value
        elif type(other) is FuelPower:
            return self.fuelPower.value / other.value
        else:
            return 0

    def __add__(self, other):
        return Power(self.elecPower + other.elecPower, self.fuelPower + other.fuelPower)

    def __sub__(self, other):
        return Power(self.elecPower - other.elecPower, self.fuelPower - other.fuelPower)

    def __str__(self):
        val = ""
        for pwr in [self.elecPower, self.fuelPower]:
            if (pwr.value != 0):
                if (val != ""): val += ", "
                val += str(pwr)
        if (val != ""):
            return val
        else:
            return "None"
