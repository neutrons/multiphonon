#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os


def sqe2dos(
        sqe, T, Ecutoff, elastic_E_cutoff, M, C_ms=None, Ei=None,
        workdir = 'work', 
        MAX_ITERATION = 7
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
        # compute MP sqe
        from .. import forward
        Q,E,S = forward.sqe(
            dos.E, dos.I, 
            Qmin=Qmin, Qmax=Qmax, dQ=dQ,
            starting_order=2, N=4
        )
        Qaxis = H.axis('Q', Q, '1./angstrom')
        Eaxis = H.axis('E', E, 'meV')
        mpsqe = H.histogram("MP SQE", [Qaxis, Eaxis], S)[(), (Efirst, Elast)]
        # compute MS sqe
        from .. import ms
        mssqe = ms.sqe(mpsqe, Ei)
        mssqe.I[:] *= C_ms
        # compute SQE correction
        sqe_correction = mpsqe + mssqe
        # sqe_correction = sqe_correction[(), (Efirst, Elast)]
        # compute corrected SQE
        corrected_sqe = sqe + sqe_correction * (-1., 0)
        # compute one phonon SQE as well
        Q1,E1,S1 = forward.sqe(
            dos.E, dos.I,
            Qmin=Qmin, Qmax=Qmax, dQ=dQ,
            starting_order=1, N=1
        )
        Q1axis = H.axis('Q', Q1, '1./angstrom')
        E1axis = H.axis('E', E1, 'meV')
        singlephonon_sqe = H.histogram("SP SQE", [Q1axis, E1axis], S1)\
                           [(), (Efirst, Elast)]
        # compute residual
        residual_sqe = corrected_sqe + singlephonon_sqe * (-1., 0)
        # compute all-phonon sqe and ms sqe
        phonon_ms_sqe = singlephonon_sqe + mpsqe + mssqe
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
        savesqe(phonon_ms_sqe, 'phonon+ms-sqe.h5')
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
        continue
    create_script(
        os.path.join(workdir, 'plot_dos.py'),
        plot_dos_code % dict(total_rounds=MAX_ITERATION)
    )
    return


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
    sq = sqe.sum('E')
    # sq.I should be normalized to 1 for each Q
    # but since we are not measuring the fulling dynamical
    # range due to limitation of instrument and Ei
    # that normalization holds true only at a small
    # region at low Q, but not too low. 
    # so we take a front portion of the Q axis
    # and ignore the very low Q where the dynamical range
    # is cut off (those are marked by nans)
    # the 1/3 factor below is kind of arbitrary
    average_sq = np.nanmean(sq[(None, sq.Q[-1]/3.)].I)
    norm = 1./average_sq
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
singlephonon sp-sqe.h5
multiphonon mp-sqe.h5
multiple-scattering ms-sqe.h5
correction sqe_correction.h5
corrected-single-phonon corrected_sqe.h5
phonon+ms phonon+ms-sqe.h5
residual residual-sqe.h5
"""

# script templates
plot_intermediate_result_sqe_code = """#!/usr/bin/env python

import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

Imax = np.nanmax(hh.load("exp-sqe.h5").I)
zmin = 0 # -Imax/100
zmax = Imax/30

for index, (title, fn) in enumerate(plots):
    plt.subplot(3, 3, index+1)
    sqe = hh.load(fn)
    Q = sqe.Q
    E = sqe.E
    Y, X = np.meshgrid(E, Q)
    Z = sqe.I
    Zm = np.ma.masked_where(np.isnan(Z), Z)
    if title=='residual':  zmin,zmax = np.array([-1.,1])/2. * zmax
    plt.pcolormesh(X, Y, Zm, vmin=zmin, vmax=zmax, cmap='hot')
    plt.colorbar()
    plt.title(title)
    continue

plt.tight_layout()
plt.show()
""" % plots_table

plot_intermediate_result_se_code = """#!/usr/bin/env python

import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

for index, (title, fn) in enumerate(plots):
    sqe = hh.load(fn)
    Q = sqe.Q
    E = sqe.E
    I = sqe.I
    I[I!=I] = 0
    se = sqe.sum('Q')
    plt.plot(E, se.I, label=title)
    continue

plt.legend()
plt.show()
""" % plots_table

plot_dos_code = """#!/usr/bin/env python

import histogram.hdf as hh, os

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 6,4.5

for round_no in range(%(total_rounds)d): 
    fn = os.path.join('round-' + str(round_no), 'dos.h5')
    dos = hh.load(fn)
    plt.plot(dos.E, dos.I, label=str(round_no))
    continue

plt.legend()
plt.show()
"""


# End of file 
