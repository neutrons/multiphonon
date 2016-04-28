#!/usr/bin/env python
#
# Jiao Lin


import histogram as H, numpy as np

def interp(iqehist, newE):
    """compute a new IQE histogram using the new energy array
    
    * iqehist: input IQE histogram
    * newE: new energy centers array
    """
    from scipy import interpolate
    mask = iqehist.I != iqehist.I
    # find energy boundaries of dynamic range for each Q 
    def get_boundary_indexes(a):
        nz = np.nonzero(a)[0]
        if nz.size:
            return nz[0], nz[-1]
        else:
            return 0,0
    boundary_indexes = [
        get_boundary_indexes(row)
        for row in np.logical_not(mask)
    ]
    E = iqehist.energy
    Eranges = [ 
        (E[ind1], E[ind2])
        for ind1, ind2 in boundary_indexes
    ]
    #
    iqehist.I[mask] = 0
    Q = iqehist.Q
    f = interpolate.interp2d(E, Q, iqehist.I, kind='linear')
    dE = E[1] - E[0]
    Emin = E[0]//dE * dE
    Emax = E[-1]//dE * dE
    Enew = np.arange(Emin, Emax+dE/2, dE)
    newS = f(Enew, iqehist.Q)
    # create new histogram
    Eaxis = H.axis("E", Enew, unit='meV')
    Qaxis = H.axis("Q", Q, unit='1./angstrom')
    newHist = H.histogram("IQE", [Qaxis, Eaxis], data=newS)
    #
    for Erange, q in zip(Eranges, Q):
        Emin, Emax = Erange
        Emin = max(Emin, Enew[0])
        Emax = min(Emax, Enew[-1])
        newHist[q, (None, Emin)].I[:] = np.nan
        newHist[q, (Emax, None)].I[:] = np.nan
        continue
    return newHist


# End of file 
