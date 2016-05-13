#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os


def sqe2dos(
        sqe, T, Ecutoff, elastic_E_cutoff, M, C_ms=None, Ei=None,
        workdir = 'work', 
        MAX_ITERATION = 20, TOLERATION = 1e-4,
        ):
    """Given a SQE, compute DOS
    * Start with a initial guess of DOS and a SQE
    * Calculate SQE of multiphonon scattering
    * Calculate SQE of multiple scattering using C_ms and multiphonon scattering SQE
    * Subtract MS and MP SQE from the experimental SQE to obtain single-phonon SQE
    * Compute a new DOS from the single-phonon SQE
    * Compare the new DOS to the previous one and calculate the difference
    * If difference is large, continue the iteration. Otherwise the new DOS is what we want
    """
    Q, E = sqe.Q, sqe.E
    dQ = Q[1]-Q[0]; Qmin = Q[0]; Qmax=Q[-1] + dQ/2.
    dE = E[1]-E[0]; Efirst = E[0]; Elast=E[-1]
    mask = sqe.I != sqe.I
    
    corrected_sqe = sqe
    prev_dos = None
    total_rounds = 0
    for roundno in range(MAX_ITERATION):
        # compute dos
        dos = singlephonon_sqe2dos(
            corrected_sqe, T, Ecutoff, elastic_E_cutoff, M)
        yield dos
        # should compare to previous round and break 
        # if change is little
        # ...
        # normalize exp SQE
        from ..forward import kelvin2mev
        beta = 1./(T*kelvin2mev)
        sqe = normalizeExpSQE(sqe)
        #
        from .. import forward
        # compute one phonon SQE as well
        singlephonon_sqe = forward.sqehist(
            dos.E, dos.I,
            T=T, M=M,
            Qmin=Qmin, Qmax=Qmax, dQ=dQ,
            starting_order=1, N=1
        )[(), (Efirst, Elast)].rename("SP SQE")        
        # compute MP sqe
        mpsqe = forward.sqehist(
            dos.E, dos.I, 
            T=T, M=M,
            Qmin=Qmin, Qmax=Qmax, dQ=dQ,
            starting_order=2, N=4
        )[(), (Efirst, Elast)].rename("MP SQE")
        # compute MS sqe
        from .. import ms
        mssqe = ms.sqe(mpsqe, Ei)
        mssqe.I[:] *= C_ms
        # total expected inelastic sqe computed from trial DOS
        tot_inel_sqe = singlephonon_sqe + mpsqe + mssqe
        tot_inel_sqe.I[mask] = np.nan
        # compute norm_adjustment
        def get_pos_tot_int(sqe):
            subset = sqe[(), (elastic_E_cutoff[-1],None)].copy().I
            subset[subset!=subset] = 0
            return subset.sum()
        norm_adjustment = get_pos_tot_int(tot_inel_sqe)/get_pos_tot_int(sqe)
        sqe.I *= norm_adjustment
        sqe.E2 *= norm_adjustment**2
        # compute SQE correction
        sqe_correction = mpsqe + mssqe
        # sqe_correction = sqe_correction[(), (Efirst, Elast)]
        # compute corrected SQE
        corrected_sqe = sqe + sqe_correction * (-1., 0)
        # compute residual
        residual_sqe = corrected_sqe + singlephonon_sqe * (-1., 0)
        # compute all-phonon sqe and ms sqe
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
    # add 
    final_dos = dos.copy()
    final_dos_subset = final_dos[(residual_pos_se.E[0], residual_pos_se.E[-1])]
    final_dos_subset.E2 += (final_dos_subset.I * rel_err_from_residual)**2
    hh.dump(final_dos, os.path.join(workdir, "final-dos.h5"))
    #
    create_script(
        os.path.join(workdir, 'plot_dos_iteration.py'),
        plot_dos_iteration_code % dict(total_rounds=total_rounds)
    )
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
    from .. import forward
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


plots_table = """
exp exp-sqe.h5
sim-singlephonon sp-sqe.h5
sim-multiphonon mp-sqe.h5
sim-multiple-scattering ms-sqe.h5
sim-correction sqe_correction.h5
exp-corrected-single-phonon corrected_sqe.h5
sim-total-inel total-inel-sqe.h5
exp-residual residual-sqe.h5
"""

# script templates
plot_intermediate_result_sqe_code = """#!/usr/bin/env python

import os
curdir = os.path.dirname(__file__)
import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

Imax = np.nanmax(hh.load(os.path.join(curdir, "exp-sqe.h5")).I)
zmin = 0 # -Imax/100
zmax = Imax/30

for index, (title, fn) in enumerate(plots):
    plt.subplot(3, 3, index+1)
    sqe = hh.load(os.path.join(curdir, fn))
    Q = sqe.Q
    E = sqe.E
    Y, X = np.meshgrid(E, Q)
    Z = sqe.I
    Zm = np.ma.masked_where(np.isnan(Z), Z)
    if title=='exp-residual':  zmin,zmax = np.array([-1.,1])/2. * zmax
    plt.pcolormesh(X, Y, Zm, vmin=zmin, vmax=zmax, cmap='hot')
    plt.colorbar()
    plt.title(title)
    continue

plt.tight_layout()
plt.show()
""" % plots_table

plot_intermediate_result_se_code = """#!/usr/bin/env python

import os
curdir = os.path.dirname(__file__)

import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

for index, (title, fn) in enumerate(plots):
    sqe = hh.load(os.path.join(curdir, fn))
    Q = sqe.Q
    E = sqe.E
    I = sqe.I
    I[I!=I] = 0
    E2 = sqe.E2
    E2[E2!=E2] = 0
    se = sqe.sum('Q')
    if title.startswith('sim'):
        plt.plot(E, se.I, '-', label=title)
    else:
        plt.errorbar(E, se.I, se.E2**.5, ls='none', elinewidth=2, label=title)

    # set a reasonable y range
    if title == 'exp':
        max_inel_I = se[(E[-1]*0.1,None)].I.max()
    continue

plt.ylim(-max_inel_I/10., max_inel_I*1.1)
plt.legend()
plt.show()
""" % plots_table

plot_dos_iteration_code = """#!/usr/bin/env python

import histogram.hdf as hh, os
curdir = os.path.dirname(__file__)

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 6,4.5

for round_no in range(%(total_rounds)d): 
    fn = os.path.join(curdir, 'round-' + str(round_no), 'dos.h5')
    dos = hh.load(fn)
    plt.errorbar(dos.E, dos.I, dos.E2**.5, label=str(round_no))
    continue

plt.legend()
plt.show()
"""


# End of file 
