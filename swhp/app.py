"""
Run the swhp
"""

from graphviz import Digraph

from .ios.db import conn, curs, getMachineById

from .phy import const as c
from .phy.env import Environment
from .phy.machine import *


def run2():
    print(getMachineById(1))
    conn.close()

def run():
    envr = Environment()
    envr.waterIn = HTF(25 + c.TK0, 20)

    htfin = HTF(70 + c.TK0, 90)
    graph = Digraph()

    hp_1 = HP_Machine(Efficiency(elecEff=0.495))
    hp_1.dT = 5
    hp_1.waterIn = envr.waterIn
    hp_1.waterOut = envr.waterOut
    hp_1.label = "HP_1"
    hp_1.pwrin_max = ElecPower(6500, "k")
    hp_1.htfout_max = HTF(88 + c.TK0, 165.8)

    p2h_1 = P2H_Machine(Efficiency(elecEff=0.94))
    p2h_1.label = "P2H_1"
    p2h_1.pwrin_max = ElecPower(100, "k")
    p2h_1.htfout_max = HTF(999, 10)

    p2h_2 = P2H_Machine(Efficiency(elecEff=0.94))
    p2h_2.label = "P2H_2"
    p2h_2.pwrin_max = ElecPower(50, "k")
    p2h_2.htfout_max = HTF(999, 10)

    fur_1 = FUR_Machine(Efficiency(fuelEff=0.92))
    fur_1.label = "FUR_1"
    fur_1.pwrin_max = FuelPower(6.52, "M")
    fur_1.htfout_max = HTF(999, 57)

    fur_2 = FUR_Machine(Efficiency(fuelEff=0.92))
    fur_2.label = "FUR_2"
    fur_2.pwrin_max = FuelPower(5.44, "M")
    fur_2.htfout_max = HTF(999, 47)

    chp_1 = CHP_Machine(Efficiency(fuelEff=0.489), 0.411)
    chp_1.label = "CHP_1"
    chp_1.pwrin_max = FuelPower(2, "M")
    chp_1.htfout_max = HTF(999, 10)

    chp_2 = CHP_Machine(Efficiency(fuelEff=0.499), 0.407)
    chp_2.label = "CHP_2"
    chp_2.pwrin_max = FuelPower(2.42, "M")
    chp_2.htfout_max = HTF(999, 10.3)

    bps_1 = BP_Machine()
    bps_1.label = "BPS_1"
    bps_1.htfout_max = HTF(999, 20)

    bps_2 = BP_Machine()
    bps_2.label = "BPS_2"
    bps_2.htfout_max = HTF(999, 97)

    stage_1_1 = EParallel_Conn(chp_1, fur_1)
    stage_1_1.label = "STAGE_1_1"

    stage_1_2i = ESerial_Conn(p2h_1, p2h_2)
    stage_1_2i.label = "STAGE_1_2I"
    stage_1_2i.htfout_max = HTF(999, 10)
    stage_1_2 = EParallel_Conn(chp_2, fur_2, stage_1_2i)
    stage_1_2.label = "STAGE_1_2"

    system_1 = ESerial_Conn(hp_1, stage_1_1, stage_1_2)
    system_1.label = "SYSTEM_1"
    system_1.htfin = htfin
    system_1.run()

    system_1.gvRepr(graph)
