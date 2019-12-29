"""
Database for loading the machine definitions
"""

import sqlite3
from ..phy.machine import *

conn = sqlite3.connect('data/swhp.db')
conn.row_factory = sqlite3.Row

curs = conn.cursor()


def getMachineById(id):
    gen_params = curs.execute('SELECT * FROM general WHERE id = ?', (id,)).fetchone()
    machine_type = gen_params['type'] + '_Machine'
    return eval(machine_type)(gen_params['eff'])
