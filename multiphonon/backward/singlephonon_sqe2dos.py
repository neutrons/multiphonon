#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import histogram as H
import numpy as np


class EnergyAxisMissingBinCenterAtZero(Exception):
    pass


def sqe2dos(sqe, T, Ecutoff, elastic_E_cutoff, M, initdos=None, update_weights=None):
    """Given a single-phonon SQE, compute DOS

    The basic procedure is
     * construct an initial guess of DOS
     * use this DOS to compute 1-phonon SQE
     * for both exp and sim SQE, integrate along Q to obtain S(E)
     * scale the initial guess DOS by the S(E) ratio
     * optionally we can do this again

    Parameters
    ----------
    sqe:histogram
        S(Q,E)

    T:float
      Temperature (kelvin)

    Ecutoff:float
        Cutoff energy beyond which DOS must be zero

    Elastic_E_cutoff: 2-tuple of floats
        Cutoff energy bracket for removing the elastic line (unit: meV)

    M:float
        Atomic mass

    initdos:histogram
        initial guess of DOS

    update_weights:2-tuple of floats
        weights for DOS update strategies (continuity, area conservation)

    """
    # create initial guess of dos
    Efull = sqe.E
    dE = sqe.E[1] - sqe.E[0]
    assert dE > 0, "Energy axis must be incremental"
    Eplus = Efull[Efull > -dE / 2]
    if abs(Eplus[0]) > dE / 1e6:
        raise EnergyAxisMissingBinCenterAtZero('"0" must be one of the bin centers of the energy axis')
    Eplus[0] = 0.0
    if initdos is None:
        initdos = guess_init_dos(Eplus, Ecutoff)
    else:
        # make sure the energy axis is compatible with sqe
        dos_Eaxis_part1 = initdos[(Eplus[0], Eplus[-1])].E
        if dos_Eaxis_part1.size != Eplus.size or not np.allclose(dos_Eaxis_part1, Eplus):
            raise RuntimeError("Incompatible energy axis. DOS: %s, SQE: %s" % (dos_Eaxis_part1, Eplus))
        pass
    # compute sqe from dos
    from ..forward.phonon import computeSQESet, kelvin2mev

    Q = sqe.Q
    dQ = Q[1] - Q[0]
    E = sqe.E
    dE = E[1] - E[0]
    beta = 1.0 / (T * kelvin2mev)
    Q2, E2, sqeset = computeSQESet(1, Q, dQ, initdos.E, dE, M, initdos.I, beta)
    # compute S(E) from SQE
    # - experiment
    # -- only need the positive part
    expsqe = sqe.copy()
    expsqe_Epositive = expsqe[(), (dE / 10, None)].I
    expsqeE2_Epositive = expsqe[(), (dE / 10, None)].E2
    mask = expsqe_Epositive != expsqe_Epositive
    expsqe_Epositive[mask] = 0
    expsqeE2_Epositive[mask] = 0
    expse = expsqe_Epositive.sum(0)
    expse_E2 = expsqeE2_Epositive.sum(0)
    # - simulation
    simsqe_arr = sqeset[0]
    simsqe = H.histogram("simsqe", [("Q", Q2, "1./angstrom"), ("E", E2, "meV")], simsqe_arr)
    simsqe_Epositive = simsqe[(), (Eplus[0], Eplus[-1])]
    simsqe_Epositive.I[mask] = 0
    simse = simsqe_Epositive.I.sum(0)
    # apply scale factor to dos
    # but only at the range of the measurement
    N_Eplus = Eplus.size
    dos_in_range = initdos[(Eplus[0], Eplus[-1])].copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        dos_in_range.I *= expse / simse
    # remember the relative error of the dos
    dos_relative_error = expse_E2**0.5 / expse
    # clean up bad values
    dos_in_range.I[dos_in_range.I != dos_in_range.I] = 0
    # clean up data near elastic line
    n_small_E = (Eplus < elastic_E_cutoff[1]).sum()
    dos_in_range.I[:n_small_E] = Eplus[:n_small_E] ** 2 * dos_in_range.I[n_small_E] / Eplus[n_small_E] ** 2
    # keep positive
    dos_in_range.I[dos_in_range.I < 0] = 0
    dos_in_range.E2[:] = (dos_in_range.I * dos_relative_error) ** 2
    # DOS range to update should be smaller than SQE E range, so we need to
    Emin = Eplus[0]
    Emax = min(Eplus[-1], Ecutoff)
    dos_to_update = dos_in_range[(Emin, min(Eplus[-1], Emax * 2))]
    # update
    return update_dos(initdos, dos_to_update, Emin, Emax, weights=update_weights)


def update_dos(original_dos_hist, new_dos_hist, Emin, Emax, weights=None):
    # only if the spectrum is nontrivial beyond Emax, we need rescale
    """Parameters
    ----------
    original_dos_hist:histogram
        original phonon density of states

    new_dos_hist:histogram
        new phonon density of states

    Emin:float
        minimum value for energy transfer axis

    Emax:float
        maximum value for energy transfer axis

    weights:float
        weights for DOS update strategies (continuity, area conservation)

    """
    from .stitch_dos import DOSStitcher

    stitch = DOSStitcher(weights)
    return stitch(original_dos_hist, new_dos_hist, Emin, Emax)


def guess_init_dos(E, cutoff):
    """Return an initial DOS

    It is x^2 near E=0, and flat after that, until it reaches
    maximum E.
    """
    dos = np.ones(E.size, dtype=float)
    dos[E > cutoff] = 0.0
    end_of_E2_zone = cutoff / 3.0
    dos[E < end_of_E2_zone] = (E * E / end_of_E2_zone / end_of_E2_zone)[E < end_of_E2_zone]
    dE = E[1] - E[0]
    norm = np.sum(dos) * dE
    g = dos / norm
    Eaxis = H.axis("E", E, "meV")
    return H.histogram("DOS", [Eaxis], data=g)


# the following methods are obsolete
"""
def update_dos_continuous(original_dos_hist, Emin, Emax, g, gerr):
    return update_dos_(original_dos_hist, Emin, Emax, g, gerr, compute_scalefactor_using_continuous_criteria)

def update_dos_keep_area(original_dos_hist, Emin, Emax, g, gerr):
    "update the lower E portion of the dos by keeping the area of the updated portion intact"
    return update_dos_(original_dos_hist, Emin, Emax, g, gerr, compute_scalefactor_using_area_criteria)

def update_dos_(original_dos_hist, Emin, Emax, g, gerr, compute_scalefactor):
    "update the lower E portion of the dos by using a function to compute the scale factor"
    scale = compute_scalefactor(original_dos_hist, Emin, Emax, g)
    g *= scale
    # compute error bar
    gerr *= scale
    # compute new DOS
    newdos = original_dos_hist.copy()
    # by updating only the front portion
    newdos[(Emin, Emax)].I[:] = g
    newdos[(Emin, Emax)].E2[:] = gerr**2
    # now renormalize
    norm = newdos.I.sum()
    newdos.I/=norm
    newdos.E2/=norm*norm
    return newdos
"""

# End of file
