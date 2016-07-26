def getDOS(eventnxs, Emin=-100, Emax=100, dE=1.,
           Qmin=0, Qmax=15., dQ=0.1, T=300, Ecutoff=50., 
           elastic_E_cutoff=(-20., 7), M=50.94,
           C_ms=0.3, Ei=116.446, workdir='work'):
    import os
    import histogram.hdf as hh, numpy as np
    # reduce
    print("reducing...")
    cmd = "mcvine instruments arcs nxs reduce %(eventnxs)s --out=iqe.nxs"
    cmd += " --eaxis %(Emin)s %(Emax)s %(dE)s --qaxis %(Qmin)s %(Qmax)s %(dQ)s"
    cmd = cmd % locals()
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)
    # to histogram
    print("to histogram...")
    cmd = "mcvine mantid extract_iqe iqe.nxs iqe.h5"
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)
    # to DOS
    iqehist = hh.load("iqe.h5")
    # interpolate data
    from .sqe import interp
    # probably don't need this line
    newiqe = interp(iqehist, newE = np.arange(Emin, Emax, dE))
    # save interpolated data
    hh.dump(newiqe, 'iqe-interped.h5')
    # create processing engine
    from .backward import sqe2dos
    print("iterative computation of DOS...")
    iterdos = sqe2dos.sqe2dos(
      newiqe, T=T, Ecutoff=Ecutoff, 
      elastic_E_cutoff=elastic_E_cutoff, M=M,
      C_ms=C_ms, Ei=Ei, workdir='work')
    doslist = list(iterdos)
    print("done.")
    return doslist


def notebookUI(eventnxs):
    import ipywidgets as widgets
    from IPython.display import display
    w_Emin = widgets.BoundedFloatText(description="Emin", min=-1000., max=0., value=-70)
    w_Emax = widgets.BoundedFloatText(description="Emax", min=0., max=1000., value=70)
    w_dE = widgets.BoundedFloatText(description="dE", min=0.01, max=50., value=1.)
    w_Qmin = widgets.BoundedFloatText(description="Qmin", min=0, max=5., value=0)
    w_Qmax = widgets.BoundedFloatText(description="Qmax", min=5., max=50., value=14.)
    w_dQ = widgets.BoundedFloatText(description="dQ", min=0.01, max=5., value=0.1)
    w_T = widgets.BoundedFloatText(description="Temperature", min=0.001, max=5000., value=300.)
    w_Ecutoff = widgets.BoundedFloatText(description="Max energy of phonons", min=5, max=1000., value=50)
    w_ElasticPeakMin = widgets.BoundedFloatText(description="Emin of elastic peak", min=-300., max=-1., value=-20.)
    w_ElasticPeakMax = widgets.BoundedFloatText(description="Emax of elastic peak", min=0.2, max=300., value=7.)
    w_mass = widgets.BoundedFloatText(description="Average atom mass", min=1., max=300., value=50.94)
    w_C_ms = widgets.BoundedFloatText(description="C_ms", min=0., max=10., value=0.3)
    w_Ei = widgets.BoundedFloatText(description="Ei", min=1, max=2000., value=116.446)

    w_inputs = (
        w_Emin, w_Emax, w_dE,
        w_Qmin, w_Qmax, w_dQ,
        w_T, w_Ecutoff,
        w_ElasticPeakMin, w_ElasticPeakMax,
        w_mass, w_C_ms, w_Ei
    )

    w_Run = widgets.Button(description="Run")
    def submit(b):
        getDOS(
            eventnxs, 
            Emin=w_Emin.value, Emax=w_Emax.value, dE=w_dE.value,
            Qmin=w_Qmin.value, Qmax=w_Qmax.value, dQ=w_dQ.value,
            T=w_T.value, Ecutoff=w_Ecutoff.value, 
            elastic_E_cutoff=(w_ElasticPeakMin.value, w_ElasticPeakMax.value),
            M=w_mass.value,
            C_ms=w_C_ms.value, Ei=w_Ei.value,
            workdir='work')
        return
    w_Run.on_click( submit )
    w_all = w_inputs + (w_Run,)
    display(*w_all)
    return
