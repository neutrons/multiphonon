#!/usr/bin/env python
#
# Jiao Lin


def interp(doshist, newE):
    """Compute a new DOS histogram from the given DOS using the new energy array by interpolation

    Parameters
    ----------
    doshist: histogram
        input DOS

    newE:numpy array of floats
        new energy centers in meV

    """
    import histogram as H
    import numpy as np

    try:
        E = doshist.energy
    except:
        E = doshist.E
    #
    newS = np.interp(newE, E, doshist.I)
    newS_E2 = np.interp(newE, E, doshist.E2)
    Eaxis = H.axis("E", newE, unit="meV")
    newHist = H.histogram("DOS", [Eaxis], data=newS, errors=newS_E2)
    return newHist
