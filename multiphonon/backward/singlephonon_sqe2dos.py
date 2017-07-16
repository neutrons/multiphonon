#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os

def sqe2dos(sqe, T, Ecutoff, elastic_E_cutoff, M, initdos=None):
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
    initdos: initial DOS histogram. Its energy axis starts with
             the positive energy axis of sqe histogram. be aware that
             it might extend beyond the largest E bin of sqe

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
    if initdos is None:
        initdos = guess_init_dos(Eplus, Ecutoff)
    else:
        # make sure the energy axis is compatible with sqe
        dos_Eaxis_part1 = initdos[(Eplus[0], Eplus[-1])].E
        assert np.allclose(dos_Eaxis_part1, Eplus)
        pass
    # compute sqe from dos
    from ..forward.phonon import computeSQESet, kelvin2mev
    Q = sqe.Q
    dQ = Q[1] - Q[0]
    E = sqe.E
    dE = E[1] - E[0]
    beta = 1./(T*kelvin2mev)    
    Q2, E2, sqeset = computeSQESet(1, Q,dQ, initdos.E,dE, M, initdos.I, beta)
    # compute S(E) from SQE
    # - experiment
    # -- only need the positive part
    expsqe = sqe.copy()
    expsqe_Epositive = expsqe[(), (-dE/2, None)].I
    expsqeE2_Epositive = expsqe[(), (-dE/2, None)].E2
    mask = expsqe_Epositive != expsqe_Epositive
    expsqe_Epositive[mask] = 0
    expsqeE2_Epositive[mask] = 0
    expse = expsqe_Epositive.sum(0)
    expse_E2 = expsqeE2_Epositive.sum(0)
    # - simulation
    simsqe_arr = sqeset[0]
    simsqe = H.histogram('simsqe', [('Q', Q2, '1./angstrom'), ('E', E2, 'meV')], simsqe_arr)
    simsqe_Epositive = simsqe[(), (Eplus[0], Eplus[-1])]
    simsqe_Epositive.I[mask] = 0
    simse = simsqe_Epositive.I.sum(0)
    # apply scale factor to dos
    # but only at the range of the measurement
    N_Eplus = Eplus.size
    dos_in_range = initdos.I[:N_Eplus].copy()
    # save the expected sum
    expected_sum = dos_in_range.sum()
    dos_in_range *= expse/simse
    # remember the relative error of the dos
    dos_relative_error = expse_E2**.5 / expse
    # clean up bad values
    dos_in_range[dos_in_range!=dos_in_range] = 0
    # clean up data near elastic line
    n_small_E = (Eplus<elastic_E_cutoff[1]).sum()
    dos_in_range[:n_small_E] = Eplus[:n_small_E] ** 2 * dos_in_range[n_small_E] / Eplus[n_small_E]**2
    # keep positive
    dos_in_range[dos_in_range<0] = 0
    # scale
    sum_now = dos_in_range.sum()
    dos_in_range *= expected_sum/sum_now
    # compute error bar
    dos_error = dos_in_range * dos_relative_error
    # compute new DOS
    newdos = initdos.copy()
    # by updating only the front portion
    newdos[(Eplus[0], Eplus[-1])].I[:] = dos_in_range
    newdos[(Eplus[0], Eplus[-1])].E2[:] = dos_error**2
    return newdos


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
    g = dos / norm
    Eaxis = H.axis("E", E, 'meV')
    return H.histogram("DOS", [Eaxis], data=g)


# End of file 
