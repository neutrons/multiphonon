#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H

def onephononsqe2dos(sqe, T, Ecutoff, elastic_E_cutoff, M):
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
    Elastic_E_cutoff: cutoff energy for removing the elastic line
    M: atomic mass

    The basic procedure is
    * construct an initial guess of DOS
    * use this DOS to compute 1-phonon SQE
    * for both exp and sim SQE, integrate along Q to obtain S(E)
    * scale the initial guess DOS by the S(E) ratio
    * optionally we can do this again
    """ 
    # create initial guess of dos
    Efull = sqe.E
    dE = sqe.E[1] - sqe.E[0]
    Eplus = Efull[Efull>-dE/2]
    assert Eplus[0] < dE/1e6
    Eplus[0] = 0.
    initdos = guess_init_dos(Eplus, Ecutoff)
    # compute sqe from dos
    from ..forward import computeSQESet, kelvin2mev
    Q = sqe.Q
    dQ = Q[1] - Q[0]
    E = sqe.E
    dE = E[1] - E[0]
    beta = 1./(T*kelvin2mev)    
    Q2, E2, sqeset = computeSQESet(1, Q,dQ, Eplus,dE, M, initdos, beta)
    length = min(E2.size, E.size)
    assert np.allclose(E2[-length:], E[-length:])
    # compute S(E) from SQE
    # - experiment
    # -- only need the positive part
    expsqe_Epositive = sqe[(), (-dE/2, None)].I
    expsqeE2_Epositive = sqe[(), (-dE/2, None)].E2
    mask = expsqe_Epositive != expsqe_Epositive
    expsqe_Epositive[mask] = 0
    expsqeE2_Epositive[mask] = 0
    expse = expsqe_Epositive.sum(0)
    expse_E2 = expsqeE2_Epositive.sum(0)
    # - simulation
    simsqe = sqeset[0]
    simsqe_Epositive = simsqe[:, -expse.shape[-1]:]
    simsqe_Epositive[mask] = 0
    simse = simsqe_Epositive.sum(0)
    # apply scale factor to dos
    dos = initdos * (expse/simse)
    dos_relative_error = expse_E2**.5 / expse
    # clean up bad values
    dos[dos!=dos] = 0
    # clean up data near elastic line
    n_small_E = (Eplus<elastic_E_cutoff).sum()
    dos[:n_small_E] = Eplus[:n_small_E] ** 2 * dos[n_small_E] / Eplus[n_small_E]**2
    # normalize
    dos /= dos.sum()*dE
    dos_error = dos * dos_relative_error
    Eaxis = H.axis("E", Eplus, 'meV')
    h = H.histogram("DOS", [Eaxis], data=dos, errors=dos_error**2)
    return h


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

# alias
onephonon = onephononsqe2dos


# End of file 
