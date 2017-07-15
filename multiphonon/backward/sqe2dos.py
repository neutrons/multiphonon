#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os


def sqe2dos(
        sqe, T, Ecutoff, elastic_E_cutoff, M,
        C_ms=None, Ei=None,
        workdir = 'work', 
        MAX_ITERATION = 20, TOLERATION = 1e-4,
        ):
    """Given a SQE, compute DOS
    * Start with an initial guess of DOS and a SQE
    * Calculate SQE of multiphonon scattering
    * Calculate SQE of multiple scattering using C_ms and multiphonon scattering SQE
    * Subtract MS and MP SQE from the experimental SQE to obtain single-phonon SQE
    * Compute a new DOS from the single-phonon SQE
    * Compare the new DOS to the previous one and calculate the difference
    * If difference is large, continue the iteration. Otherwise the new DOS is what we want
    
    Parameters:
      - sqe: measured S(Q,E) histogram
      - T: temperature (Kelvin)
      - Ecutoff: max phonon energy (meV)
      - elastic_E_cutoff: 2-tuple of floats. cutoff for elastic peak
      - M: average atomic mass (amu)
      - C_ms: ratio of multiple scattering over multiphonon scattering
      - Ei: incident energy
    """
    mask = sqe.I != sqe.I    
    corrected_sqe = sqe
    prev_dos = None
    total_rounds = 0
    for roundno in range(MAX_ITERATION):
        # compute dos.
        # corrected_sqe: the most recent corrected sqe histogram. same shape as input sqe
        dos = singlephonon_sqe2dos(
            corrected_sqe, T, Ecutoff, elastic_E_cutoff, M)
        # dos only contains positive portion of the Eaxis of the corrected_sqe
        yield dos
        # compute expected sqe
        from ..forward import dos2sqe
        # all sqes are histograms and have the same axes of the input experimental sqe
        # the tot_inel_sqe is masked by the input experimental sqe
        singlephonon_sqe, mpsqe, mssqe, tot_inel_sqe = dos2sqe(
            dos, C_ms, sqe, T, M, Ei
        )
        # scale exp sqe for comparision.
        # after scale the total intensity of the E>elastic_E_cutoff[1] portion of the exp sqe
        # matches that of the tot_inel_sqe
        scale_expsqe_to_match_inel_se(sqe, tot_inel_sqe, elastic_E_cutoff[-1])
        # compute SQE correction
        sqe_correction = mpsqe + mssqe
        # compute corrected SQE
        corrected_sqe = sqe + sqe_correction * (-1., 0)
        # compute residual
        residual_sqe = corrected_sqe + singlephonon_sqe * (-1., 0)
        # save intermediate results
        cwd = os.path.join(workdir, "round-%d" % roundno)
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        def savesqe(sqe, fn):
            sqe.I[mask] = np.nan
            hh.dump(sqe, os.path.join(cwd, fn))
            return
        savesqe(sqe, 'exp-sqe.h5')
        savesqe(mpsqe, 'mp-sqe.h5')
        savesqe(mssqe, 'ms-sqe.h5')
        savesqe(sqe_correction, 'sqe_correction.h5')
        savesqe(corrected_sqe, 'corrected_sqe.h5')
        savesqe(singlephonon_sqe, 'sp-sqe.h5')
        savesqe(residual_sqe, 'residual-sqe.h5')
        savesqe(tot_inel_sqe, 'total-inel-sqe.h5')
        # save DOS
        hh.dump(dos, os.path.join(cwd, 'dos.h5'))
        # write scripts
        create_script(
            os.path.join(cwd, "plot_sqe.py"),
            plot_intermediate_result_sqe_code
        )
        create_script(
            os.path.join(cwd, "plot_se.py"),
            plot_intermediate_result_se_code
        )
        total_rounds += 1
        if prev_dos:
            if isclose(dos, prev_dos, TOLERATION):
                break
        prev_dos = dos
        continue
    # in the end, add error of residual to the error bar 
    # of the DOS
    def get_pos_se(sqe):
        s = sqe[(), (elastic_E_cutoff[-1],None)].copy()
        s.I[s.I!=s.I] = 0
        return s.sum('Q')
    residual_pos_se = get_pos_se(residual_sqe)
    exp_pos_se = get_pos_se(sqe)
    rel_err_from_residual = np.abs(residual_pos_se.I)/exp_pos_se.I
    # add to the error bar
    final_dos = dos.copy()
    final_dos_subset = final_dos[(residual_pos_se.E[0], residual_pos_se.E[-1])]
    final_dos_subset.E2 += (final_dos_subset.I * rel_err_from_residual)**2
    hh.dump(final_dos, os.path.join(workdir, "final-dos.h5"))
    #
    create_script(
        os.path.join(workdir, 'plot_dos_iteration.py'),
        plot_dos_iteration_code % dict(total_rounds=total_rounds)
    )
    computeDirtyDOS(sqe, final_dos, M, T, os.path.join(workdir, 'dirdydos'))
    return


def computeDirtyDOS(sqe, dos, M, T, workdir):
    """dirty dos calculation is procedure that quickly 
    "correct" sqe using the one-phonon Q multiplier.
    After correction, the sqe would look like mostly Q-independent,
    and the sum over Q axis can give a very rough estimate of the DOS.
    This is mostly for double-checking the calculations.
    """
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    from ..forward.phonon import computeSNQ, DWExp, kelvin2mev, gamma0
    beta = 1./(T*kelvin2mev)
    E = dos.E; Q = sqe.Q; g = dos.I
    dE = E[1] - E[0]
    DW2 = DWExp(Q, M, E, g, beta, dE)
    sq = computeSNQ(DW2, 1)
    sqe1 = sqe.copy()
    sqe1.I /= sq[:, np.newaxis]
    sqe1.E2 /= sq[:, np.newaxis] * sq[:, np.newaxis]
    hh.dump(sqe1, os.path.join(workdir, 'corrected-sqe.h5'))
    # compute a sum to obtain S(E)
    Qdiff = Q[-1]-Q[0]
    # take the middle part. 1/6 is kind of arbitrary
    se1 = sqe1[ (Q[0]+Qdiff/6., Q[-1]-Qdiff/6.), (E[0], None) ].sum('Q')
    hh.dump(se1, os.path.join(workdir, 'se.h5'))
    assert np.allclose(se1.E, E)
    # 
    g0 = gamma0(E,g, beta, dE)
    fE = (1-np.exp(-se1.E*beta)) * se1.E * g0
    ddos = se1.copy()
    ddos.I *= fE
    ddos.E2 *= fE*fE
    hh.dump(ddos, os.path.join(workdir, 'ddos.h5'))
    return


def scale_expsqe_to_match_inel_se(expsqe, simsqe, elastic_E_positive_cutoff):
    # Compute norm_adjustment
    def get_pos_tot_int(sqe):
        subset = sqe[(), (elastic_E_positive_cutoff,None)].copy().I
        subset[subset!=subset] = 0
        return subset.sum()
    norm_adjustment = get_pos_tot_int(simsqe)/get_pos_tot_int(expsqe)
    expsqe.I *= norm_adjustment
    expsqe.E2 *= norm_adjustment**2
    return


def isclose(dos1, dos2, TOLERATION):
    return np.allclose(dos1.I, dos2.I, rtol=TOLERATION, atol=TOLERATION)


def create_script(fn, content):
    open(fn, 'wt').write(content)
    import stat
    st = os.stat(fn)
    os.chmod(fn, st.st_mode | stat.S_IEXEC)
    return


def removeElasticPeak(sqe, elastic_E_cutoff):
    negEcut, posEcut = elastic_E_cutoff
    E = sqe.E; dE = E[1]-E[0]
    left = sqe[(), (None, negEcut-dE)]
    leftindex = left.I.shape[1]
    right = sqe[(), (posEcut+dE, None)]
    rightindex = sqe.I.shape[1] - right.I.shape[1]
    leftIs = sqe.I[:, leftindex]
    rightIs = sqe.I[:, rightindex]
    dI = rightIs - leftIs
    increments = np.arange(0, 1., 1./(rightindex-leftindex))
    increments = np.tile(increments, sqe.Q.size)
    increments.shape = sqe.Q.size, -1
    increments *= dI[:, np.newaxis]
    linear_interp_I = leftIs[:, np.newaxis] + increments
    sqe[(), elastic_E_cutoff].I[:] = linear_interp_I
    return sqe                                                        


def normalizeExpSQE(sqe):
    # integration of S(E) should be 1 for every Q
    # the idea here is to for each Q, we calculate 
    # a normalization factor, and then take the median of
    # all normalization factors.
    mask = sqe.I != sqe.I
    copy = sqe.copy()
    copy.I[mask] = 0
    E = sqe.E; dE = E[1] - E[0]
    Q = sqe.Q; dQ = Q[1] - Q[0]
    sq = copy.sum('E')
    # sq.I should be normalized to 1 for each Q
    # but since we are not measuring the fulling dynamical
    # range due to limitation of instrument and Ei
    # that normalization holds true only at a small
    # region at low Q, but not too low. 
    # so we take a front portion of the Q axis
    # and ignore the very low Q where the dynamical range
    # is cut off (those are marked by nans)
    # the 1/3 factor below is kind of arbitrary
    average_sq = np.nanmean(sq[(None, sq.Q[-1]*1/2.)].I)*dE
    norm = 1./average_sq
    norm = 1./(np.nansum(sqe.I)*dE/Q.size)
    sqe.I *= norm
    sqe.E2 *= norm*norm
    return sqe
    

# this is also OK but not as simple and robust as normalizeExpSQE
def normalizeExpSQE_inelonly(sqe, dos, M, beta, elastic_E_cutoff):
    # integration of inelastic S(E) should be 1-exp(-2W) for every Q
    # the idea here is to for each Q, we calculate 
    # a normalization factor, and then take the median of
    # all normalization factors.
    sqe1 = removeElasticPeak(sqe.copy(), elastic_E_cutoff)
    from ..forward import phonon as forward
    Q = sqe.Q
    E = dos.E; g = dos.I; dE = E[1] - E[0]
    DW2 = forward.DWExp(Q, M, E,g, beta, dE)
    DW = np.exp(-DW2)
    integration = 1 - DW
    I = sqe1.I
    ps = I.sum(1) * dE
    # 
    norm_factors = integration/ps
    norm = np.median(norm_factors)
    sqe.I *= norm
    sqe.E2 *= norm*norm
    return sqe
    

# 
from singlephonon_sqe2dos import sqe2dos as singlephonon_sqe2dos
from ._sqe2dos_script_templates import plot_intermediate_result_sqe_code,\
    plot_intermediate_result_se_code, plot_dos_iteration_code

# End of file 
