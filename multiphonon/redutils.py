def _createDefaultMantidUserConfig(facility='SNS'):
    # create default Mantid user configuration for DEMO purpose.
    import os
    mantid_config_path = os.path.expanduser('~/.mantid/Mantid.user.properties')
    mantid_user_dir = os.path.dirname(mantid_config_path)
    if not os.path.exists(mantid_config_path):
        if not os.path.exists(mantid_user_dir):
            os.makedirs(mantid_user_dir)
        with open(mantid_config_path, 'wt') as of:
            of.write('default.facility=%s' % facility)
    return
# this should be done before mantid is imported
_createDefaultMantidUserConfig()


mantid_checked = False
def _checkMantid():
    print "* Checking Mantid ..."
    import subprocess as sp, shlex
    sp.call(shlex.split("python -c 'import mantid'"), stdout=sp.PIPE, stderr=sp.PIPE) # sometimes mantid import for the first time may fail
    if sp.call(shlex.split("python -c 'import mantid'")):
        raise RuntimeError("Please install mantid")
    global mantid_checked
    mantid_checked = True
    print "  - Done."
    return
if not mantid_checked:
    _checkMantid()


def reduce(nxsfile, qaxis, outfile, use_ei_guess=False, ei_guess=None, eaxis=None, tof2E=True, ibnorm='ByCurrent'):
    """reduce a NeXus file to a I(Q,E) histogram using Mantid

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
    from mantid.simpleapi import DgsReduction, SofQW3, SaveNexus, Load
    if tof2E == 'guess':
        # XXX: this is a simple guess. all raw data files seem to have root "entry"
        cmd = 'h5ls %s' % nxsfile
        import subprocess as sp, shlex
        o = sp.check_output(shlex.split(cmd)).strip().split()[0]
        tof2E = o == 'entry'
    if tof2E:
        if use_ei_guess:
            DgsReduction(
                SampleInputFile=nxsfile,
                IncidentEnergyGuess=ei_guess,
                UseIncidentEnergyGuess=use_ei_guess,
                OutputWorkspace='reduced',
                EnergyTransferRange=eaxis,
                IncidentBeamNormalisation=ibnorm,
                )
        else:
            DgsReduction(
                SampleInputFile=nxsfile,
                OutputWorkspace='reduced',
                EnergyTransferRange=eaxis,
                IncidentBeamNormalisation=ibnorm,
                )
    else: 
        reduced = Load(nxsfile)
    SofQW3(
        InputWorkspace='reduced',
        OutputWorkspace='iqw',
        QAxisBinning=qaxis,
        EMode='Direct',
        )
    SaveNexus(
        InputWorkspace='iqw',
        Filename = outfile,
        Title = 'iqw',
        )
    return


def extract_iqe(mantid_nxs, histogram):
    "extract iqe from a mantid-saved h5 file and save to a histogram"
    import h5py, numpy as np
    inpath, outpath = mantid_nxs, histogram
    f = h5py.File(inpath)
    w = f['mantid_workspace_1']['workspace']
    e = np.array(w['axis1'])
    de = e[1] - e[0]
    ee = (e+de/2.)[:-1]
    q = np.array(w['axis2'])
    dq = q[1] - q[0]
    qq = (q+dq/2.)[:-1]
    I = np.array(np.array(w['values']))
    # I[I!=I] = 0
    E2 = np.array(np.array(w['errors'])**2)
    import histogram as H
    iqe = H.histogram('iqe', [('Q',qq,  'angstrom**-1'), ('energy', ee, 'meV')], data=I, errors = E2)
    import histogram.hdf as hh
    hh.dump(iqe, outpath)
    return


