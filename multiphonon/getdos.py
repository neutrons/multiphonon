import histogram.hdf as hh, numpy as np
import os

# hide the warnings on divide by zero etc
np.seterr(divide='ignore', invalid='ignore')


def getDOS(sample_nxs, mt_nxs=None, mt_fraction=0.9, const_bg_fraction=0.,
           Emin=-100, Emax=100, dE=1.,
           Qmin=0, Qmax=15., dQ=0.1, T=300, Ecutoff=50., 
           elastic_E_cutoff=(-20., 7), M=50.94,
           C_ms=0.3, Ei=116.446, initdos=None, update_strategy_weights=None,
           workdir='work',
           iqe_nxs="iqe.nxs", iqe_h5="iqe.h5", maxiter=10):
    """Compute DOS from direct-geometry powder neutron scattering spectrum
    by performing multiphonon and multiple-scattering corrections.
    This is an iterator. Please call it with an evaluation of the iteration.
    For example:

      >>> output = list(getDOS(...))

    Parameters
    ----------
    sample_nxs : str
        Sample Nexus file

    mt_nxs : str
        Empty can Nexus file

    mt_fraction : float
        0<=mt_fraction<=1. Amount of empty can data to be subtracted from sample data

    const_bg_fraction : float
        Constant background fraction

    Emin, Emax, dE : floats
        Energy transfer axis setting

    Qmin, Qmax, dQ : floats
        Momentum transfer axis setting

    T : float
        Temperature (Kelvin)

    Ecutoff : float
        Maximum phonon energy

    elastic_E_cutoff: 2-tuple of floats
        cutoff for elastic peak (meV)

    M : float
        Average atomic mass (u)

    C_ms: float
        MS = C_ms * MP

    Ei : float
        Incident energy (meV)

    initdos : histogram
        initial guess of DOS

    update_strategy_weights : floats
        Weights for the update strategies (force continuity, area conservation). 
        Useful only if multiple Ei.

    work : str
        Work directory

    maxiter: int
        Max iteration

    """
    for msg in reduce2iqe(sample_nxs, Emin,Emax,dE, Qmin,Qmax,dQ, mt_nxs, iqe_nxs, iqe_h5, workdir):
        yield msg
    iqe_h5, mtiqe_h5, Qaxis, Eaxis = msg
    iqehist = hh.load(iqe_h5)
    if const_bg_fraction:
        ave = np.nanmean(iqehist.I)
        iqehist.I -= ave*const_bg_fraction
    if mt_nxs is not None:
        iqehist -= hh.load(mtiqe_h5) * (mt_fraction, 0)
    # to DOS
    # interpolate data
    from .sqe import interp
    # probably don't need this line
    newiqe = interp(iqehist, newE = np.arange(*Eaxis))
    # save interpolated data
    hh.dump(newiqe, 'iqe-interped.h5')
    # init dos
    if initdos:
        initdos = hh.load(initdos)
    # create processing engine
    from .backward import sqe2dos
    iterdos = sqe2dos.sqe2dos(
        newiqe, T=T, Ecutoff=Ecutoff, 
        elastic_E_cutoff=elastic_E_cutoff, M=M,
        C_ms=C_ms, Ei=Ei,
        initdos=initdos, update_strategy_weights=update_strategy_weights,
        workdir=workdir,
        MAX_ITERATION=maxiter)
    doslist = []
    yield "Iterative computation of DOS..."
    for i,dos in enumerate(iterdos):
        yield "Finished round #%s" % (i+1,)
        continue
    yield "Done"
    return


def reduce2iqe(sample_nxs, Emin,Emax,dE, Qmin,Qmax,dQ, mt_nxs=None, iqe_nxs='iqe.nxs', iqe_h5='iqe.h5', workdir='work'):
    # prepare paths
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    if not os.path.isabs(iqe_nxs):
        iqe_nxs = os.path.abspath(os.path.join(workdir, iqe_nxs))
    if not os.path.isabs(iqe_h5):
        iqe_h5 = os.path.abspath(os.path.join(workdir, iqe_h5))
    # reduce
    Eaxis = _normalize_axis_setting(Emin, Emax, dE)
    Eaxis = _checkEaxis(*Eaxis)
    Qaxis = _normalize_axis_setting(Qmin, Qmax, dQ)
    yield "Converting sample data to powder I(Q,E)..."
    raw2iqe(sample_nxs, iqe_nxs, iqe_h5, Eaxis, Qaxis, type='sample')
    if mt_nxs is not None:
        _tomtpath = lambda p: os.path.join(
            os.path.dirname(p), 'mt-'+os.path.basename(p))
        mtiqe_nxs = _tomtpath(iqe_nxs)
        mtiqe_h5 = _tomtpath(iqe_h5)
        yield "Converting MT data to powder I(Q,E)..."
        raw2iqe(mt_nxs, mtiqe_nxs, mtiqe_h5, Eaxis, Qaxis, type='MT')
    else:
        mtiqe_h5=None
    yield "Results: sample IQE, MT IQE, Qaxis, Eaxis"
    yield iqe_h5, mtiqe_h5, Qaxis, Eaxis


def _checkEaxis(Emin, Emax, dE):
    saved = Emin, Emax, dE
    centers = np.arange(Emin, Emax, dE)
    if np.isclose(centers, 0.).any():
        return saved
    import warnings
    Emin = int(Emin/dE) * dE
    Emax = int(Emax/dE) * dE
    new = Emin, Emax, dE
    warnings.warn(
        "Zero has to be one of the ticks in the energy axis.\n"
        "Energy axis modified from %s to %s \n" % (saved, new)
        )
    return new
    

def _normalize_axis_setting(min, max, delta):
    # try to deal with numerical error
    nsteps = round( 1.*(max-min)/delta )
    if abs(max - (min+nsteps*delta)) < 1e-5:
        max = max + delta/2.
    return min, max, delta


def _md5(s):
    import hashlib
    return hashlib.md5(s).hexdigest()


def raw2iqe(eventnxs, iqe_nxs, iqe_h5, Eaxis, Qaxis, type):
    # if iqe_nxs exists and the parameters do not match, we need to remove the old result
    parameters_fn = os.path.join(os.path.dirname(iqe_nxs), 'raw2iqe-%s.params' % type)
    parameters_text = 'nxs=%s\nEaxis=%s\nQxis=%s\n' % (eventnxs, Eaxis, Qaxis)
    remove_cache = False
    if os.path.exists(iqe_nxs):
        if os.path.exists(parameters_fn):
            saved = open(parameters_fn).read()
            if saved != parameters_text:
                remove_cache = True
        else:
            remove_cache = True
    if remove_cache:
        os.remove(iqe_nxs); os.remove(iqe_h5)
    # 
    from .redutils import reduce, extract_iqe
    Emin, Emax, dE = Eaxis
    Emin-=dE/2; Emax-=dE/2 # mantid algo use bin boundaries
    Qmin, Qmax, dQ = Qaxis
    Qmin-=dQ/2; Qmax-=dQ/2
    # reduce
    if not os.path.exists(iqe_nxs):
        qaxis = Qmin, dQ, Qmax
        eaxis = Emin, dE, Emax
        if isinstance(eventnxs, unicode):
            eventnxs = eventnxs.encode()
        if isinstance(iqe_nxs, unicode):
            iqe_nxs = iqe_nxs.encode()
        reduce(eventnxs, qaxis, iqe_nxs, eaxis=eaxis, tof2E='guess', ibnorm='ByCurrent')
    else:
        import warnings
        msg = "Reusing old reduction result from %s" % iqe_nxs
        warnings.warn(msg)
    # to histogram
    if not os.path.exists(iqe_h5):
        extract_iqe(iqe_nxs, iqe_h5)
    # fix energy axis if necessary
    _fixEaxis(iqe_h5, Eaxis)
    # save parameters
    open(parameters_fn, 'wt').write(parameters_text)
    return



def _fixEaxis(iqe_h5_path, Eaxis):
    """when iqe is obtained from a nxs or nxspe file where
    tof axis is already converted to E, the reduced data may
    not have the Eaxis as desired. this method fix it by 
    interpolation
    """
    h = hh.load(iqe_h5_path)
    eaxis = h.axes()[1]
    centers = eaxis.binCenters()
    emin, emax, de = Eaxis
    centers1 = np.arange(emin, emax, de)
    if centers.size == centers1.size and np.allclose(centers, centers1):
        return
    # save a copy of the original histogram
    import shutil
    shutil.copyfile(iqe_h5_path, iqe_h5_path+'.bkup-wrongEaxis')
    from .sqe import interp
    h1 = interp(h, centers1)
    hh.dump(h1, iqe_h5_path)
    return


from .ui.getdos0 import notebookUI
