
import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
import histogram.hdf as hh, os


def plot_dos_iteration(curdir, total_rounds=None):
    """
    plot the  DOS for each iteration
   
    Parameters
    ----------
    curdir : str
        path to the root of the working directory for SQE->DOS calculation
 
    total_rounds : integer
        number of iterations

    """
    if total_rounds is None:
        import glob
        dirs = glob.glob(os.path.join(curdir, 'round-*'))
        _get_round_no = lambda p: int(os.path.basename(p).lstrip('round-'))
        total_rounds = max(map(_get_round_no, dirs)) + 1
    # mpl.rcParams['figure.figsize'] = 6,4.5
    for round_no in range(total_rounds):
        fn = os.path.join(curdir, 'round-' + str(round_no), 'dos.h5')
        dos = hh.load(fn)
        plt.errorbar(dos.E, dos.I, dos.E2**.5, label=str(round_no))
        continue
    plt.legend()
    return


def plot_residual(curdir):
    """plot the  residual DOS
   
    Parameters
    ----------
    curdir : str
        path to the root of the working directory for SQE->DOS calculation

    """

    exp_pos_se = hh.load(os.path.join(curdir, 'I_E-exp-posE.h5'))
    residual_pos_se = hh.load(os.path.join(curdir, 'residual_E-posE.h5'))
    E = exp_pos_se.E
    plt.errorbar(E, exp_pos_se.I, exp_pos_se.E2**.5, label='exp S(E)')
    plt.errorbar(E, residual_pos_se.I, residual_pos_se.E2**.5, label='residual')
    plt.plot([E[0], E[-1]], [0,0], 'k', label='baseline')
    plt.legend()
    return


def plot_intermediate_result_sqe(curdir):
    """plot the  intermediate S(Q,E)

    Parameters
    ----------

    curdir: str
        path to one of the iteration working directory for SQE->DOS calculation,
        for example, work/round-5

    """

    from ._sqe2dos_script_templates import plots_table as plots
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
    return


def plot_intermediate_result_se(curdir):
    """plot the  intermediate S(E)
   
    Parameters
    ----------

    curdir: str
        path to one of the iteration working directory for SQE->DOS calculation,
        for example, work/round-5

    """

    # mpl.rcParams['figure.figsize'] = 12,9
    from ._sqe2dos_script_templates import plots_table as plots
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
    return
    
