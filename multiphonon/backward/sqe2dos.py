#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import numpy as np, histogram as H, histogram.hdf as hh, os


def sqe2dos(
        sqe, T, Ecutoff, elastic_E_cutoff, M, C_ms=None, Ei=None,
        workdir = 'work',
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

    corrected_sqe = sqe
    for roundno in range(5):
        # compute dos
        dos = onephonon(corrected_sqe, T, Ecutoff, elastic_E_cutoff, M)
        yield dos
        # should compare to previous round and break 
        # if change is little
        # ...
        # normalize exp SQE
        from ..forward import kelvin2mev
        beta = 1./(T*kelvin2mev)
        sqe = normalizeExpSQE(sqe, dos, M, beta, elastic_E_cutoff)
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
        # compute SQE correction
        sqe_correction = mpsqe + mssqe * (C_ms,0)
        # sqe_correction = sqe_correction[(), (Efirst, Elast)]
        # compute corrected SQE
        corrected_sqe = sqe + sqe_correction * (-1., 0)
        # save intermediate results
        cwd = os.path.join(workdir, "round-%d" % roundno)
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        hh.dump(sqe, os.path.join(cwd, 'exp-sqe.h5'))
        hh.dump(mpsqe, os.path.join(cwd, 'mp-sqe.h5'))
        hh.dump(mssqe, os.path.join(cwd, 'ms-sqe.h5'))
        hh.dump(sqe_correction, os.path.join(cwd, 'sqe_correction.h5'))
        hh.dump(corrected_sqe, os.path.join(cwd, 'corrected_sqe.h5'))
        plot_script = os.path.join(cwd, "plot.py")
        open(plot_script, 'wt').write(plot_intermediate_result_code)
        import stat
        st = os.stat(plot_script)
        os.chmod(plot_script, st.st_mode | stat.S_IEXEC)
        continue
    return


def normalizeExpSQE(sqe, dos, M, beta, elastic_E_cutoff):
    # integration of S(E) should be 1-exp(-2W) for every Q
    from .. import forward
    Q = sqe.Q
    E = dos.E; g = dos.I; dE = E[1] - E[0]
    DW2 = forward.DWExp(Q, M, E,g, beta, dE)
    DW = np.exp(-DW2)
    integration = 1 - DW
    sqe2 = sqe.copy()
    sqe2 = sqe2[(), (elastic_E_cutoff, None)]
    I = sqe2.I
    I[I!=I] = 0
    ps = I.sum(1) * dE
    norm_factors = integration/ps
    norm = np.median(norm_factors)
    sqe.I *= norm
    sqe.E2 *= norm*norm
    return sqe
    

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


plot_intermediate_result_code = """#!/usr/bin/env python

import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = \"\"\"
exp exp-sqe.h5
multiphonon mp-sqe.h5
multiple-scattering ms-sqe.h5
correction sqe_correction.h5
corrected corrected_sqe.h5
\"\"\"
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

Imax = np.nanmax(hh.load("exp-sqe.h5").I)
zmin = -Imax/100
zmax = Imax/30

for index, (title, fn) in enumerate(plots):
    plt.subplot(3, 2, index+1)
    sqe = hh.load(fn)
    Q = sqe.Q
    E = sqe.E
    Y, X = np.meshgrid(E, Q)
    Z = sqe.I
    plt.pcolormesh(X, Y, Z, vmin=zmin, vmax=zmax)
    plt.colorbar()
    plt.title(title)
    continue

plt.tight_layout()
plt.show()
"""


# End of file 
