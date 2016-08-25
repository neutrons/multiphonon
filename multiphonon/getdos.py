import histogram.hdf as hh, numpy as np
import os

def getDOS(sample_nxs, mt_nxs=None, mt_fraction=0.9,
           Emin=-100, Emax=100, dE=1.,
           Qmin=0, Qmax=15., dQ=0.1, T=300, Ecutoff=50., 
           elastic_E_cutoff=(-20., 7), M=50.94,
           C_ms=0.3, Ei=116.446, workdir='work',
           iqe_nxs="iqe.nxs", iqe_h5="iqe.h5"):
    # prepare paths
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    if not os.path.isabs(iqe_nxs):
        iqe_nxs = os.path.abspath(os.path.join(workdir, iqe_nxs))
    if not os.path.isabs(iqe_h5):
        iqe_h5 = os.path.abspath(os.path.join(workdir, iqe_h5))
    # reduce
    Eaxis = Emin, Emax, dE
    Qaxis = Qmin, Qmax, dQ
    raw2iqe(sample_nxs, iqe_nxs, iqe_h5, Eaxis, Qaxis)
    iqehist = hh.load(iqe_h5)
    if mt_nxs is not None:
        _tomtpath = lambda p: os.path.join(
            os.path.dirname(p), 'mt-'+os.path.basename(p))
        mtiqe_nxs = _tomtpath(iqe_nxs)
        mtiqe_h5 = _tomtpath(iqe_h5)
        raw2iqe(mt_nxs, mtiqe_nxs, mtiqe_h5, Eaxis, Qaxis)
        iqehist -= hh.load(mtiqe_h5) * (mt_fraction, 0)
    # to DOS
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


def raw2iqe(eventnxs, iqe_nxs, iqe_h5, Eaxis, Qaxis):
    Emin, Emax, dE = Eaxis
    Qmin, Qmax, dQ = Qaxis
    # reduce
    print("reducing...")
    if not os.path.exists(iqe_nxs):
        cmd = "mcvine instruments arcs nxs reduce "
        cmd += "%(eventnxs)s --out=%(iqe_nxs)s "
        cmd += "--eaxis %(Emin)s %(Emax)s %(dE)s "
        cmd += "--qaxis %(Qmin)s %(Qmax)s %(dQ)s "
        cmd = cmd % locals()
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
    # to histogram
    print("to histogram...")
    if not os.path.exists(iqe_h5):
        cmd = "mcvine mantid extract_iqe %(iqe_nxs)s %(iqe_h5)s" % locals()
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
    return

def notebookUI(eventnxs, options=None, load_options_path=None):
    import yaml
    if options is not None and load_options_path:
        raise RuntimeError(
            "Both options and load_options_path were set: %s, %s" %(
                options, load_options_path)
        )
    if load_options_path:
        options = yaml.load(open(load_options_path))
    if options is None:
        options = default_options
    #
    import ipywidgets as widgets
    from IPython.display import display
    w_Emin = widgets.BoundedFloatText(description="Emin", min=-1000., max=0., value=options['Emin'])
    w_Emax = widgets.BoundedFloatText(description="Emax", min=0., max=1000., value=options['Emax'])
    w_dE = widgets.BoundedFloatText(description="dE", min=0.01, max=50., value=options['dE'])
    w_Qmin = widgets.BoundedFloatText(description="Qmin", min=0, max=5., value=options['Qmin'])
    w_Qmax = widgets.BoundedFloatText(description="Qmax", min=5., max=50., value=options['Qmax'])
    w_dQ = widgets.BoundedFloatText(description="dQ", min=0.01, max=5., value=options['dQ'])
    w_T = widgets.BoundedFloatText(description="Temperature", min=0.001, max=5000., value=options['T'])
    w_Ecutoff = widgets.BoundedFloatText(description="Max energy of phonons", min=5, max=1000., value=options['Ecutoff'])
    w_ElasticPeakMin = widgets.BoundedFloatText(description="Emin of elastic peak", min=-300., max=-1., value=options['ElasticPeakMin'])
    w_ElasticPeakMax = widgets.BoundedFloatText(description="Emax of elastic peak", min=0.2, max=300., value=options['ElasticPeakMax'])
    w_M = widgets.BoundedFloatText(description="Average atom mass", min=1., max=1000., value=options['M'])
    w_C_ms = widgets.BoundedFloatText(description="C_ms", min=0., max=10., value=options['C_ms'])
    w_Ei = widgets.BoundedFloatText(description="Ei", min=1, max=2000., value=options['Ei'])
    w_workdir = widgets.Text(description="work dir", value=options['workdir'])

    w_inputs = (
        w_Emin, w_Emax, w_dE,
        w_Qmin, w_Qmax, w_dQ,
        w_T, w_Ecutoff,
        w_ElasticPeakMin, w_ElasticPeakMax,
        w_M, w_C_ms, w_Ei, w_workdir
    )

    w_Run = widgets.Button(description="Run")
    def submit(b):
        kargs = dict(
            Emin=w_Emin.value, Emax=w_Emax.value, dE=w_dE.value,
            Qmin=w_Qmin.value, Qmax=w_Qmax.value, dQ=w_dQ.value,
            T=w_T.value, Ecutoff=w_Ecutoff.value, 
            elastic_E_cutoff=(w_ElasticPeakMin.value, w_ElasticPeakMax.value),
            M=w_M.value,
            C_ms=w_C_ms.value, Ei=w_Ei.value,
            workdir=w_workdir.value,
            )
        import pprint, os, yaml
        pprint.pprint(eventnxs)
        pprint.pprint(kargs)
        workdir = kargs['workdir']
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        options = dict(kargs)
        options['ElasticPeakMin']=w_ElasticPeakMin.value
        options['ElasticPeakMax']=w_ElasticPeakMax.value
        yaml.dump(options, 
                  open(os.path.join(workdir, 'getdos-opts.yaml'), 'wt'))
        getDOS(eventnxs, **kargs)
        return
    w_Run.on_click( submit )
    w_all = w_inputs + (w_Run,)
    display(*w_all)
    return


default_options = dict(
    Emin = -70,
    Emax = 70,
    dE = 1.,
    Qmin = 0.,
    Qmax = 14.,
    dQ = 0.1,
    T = 300.,
    Ecutoff = 50.,
    ElasticPeakMin = -20,
    ElasticPeakMax = 7.,
    M = 50.94,
    C_ms = 0.3,
    Ei = 100.,
    workdir = 'work',
    )
