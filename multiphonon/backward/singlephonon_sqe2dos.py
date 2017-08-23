#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os

class EnergyAxisMissingBinCenterAtZero(Exception): pass


def sqe2dos(sqe, T, Ecutoff, elastic_E_cutoff, M, initdos=None, update_weights=None):
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
    update_weights: weights for DOS update strategies (continuity, area conservation)

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
    assert dE>0, "Energy axis must be incremental"
    Eplus = Efull[Efull>-dE/2]
    if abs(Eplus[0]) > dE/1e6:
        raise EnergyAxisMissingBinCenterAtZero('"0" must be one of the bin centers of the energy axis')
    Eplus[0] = 0.
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
    dos_in_range = initdos[(Eplus[0], Eplus[-1])].copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        dos_in_range.I *= expse/simse
    # remember the relative error of the dos
    dos_relative_error = expse_E2**.5 / expse
    # clean up bad values
    dos_in_range.I[dos_in_range.I!=dos_in_range.I] = 0
    # clean up data near elastic line
    n_small_E = (Eplus<elastic_E_cutoff[1]).sum()
    dos_in_range.I[:n_small_E] = Eplus[:n_small_E] ** 2 * dos_in_range.I[n_small_E] / Eplus[n_small_E]**2
    # keep positive
    dos_in_range.I[dos_in_range.I<0] = 0
    # DOS range to update should be smaller than SQE E range, so we need to
    dos_to_update = dos_in_range[(Eplus[0], min(Eplus[-1], Ecutoff))]
    # update
    return update_dos(initdos, dos_to_update.E[0], dos_to_update.E[-1],
                      g=dos_to_update.I, gerr=dos_to_update.I*dos_relative_error[:dos_to_update.I.size],
                      weights=update_weights)

def update_dos(original_dos_hist, Emin, Emax, g, gerr, weights=None):
    # only if the spectrum is nontrivial beyond Emax, we need rescale
    assert original_dos_hist.E[-1] >= Emax
    dE = original_dos_hist.E[1]-original_dos_hist.E[0]
    if Emax+dE > original_dos_hist.E[-1]:
        rescale = False
    else:
        g_beyond_range = original_dos_hist[(Emax+dE,None)].I
        assert np.all(g_beyond_range >= 0)
        rescale = g_beyond_range.sum() > 0
    # if need rescale, calculate the factor using some strategies and take weighted average
    if rescale:
        import warnings
        scale1 = compute_scalefactor_using_continuous_criteria(original_dos_hist, Emin, Emax, g)
        scale2 = compute_scalefactor_using_area_criteria(original_dos_hist, Emin, Emax, g)
        if np.isinf(scale1) or np.isnan(scale1):
            # this can happen if the original dos has value zero
            warnings.warn(
                "fail to use the continuous criteria to determine the scale factor for combining DOSes"
                )
            scale = scale2
        else:
            if abs(scale1-scale2)/scale1 > 0.05:
                warnings.warn(
                    "Scaling factor to combine DOSes calculated is not stable: %s (using continuous criteria) vs %s (using area criteria)\n"
                    "You may want to consider adjusting the parameters such as E range (Emax more specifically)" % (scale1, scale2)
                )
            if weights is None:
                weights = [.5, .5]
            scale = np.dot([scale1, scale2], weights)
        assert scale == scale and not np.isinf(scale), "scale is a bad number: %s" % scale
        g *= scale
        # compute error bar
        gerr *= scale
    # compute new DOS
    newdos = original_dos_hist.copy()
    # by updating only the front portion
    lowEportion = newdos[(Emin, Emax)]
    lowEportion.I[:] = g
    lowEportion.E2[:] = gerr**2
    # now renormalize
    return normalize_dos(newdos)


def normalize_dos(dos_hist):
    dE = dos_hist.E[1]-dos_hist.E[0]
    norm = dos_hist.I.sum()*dE
    dos_hist.I/=norm
    dos_hist.E2/=norm*norm
    return dos_hist
    

def compute_scalefactor_using_area_criteria(original_dos_hist, Emin, Emax, g):
    "update the lower E portion of the dos by keeping the area of the updated portion intact"
    expected_sum = original_dos_hist[(Emin, Emax)].I.sum()
    sum_now = g.sum()
    return expected_sum/sum_now

def compute_scalefactor_using_continuous_criteria(original_dos_hist, Emin, Emax, g):
    "update the lower E portion of the dos by keeping the DOS value at maximum E the same as the original DOS"
    v_at_Emax = original_dos_hist[Emax][0]
    v_now_at_Emax = g[-1]
    return v_at_Emax/v_now_at_Emax


def guess_init_dos(E, cutoff):
    """return an initial DOS

    It is x^2 near E=0, and flat after that, until it reaches
    maximum E.
    """
    dos = np.ones(E.size, dtype=float)
    dos[E>cutoff] = 0.
    end_of_E2_zone = cutoff/3.
    dos[E<end_of_E2_zone] = (E*E/end_of_E2_zone/end_of_E2_zone)[E<end_of_E2_zone]
    dE = E[1] - E[0]
    norm = np.sum(dos) * dE
    g = dos / norm
    Eaxis = H.axis("E", E, 'meV')
    return H.histogram("DOS", [Eaxis], data=g)

# the following methods are obsolete
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

# End of file 
