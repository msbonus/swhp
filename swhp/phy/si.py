"""
SI units
"""

import numpy as np

class SI:
    SIpfx = {
        'G': 10**9,
        'M': 10**6,
        'k': 10**3,
        'h': 10**2,
        'da': 10**1,
        '1': 1,
        'd': 10**-1,
        'c': 10**-2,
        'm': 10**-3,
        'u': 10**-6,
    }

    # Get multiplier by prefix
    def prefix(pfx):
        return SI.SIpfx.get(pfx)

    # Format a number with SI prefix
    def fmt(value):
        for pfx in SI.SIpfx:
            sipow = SI.SIpfx.get(pfx)
            if np.log10(sipow) % 3 == 0:
                if (pfx == "1"): pfx = ""
                if abs(value) >= sipow: return "%g %s" % (value / sipow, pfx)
