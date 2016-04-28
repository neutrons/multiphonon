#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np

def sqe2dos(sqe, T, Ecutoff, M):
    """ 
    Given a one-phonon sqe, compute dos

    sqe:
      For a simulated sqe, this is easy.
      For an experimental sqe, the part around elastic line
      has be masked as NaNs.
      It is assumed that the E axis is symmetric about
      zero, and zero is one of the E values (or close to zero).

    T: temperature (kelvin)
    Ecutoff: beyond this DOS must be zero
    M: atomic mass

    The basic procedure is
    * construct an initial guess of DOS
    * use this DOS to compute 1-phonon SQE
    * for both exp and sim SQE, integrate along Q to obtain S(E)
    * scale the initial guess DOS by the S(E) ratio
    * optionally we can do this again
    """ 
    Efull = sqe.E
    dE = sqe.E[1] - sqe.E[0]
    Eplus = Efull[Efull>-dE/2]
    assert Eplus[0] < dE/1e6
    Eplus[0] = 0.
    initdos = guess_init_dos(Eplus, Ecutoff)
    
    from ..forward import computeSQESet, kelvin2mev
    Q = sqe.Q
    dQ = Q[1] - Q[0]
    E = sqe.E
    dE = E[1] - E[0]
    beta = 1./(T*kelvin2mev)    
    Q2, E2, sqeset = computeSQESet(1, Q,dQ, Eplus,dE, M, initdos, beta)
    assert np.allclose(E2, E)
    simsqe = sqeset[0]
    expse = sqe[(), (-dE/2, None)].I.sum(0)
    simse = simsqe[:, -expse.shape[-1]:].sum(0)
    dos = initdos * (expse/simse)
    return dos


def guess_init_dos(E, cutoff):
    """return an initial DOS

    It is x^2 near E=0, and flat after that, until it reaches
    maximum E.
    """
    dos = np.ones(E.size, dtype=float)
    dos[E>cutoff] = 0
    end_of_E2_zone = cutoff/3.
    dos[E<end_of_E2_zone] = (E*E/end_of_E2_zone/end_of_E2_zone)[E<end_of_E2_zone]
    dE = E[1] - E[0]
    norm = np.sum(dos) * dE
    return dos / norm


# End of file 
