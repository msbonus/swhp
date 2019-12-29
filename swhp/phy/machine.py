"""
Energy machine classes
"""

import numpy as np

from ..ios.vars import isNone, dropNone
from ..ios.logger import SimpleLogger as log

from .htf import HTF
from .power import Power, ElecPower, FuelPower
from .eff import Efficiency


class EItem:
    def __init__(self):
        self.active = True

        self.pwr = None
        self.pwr_factor = 1
        self.htfin = None
        self.htfout = None

        self.htfin_min = HTF()
        self.htfin_max = HTF()

        self.htfout_min = HTF()
        self.htfout_max = HTF()

        self.label = None

    # htf input with volume flow limited by htfin_max and htfout_max
    def limit_htfin_massflow(self):
        self.htfin.massflow = min(dropNone(self.htfin.massflow, self.htfin_max.massflow, self.htfout_max.massflow))

    # htf output with volume flow limited by htfin_max and htfout_max
    def limit_htfout(self):
        self.htfout.temperature = min(dropNone(self.htfout.temperature, self.htfout_max.temperature))
        self.htfout.massflow = min(dropNone(self.htfout.massflow, self.htfin_max.massflow, self.htfout_max.massflow))


class EMachine(EItem):
    # input values: Efficiency efficiency
    def __init__(self, efficiency, genEff=0):
        super().__init__()

        self.efficiency = efficiency
        self.genEff = genEff

        self.pwrin_min = 0
        self.pwrin_max = 0

    def gvRepr(self, graph):
        with graph.subgraph(name='cluster_' + self.label) as c:
            c.attr('node', shape='record')
            c.attr(label=self.label)
            # c.node(self.label, '{<IN>IN: ' + self.htfin.__str__(short = True) + '|' + str(self.pwr) + '|<OUT>OUT: ' + self.htfout.__str__(short = True) + '}')
            c.node(self.label + '_IN', 'IN: ' + self.htfin.__str__(short=True))
            c.node(self.label + '_OUT', 'OUT: ' + self.htfout.__str__(short=True))
            c.node(self.label, self.label + ': ' + str(self.pwr))
            c.edge(self.label + '_IN', self.label)
            c.edge(self.label, self.label + '_OUT')

    # check parameters
    def check(self):
        if (self.pwr_factor > 1):
            log.trace("pwr_factor > 1")
        elif (self.htfout > self.htfout_max):
            log.trace("self.htfout > self.htfout_max")
        else:
            return True
        return False

    # power generation
    def generate(self):
        # generating electric power from fuel (cogeneration)
        self.pwrgen = Power(ElecPower(self.pwruse.fuelPower.value * self.genEff))

    # power balance
    def balance(self):
        self.pwr = self.pwrgen - self.pwruse

    # defined values: HTF htfin
    # calculated values: Power pwr, HTF htfout
    def forwardtask(self):
        # limit power factor by 100%
        self.pwr_factor = min(self.pwr_factor, 1)
        # power consumption
        self.pwruse = Power(self.pwrin_max * self.pwr_factor)

        # htf output is an input...
        self.htfout = HTF() + self.htfin
        # ...plus temperature raise dT
        # dT = P * nu / (m * Cp)
        self.htfout.temperature += self.pwruse * self.efficiency / (self.htfin.massflow * self.htfin.getCp())

    # defined values: HTF htfin, HTF htfout
    # calculated values: Power pwrin, Power pwrout
    def reversetask(self):
        # limit output htf temperature and massflow
        self.limit_htfout()
        # power used for heating
        # P = m * Cp * dT
        pwr = (self.htfin.massflow * self.htfin.getCp()) * (self.htfout.temperature - self.htfin.temperature)
        # power consumption and power factor
        self.pwruse = EMachine.splitOutput(pwr, self.efficiency)
        self.pwr_factor = self.pwruse / self.pwrin_max

    # FIXME: double computation
    def splitOutput(pwr, efficiency):
        elecPwr = ElecPower(pwr / efficiency.elecEff) if efficiency.elecEff != 0 else 0
        fuelPwr = FuelPower(pwr / efficiency.fuelEff) if efficiency.fuelEff != 0 else 0
        return Power(elecPwr, fuelPwr)

    def run(self):
        if ((self.pwr_factor == 0) or (self.htfin.massflow == 0)):
            self.active = False

        if (self.active):
            log.inf("Running " + type(self).__name__ + " " + self.label)
            if (not isNone(self.htfin, self.htfout)):
                log.inf("Attempting reverse task")
                self.limit_htfin_massflow()
                self.reversetask()
                if (not self.check()):
                    log.inf("Check failed, attempting forward task")
                    self.forwardtask()
                self.generate()
                self.balance()
            elif (not isNone(self.htfin)):
                log.inf("Attempting forward task")
                self.limit_htfin_massflow()
                self.forwardtask()
                if (not self.check()):
                    log.inf("Check failed, attempting reverse task")
                    self.reversetask()
                self.generate()
                self.balance()
            else:
                raise ValueError("not enough input for machine")
            log.inf("Input: " + str(self.htfin) + ", output: " + str(self.htfout))
            log.inf("Energy balance: " + str(self.pwr) + ", power factor:  " + str(self.pwr_factor))
        else:
            log.inf(type(self).__name__ + " " + self.label + " is not active")
            self.pwr = Power()
            self.pwr_factor = 0
            self.htfin = HTF()
            self.htfout = HTF()


# Power to heat
class P2H_Machine(EMachine):
    pass


# Furnace
class FUR_Machine(EMachine):
    pass


# Cogeneration / combined heat and power
class CHP_Machine(EMachine):
    pass


# Bypass
class BP_Machine(EMachine):
    def __init__(self):
        super().__init__(Efficiency())
        self.pwrin_max = Power()


# Heat pump
class HP_Machine(EMachine):
    def __init__(self, eff):
        super().__init__(eff)
        self.dT = 0
        self.waterIn = HTF()
        self.waterOut = HTF()

    def getCOP(self):
        return self.efficiency.elecEff * (self.htfout.temperature) / (
                self.htfout.temperature - self.waterIn.temperature)

    # defined values: HTF htfin, HTF waterIn, HTF waterOut
    # calculated values: Power pwr, HTF htfout
    def forwardtask(self):
        # power consumption
        self.pwruse = Power(self.pwrin_max * self.pwr_factor)

        # htf output is an input...
        self.htfout = HTF() + self.htfin

        # solving an equation for output temperature
        # P * COP = m * Cp * dT
        ea = self.htfin.massflow * self.htfin.getCp()
        eb = - (self.pwruse * self.efficiency + self.htfin.massflow * self.htfin.getCp() * (
                self.waterIn.temperature + self.htfin.temperature))
        ec = self.htfin.massflow * self.htfin.getCp() * self.waterIn.temperature * self.htfin.temperature
        eD = eb ** 2 - 4 * ea * ec
        self.htfout.temperature = (-eb + np.sqrt(eD)) / (2 * ea)
        log.inf("COP:", self.getCOP())

    # defined values: HTF htfin, HTF htfout
    # calculated values: Power pwrin, Power pwrout
    def reversetask(self):
        # limit output htf temperature and massflow
        self.limit_htfout()
        # power used for heating
        # P = m * Cp * dT
        pwr = (self.htfin.massflow * self.htfin.getCp()) * (self.htfout.temperature - self.htfin.temperature)
        # power consumption and power factor
        self.pwruse = Power(ElecPower(pwr / self.getCOP()))
        self.pwr_factor = self.pwruse / self.pwrin_max
        log.inf("COP:", self.getCOP())


"""
Coupling variations
"""


class EConn(EItem):
    def __init__(self, *elements):
        super().__init__()

        self.elements = list()

        for element in elements:
            self.elements.append(element)

    def run(self):
        log.inf("Running", type(self).__name__, self.label)
        log.inc()
        self.compute()
        log.dec()
        log.inf("Input: " + str(self.htfin) + ", output: " + str(self.htfout))
        log.inf("Energy balance:", self.pwr)
        log.inf()


class ESerial_Conn(EConn):
    def compute(self):
        self.pwr = Power()
        self.limit_htfin_massflow()

        htfin_element = HTF(self.htfin.temperature,
                            min(dropNone(self.htfin.massflow, self.htfin_max.massflow, self.htfout_max.massflow)))

        for element in self.elements:
            element.htfin = HTF() + htfin_element

            element.run()

            self.pwr += element.pwr
            htfin_res = htfin_element - element.htfin
            htfin_element = element.htfout + htfin_res

        self.htfout = htfin_element

    def gvRepr(self, graph):
        with graph.subgraph(name='cluster_' + self.label) as c:
            c.attr('node', shape='box')
            c.node(self.label + '_IN', 'IN: ' + self.htfin.__str__(short=True))
            c.node(self.label + '_OUT', 'OUT: ' + self.htfout.__str__(short=True))
            c.attr(label=self.label)
            for element in self.elements:
                element.gvRepr(c)
            c.edge(self.label + '_IN', self.elements[0].label + '_IN')
            c.edge(self.elements[-1].label + '_OUT', self.label + '_OUT')
            for i in range(len(self.elements) - 1):
                c.edge(self.elements[i].label + '_OUT', self.elements[i + 1].label + '_IN')


class EParallel_Conn(EConn):
    def compute(self):
        self.htfout = HTF()
        self.pwr = Power()

        # pwr input for the first element
        htfin_res = HTF() + self.htfin

        for element in self.elements:
            # htf as input
            element.htfin = HTF() + htfin_res
            element.run()

            # pwr balance
            self.pwr += element.pwr
            # mix htf output
            self.htfout += element.htfout

            # subtract used htf
            htfin_res -= element.htfin

            log.inf()

        if (htfin_res.massflow != 0):
            log.inf("Rejected " + str(htfin_res))
            self.htfin -= htfin_res

    def gvRepr(self, graph):
        with graph.subgraph(name='cluster_' + self.label) as c:
            c.attr('node', shape='box')
            c.node(self.label + '_IN', 'IN: ' + self.htfin.__str__(short=True))
            c.node(self.label + '_OUT', 'OUT: ' + self.htfout.__str__(short=True))
            c.attr(label=self.label)
            for element in self.elements:
                element.gvRepr(c)
                c.edge(self.label + '_IN', element.label + '_IN')
                c.edge(element.label + '_OUT', self.label + '_OUT')
