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

    @classmethod
    def err(cls, *msg):
        if cls.loglevel >= LogLevel.Err:
            print(cls.ind, *msg)

    @classmethod
    def war(cls, *msg):
        if cls.loglevel >= LogLevel.War:
            print(cls.ind, *msg)

    @classmethod
    def inf(cls, *msg):
        if cls.loglevel >= LogLevel.Inf:
            print(cls.ind, *msg)

    @classmethod
    def debug(cls, *msg):
        if cls.loglevel >= LogLevel.Debug:
            print(cls.ind, *msg)

    @classmethod
    def trace(cls, *msg):
        if cls.loglevel >= LogLevel.Trace:
            print(cls.ind, *msg)

    @classmethod
    def spew(cls, *msg):
        if cls.loglevel >= LogLevel.Spew:
            print(cls.ind, *msg)
