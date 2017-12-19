#!/usr/bin/env python
#
# Jiao Lin


import histogram as H, numpy as np

def plot(iqe):
    """ Parameters
    ----------

    iqe: histogram
        input IQE

    """
    Q = iqe.Q
    try:
        E= iqe.energy
    except:
        E = iqe.E
        pass
    Qg, Eg = np.mgrid[Q[0]:Q[-1]+1e-5:Q[1]-Q[0], E[0]:E[-1]+1e-5:E[1]-E[0]]
    import numpy.ma as ma
    Zm = ma.array(iqe.I, mask=np.isnan(iqe.I))
    from matplotlib import pyplot as plt
    plt.pcolormesh(Qg, Eg, Zm)
    plt.clim(0, np.nanmax(iqe.I))
    plt.xlim(np.min(Q), np.max(Q))
    plt.ylim(np.min(E), np.max(E))
    plt.colorbar()
    return


def interp(iqehist, newE):
    """compute a new IQE histogram using the new energy array
    
    Parameters
    ----------

    iqehist: histogram
        input IQE

    newE:float
        new energy centers array

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
    try:
        E = iqehist.energy
    except:
        E = iqehist.E
    Eranges = [ 
        (E[ind1], E[ind2])
        for ind1, ind2 in boundary_indexes
    ]
    #
    iqehist.I[mask] = 0
    iqehist.E2[mask] = 0
    Q = iqehist.Q
    f = interpolate.interp2d(E, Q, iqehist.I, kind='linear')
    E2f = interpolate.interp2d(E, Q, iqehist.E2, kind='linear')
    dE = E[1] - E[0]
    Emin = E[0]//dE * dE
    Emax = E[-1]//dE * dE
    # Enew = np.arange(Emin, Emax+dE/2, dE)
    newS = f(newE, Q)
    newS_E2 = E2f(newE, Q)
    # create new histogram
    Eaxis = H.axis("E", newE, unit='meV')
    Qaxis = H.axis("Q", Q, unit='1./angstrom')
    newHist = H.histogram("IQE", [Qaxis, Eaxis], data=newS, errors=newS_E2)
    #
    for Erange, q in zip(Eranges, Q):
        Emin, Emax = Erange
        if Emin > newE[0]:
            Emin = min(Emin, newE[-1])
            newHist[q, (None, Emin)].I[:] = np.nan
            newHist[q, (None, Emin)].E2[:] = np.nan
        if Emax < newE[-1]:
            Emax = max(Emax, newE[0])
            newHist[q, (Emax, None)].I[:] = np.nan
            newHist[q, (Emax, None)].E2[:] = np.nan
        continue
    return newHist



def dynamical_range_mask(sqe, Ei):
    """calculate a mask of dynamical range being measured
    at the given incident energy.
    0 means within dynamical range

    Parameters
    ----------

    sqe: histogram
        S(Q,E)

    Ei:float
        incident energy

    """
    Q = sqe.Q
    E = sqe.E
    Ef = Ei - E
    from ..units.neutron import e2k, SE2K
    ki = e2k(Ei)
    kf = Ef ** .5 * SE2K
    import numpy as np
    kf = np.tile(kf, Q.size)
    kf.shape = Q.size, -1
    Q2d = np.repeat(Q, E.size)
    Q2d.shape = Q.size, -1
    mask = np.zeros(sqe.I.shape, dtype="bool")
    mask = (ki+kf > Q2d) * (ki+Q2d > kf) * (kf+Q2d > ki)
    return np.logical_not(mask)


# End of file 
