"""
Environment
"""

from .htf import HTF


class Environment:
    def __init__(self):
        self.airTemp = 0
        self.waterIn = HTF()
        self.waterOut = HTF()
