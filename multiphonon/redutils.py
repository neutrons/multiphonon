def reduce(nxsfile, qaxis, outfile, use_ei_guess=False, ei_guess=None, eaxis=None, tof2E=True, ibnorm='ByCurrent'):
    "reduce Nexus file to I(Q,E)"
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
