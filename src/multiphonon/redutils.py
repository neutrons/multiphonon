import sys

mantid_checked = False


def _checkMantid():
    print("* Checking Mantid ...")
    import shlex
    import subprocess as sp

    sp.call(
        shlex.split("python -c 'import matplotlib, mantid'"),
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )  # sometimes mantid import for the first time may fail
    if sp.call(shlex.split("python -c 'import matplotlib, mantid'")):
        raise RuntimeError("Please install mantid")
    global mantid_checked
    mantid_checked = True
    print("  - Done.")
    return


if not mantid_checked:
    _checkMantid()


def reduce(
    nxsfile,
    qaxis,
    outfile,
    use_ei_guess=False,
    ei_guess=None,
    eaxis=None,
    tof2E=True,
    ibnorm="ByCurrent",
):
    """Reduce a NeXus file to a I(Q,E) histogram using Mantid

    This is a wrapper of Mantid algorithms to reduce a NeXus file to IQE histogram.

    Parameters
    ----------
    nxsfile: str
        path to nxs file

    qaxis: 3-tuple of floats
        Momentum transfer axis. (Qmin, dQ, Qmax). unit: inverse angstrom

    outfile: str
        path to save nxs data

    use_ei_guess: boolean
        Use incident energy guess

    ei_guess: float
        Initial guess of incident energy (meV)

    eaxis: 3-tuple of floats
        Energy transfer axis. (Emin, dE, Emax). unit: meV

    tof2E: boolean
        Conversion from time of flight axis to energy axis or not.
        If the NeXus file is in time of flight, tof2E=True
        If the NeXus file is processed and in energy transfer, tof2E=False

    ibnorm: str
        Incident beam normalization choice. Allowed values: None, ByCurrent, ToMonitor
        For more details, see http://docs.mantidproject.org/nightly/algorithms/DgsReduction-v1.html

    """
    import mantid.simpleapi as msa
    from mantid import mtd
    from mantid.simpleapi import DgsReduction, Load

    msa.config.setFacility("SNS")
    if tof2E == "guess":
        # XXX: this is a simple guess. all raw data files seem to have root "entry"
        cmd = "h5ls %s" % nxsfile
        import shlex
        import subprocess as sp

        o = sp.check_output(shlex.split(cmd)).strip().split()[0]
        if sys.version_info >= (3, 0) and isinstance(o, bytes):
            o = o.decode()
        tof2E = o == "entry"
    if tof2E:
        if use_ei_guess:
            DgsReduction(
                SampleInputFile=nxsfile,
                IncidentEnergyGuess=ei_guess,
                UseIncidentEnergyGuess=use_ei_guess,
                OutputWorkspace="reduced",
                EnergyTransferRange=eaxis,
                IncidentBeamNormalisation=ibnorm,
            )
        else:
            DgsReduction(
                SampleInputFile=nxsfile,
                OutputWorkspace="reduced",
                EnergyTransferRange=eaxis,
                IncidentBeamNormalisation=ibnorm,
            )
        reduced = mtd["reduced"]
    else:
        reduced = Load(nxsfile)
    # get eaxis info from mtd workspace, if necessary
    if eaxis is None:
        Edim = reduced.getXDimension()
        emin = Edim.getMinimum()
        emax = Edim.getMaximum()
        de = Edim.getX(1) - Edim.getX(0)
        eaxis = emin, de, emax
    qmin, dq, qmax = qaxis
    nq = int((qmax - qmin + dq / 2.0) / dq)
    emin, de, emax = eaxis
    ne = int((emax - emin + de / 2.0) / de)
    #
    md = msa.ConvertToMD(
        InputWorkspace=reduced,
        QDimensions="|Q|",
        dEAnalysisMode="Direct",
        MinValues="%s,%s" % (qmin, emin),
        MaxValues="%s,%s" % (qmax, emax),
    )
    binned = msa.BinMD(
        InputWorkspace=md,
        AxisAligned=1,
        AlignedDim0="|Q|,%s,%s,%s" % (qmin, qmax, nq),
        AlignedDim1="DeltaE,%s,%s,%s" % (emin, emax, ne),
    )
    # create histogram
    import histogram as H
    import histogram.hdf as hh

    data = binned.getSignalArray().copy()
    err2 = binned.getErrorSquaredArray().copy()
    nev = binned.getNumEventsArray()
    data /= nev
    err2 /= nev * nev
    import numpy as np

    qaxis = H.axis("Q", boundaries=np.arange(qmin, qmax + dq / 2.0, dq), unit="1./angstrom")
    eaxis = H.axis("E", boundaries=np.arange(emin, emax + de / 2.0, de), unit="meV")
    hist = H.histogram("IQE", (qaxis, eaxis), data=data, errors=err2)
    if outfile.endswith(".nxs"):
        import warnings

        warnings.warn("reduce function no longer writes iqe.nxs nexus file. it only writes iqe.h5 histogram file")
        outfile = outfile[:-4] + ".h5"
    hh.dump(hist, outfile)
    return hist
