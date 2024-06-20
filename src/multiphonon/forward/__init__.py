#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>


import numpy as np


def dos2sqe(dos, C_ms, sqe, T, M, Ei):
    """Calculate SQE from DOS.

    The computed SQE has similar props as the given (experimental) SQE.

    Parameters
    ----------
    dos: histogram
        Phonon density of states

    C_ms:float
        MS = C_ms * MP

    sqe:histogram
        S(Q,E)

    T: float
        Temperature (Kelvin)

    M: float
        Atomic mass

    Ei: float
        Incident energy (meV)

    """
    Q, E = sqe.Q, sqe.E
    dQ = Q[1] - Q[0]
    Qmin = Q[0]
    Qmax = Q[-1] + dQ / 2.0
    dE = E[1] - E[0]
    Efirst = E[0]
    Elast = E[-1]
    mask = sqe.I != sqe.I

    from . import phonon

    # compute one phonon SQE
    singlephonon_sqe = phonon.sqehist(
        dos.E,
        dos.I,
        starting_order=1,
        N=1,
        T=T,
        M=M,
        Qmin=Qmin,
        Qmax=Qmax,
        dQ=dQ,
    )[(), (Efirst, Elast)].rename("SP SQE")
    # compute MP sqe
    mpsqe = phonon.sqehist(
        dos.E,
        dos.I,
        starting_order=2,
        N=4,
        T=T,
        M=M,
        Qmin=Qmin,
        Qmax=Qmax,
        dQ=dQ,
    )[(), (Efirst, Elast)].rename("MP SQE")
    # compute MS sqe
    from .. import ms

    mssqe = ms.sqe(mpsqe, Ei)
    mssqe.I[:] *= C_ms
    # total expected inelastic sqe computed from trial DOS
    tot_inel_sqe = singlephonon_sqe + mpsqe + mssqe
    tot_inel_sqe.I[mask] = np.nan
    return singlephonon_sqe, mpsqe, mssqe, tot_inel_sqe
