"""
Various helpers
"""

def isNone(*variables, strict=False):
    if strict:
        for var in variables:
            if not (var is None): return False
        return True
    else:
        for var in variables:
            if (var is None): return True
        return False


def dropNone(*variables):
    ret = list()
    for var in variables:
        if not (var is None): ret.append(var)
    return ret
