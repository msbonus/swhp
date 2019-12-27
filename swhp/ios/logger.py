"""
Logger
"""

from enum import IntEnum, auto

class LogLevel(IntEnum):
    Non = 0
    Err = auto()
    War = auto()
    Inf = auto()
    Debug = auto()
    Trace = auto()
    Spew = auto()


class SimpleLogger:
    elem = "  "
    loglevel = LogLevel.Inf
    ind = ""

    @classmethod
    def inc(cls):
        cls.ind += cls.elem

    @classmethod
    def dec(cls):
        cls.ind = cls.ind[0:-len(cls.elem)]

    @classmethod
    def reset(cls):
        cls.ind = ""

    def err(self, *msg):
        if self.loglevel >= LogLevel.Err:
            print(self.ind, *msg)

    def war(self, *msg):
        if self.loglevel >= LogLevel.War:
            print(self.ind, *msg)

    @classmethod
    def inf(cls, *msg):
        if cls.loglevel >= LogLevel.Inf:
            print(cls.ind, *msg)

    def debug(self, *msg):
        if self.loglevel >= LogLevel.Debug:
            print(self.ind, *msg)

    @classmethod
    def trace(cls, *msg):
        if cls.loglevel >= LogLevel.Trace:
            print(cls.ind, *msg)

    def spew(self, *msg):
        if self.loglevel >= LogLevel.Spew:
            print(self.ind, *msg)