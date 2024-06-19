import os
import sys

import histogram.hdf as hh
import numpy as np

# hide the warnings on divide by zero etc
np.seterr(divide="ignore", invalid="ignore")


def getDOS(
    sample_nxs,
    mt_nxs=None,
    mt_fraction=0.9,
    const_bg_fraction=0.0,
    Emin=-100,
    Emax=100,
    dE=1.0,
    Qmin=0,
    Qmax=15.0,
    dQ=0.1,
    T=300,
    Ecutoff=50.0,
    elastic_E_cutoff=(-20.0, 7),
    M=50.94,
    C_ms=0.3,
    Ei=116.446,
    initdos=None,
    update_strategy_weights=None,
    workdir="work",
    iqe_h5="iqe.h5",
    maxiter=10,
):
    """Compute DOS from direct-geometry powder neutron scattering spectrum
    by performing multiphonon and multiple-scattering corrections.
    Inorder to monitor messages, this function returns an iterator.
    Please call it with an evaluation of an iteration.
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

    iqe_h5 : str
        A name of the file to hold the reduced data.  If this file already
        exits, in the work directory, with the correct parameters the it is
        loaded rather than re reduced.

    maxiter: int
        Max iteration

    """
    for msg in reduce2iqe(sample_nxs, Emin, Emax, dE, Qmin, Qmax, dQ, mt_nxs, iqe_h5, workdir):
        yield msg
    iqe_h5, mtiqe_h5, Qaxis, Eaxis = msg
    iqehist = hh.load(iqe_h5)
    if const_bg_fraction:
        ave = np.nanmean(iqehist.I)
        iqehist.I -= ave * const_bg_fraction
    if mt_nxs is not None:
        iqehist -= hh.load(mtiqe_h5) * (mt_fraction, 0)
        I = iqehist.I
        if (I < 0).sum() > I.size * 0.005:
            import warnings

            warnings.warn(
                "After MT subtraction, some intensities are negative. Please check your MT data and mt_fraction value"
            )
    # to DOS
    # interpolate data
    from .sqe import interp

    # probably don't need this line
    newiqe = interp(iqehist, newE=np.arange(*Eaxis))
    # save interpolated data
    hh.dump(newiqe, "iqe-interped.h5")
    # init dos
    if initdos:
        initdos = hh.load(initdos)
    # create processing engine
    from .backward import sqe2dos

    iterdos = sqe2dos.sqe2dos(
        newiqe,
        T=T,
        Ecutoff=Ecutoff,
        elastic_E_cutoff=elastic_E_cutoff,
        M=M,
        C_ms=C_ms,
        Ei=Ei,
        initdos=initdos,
        update_strategy_weights=update_strategy_weights,
        workdir=workdir,
        MAX_ITERATION=maxiter,
    )
    doslist = []
    yield "Iterative computation of DOS..."
    for i, dos in enumerate(iterdos):
        yield "Finished round #%s" % (i + 1,)
        continue
    yield "Done"
    return


def reduce2iqe(
    sample_nxs,
    Emin,
    Emax,
    dE,
    Qmin,
    Qmax,
    dQ,
    mt_nxs=None,
    iqe_h5="iqe.h5",
    workdir="work",
):
    """Reduce sample and (optionally) empty can nxs files and generate I(Q,E)
    histograms.

    Inorder to monitor messages, this function returns an iterator.
    Please call it using this form:

        >>> for msg in reduce2iqe(...): print msg

    Parameters
    ----------
    sample_nxs : str
        Sample Nexus file

    Emin : float
        Energy tranfer axis minimum

    Emax : float
        Energy tranfer axis maximum

    dE : float
        Energy tranfer axis step size

    Qmin : float
        Momentum tranfer axis minimum

    Qmax : float
        Momentum tranfer axis maximum

    dQ : float
        Momentum tranfer axis step size

    mt_nxs : str
        Empty can Nexus file

    iqe_h5: str
        output histogram filename of reduced I(Q,E)

    workdir: str
        path to working directory

    """
    # prepare paths
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    if not os.path.isabs(iqe_h5):
        iqe_h5 = os.path.abspath(os.path.join(workdir, iqe_h5))
    # reduce
    Eaxis = _normalize_axis_setting(Emin, Emax, dE)
    Eaxis = _checkEaxis(*Eaxis)
    Qaxis = _normalize_axis_setting(Qmin, Qmax, dQ)
    yield "Converting sample data to powder I(Q,E)..."
    raw2iqe(sample_nxs, iqe_h5, Eaxis, Qaxis, type="sample")
    if mt_nxs is not None:
        _tomtpath = lambda p: os.path.join(os.path.dirname(p), "mt-" + os.path.basename(p))
        mtiqe_h5 = _tomtpath(iqe_h5)
        yield "Converting MT data to powder I(Q,E)..."
        raw2iqe(mt_nxs, mtiqe_h5, Eaxis, Qaxis, type="MT")
    else:
        mtiqe_h5 = None
    yield "Results: sample IQE, MT IQE, Qaxis, Eaxis"
    yield iqe_h5, mtiqe_h5, Qaxis, Eaxis


def _checkEaxis(Emin, Emax, dE):
    saved = Emin, Emax, dE
    centers = np.arange(Emin, Emax, dE)
    if np.isclose(centers, 0.0).any():
        return saved
    import warnings

    Emin = int(Emin / dE) * dE
    Emax = int(Emax / dE) * dE
    new = Emin, Emax, dE
    warnings.warn(
        "Zero has to be one of the ticks in the energy axis.\n" "Energy axis modified from %s to %s \n" % (saved, new)
    )
    return new


def _normalize_axis_setting(min, max, delta):
    # try to deal with numerical error
    nsteps = round(1.0 * (max - min) / delta)
    if abs(max - (min + nsteps * delta)) < 1e-5:
        max = max + delta / 1.0e4
    return min, max, delta


def _md5(s):
    import hashlib

    return hashlib.md5(s).hexdigest()


def raw2iqe(eventnxs, iqe_h5, Eaxis, Qaxis, type):
    """Read and reduce a raw nxs file.  If the reduced file already exists it
    will read the existing file rather than recreate it.

    Parameters
    ----------
    eventnxs : str
    The raw data file

    iqe_h5 : str
    The filename to create from the raw
    If this file already exits with the correct parameters,  it is simply read.

    Eaxis : tpl
    A tuple containing  Emin, Emax, Edelta

    Qaxis : tpl
    A tuple containing  Qmin, Qmax, Qdelta

    type : str

    """
    # if iqe_h5 exists and the parameters do not match,
    # we need to remove the old result
    parameters_fn = os.path.join(os.path.dirname(iqe_h5), "raw2iqe-%s.params" % type)
    parameters_text = "nxs=%s\nEaxis=%s\nQxis=%s\n" % (eventnxs, Eaxis, Qaxis)
    remove_cache = False
    if os.path.exists(iqe_h5):
        if os.path.exists(parameters_fn):
            with open(parameters_fn) as stream:
                saved = stream.read()
            if saved != parameters_text:
                remove_cache = True
        else:
            remove_cache = True
    if remove_cache:
        os.remove(iqe_h5)
    #
    from .redutils import reduce

    Emin, Emax, dE = Eaxis
    Emin -= dE / 2
    Emax -= dE / 2  # mantid algo use bin boundaries
    Qmin, Qmax, dQ = Qaxis
    Qmin -= dQ / 2
    Qmax -= dQ / 2
    # reduce
    if not os.path.exists(iqe_h5):
        qaxis = Qmin, dQ, Qmax
        eaxis = Emin, dE, Emax
        if sys.version_info < (3, 0) and isinstance(eventnxs, unicode):
            eventnxs = eventnxs.encode()
        if sys.version_info < (3, 0) and isinstance(iqe_h5, unicode):
            iqe_h5 = iqe_h5.encode()
        reduce(eventnxs, qaxis, iqe_h5, eaxis=eaxis, tof2E="guess", ibnorm="ByCurrent")
    else:
        import warnings

        msg = "Reusing old reduction result from %s" % iqe_h5
        warnings.warn(msg)
    # fix energy axis if necessary
    _fixEaxis(iqe_h5, Eaxis)
    # save parameters
    with open(parameters_fn, "wt") as stream:
        stream.write(parameters_text)
    return


def _fixEaxis(iqe_h5_path, Eaxis):
    """When iqe is obtained from a nxs or nxspe file where
    tof axis is already converted to E, the reduced data may
    not have the Eaxis as desired. this method fixes it by
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

    shutil.copyfile(iqe_h5_path, iqe_h5_path + ".bkup-wrongEaxis")
    from .sqe import interp

    h1 = interp(h, centers1)
    hh.dump(h1, iqe_h5_path)
    return
