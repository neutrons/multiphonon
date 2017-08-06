import histogram.hdf as hh, numpy as np
import os

# hide the warnings on divide by zero etc
np.seterr(divide='ignore', invalid='ignore')


def getDOS(sample_nxs, mt_nxs=None, mt_fraction=0.9, const_bg_fraction=0.,
           Emin=-100, Emax=100, dE=1.,
           Qmin=0, Qmax=15., dQ=0.1, T=300, Ecutoff=50., 
           elastic_E_cutoff=(-20., 7), M=50.94,
           C_ms=0.3, Ei=116.446, initdos=None, workdir='work',
           iqe_nxs="iqe.nxs", iqe_h5="iqe.h5", maxiter=10):
    """compute DOS from powder spectrum by performing multiphonon and 
    multiple-scattering corrections.
    This is an iterator. so call it with an evaluation of the iteration.
    For example:

      >>> output = list(getDOS(...))
    """
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
    yield "Convert sample data to powder I(Q,E)"
    raw2iqe(sample_nxs, iqe_nxs, iqe_h5, Eaxis, Qaxis)
    iqehist = hh.load(iqe_h5)
    if const_bg_fraction:
        ave = np.nanmean(iqehist.I)
        iqehist.I -= ave*const_bg_fraction
    if mt_nxs is not None:
        _tomtpath = lambda p: os.path.join(
            os.path.dirname(p), 'mt-'+os.path.basename(p))
        mtiqe_nxs = _tomtpath(iqe_nxs)
        mtiqe_h5 = _tomtpath(iqe_h5)
        yield "Convert MT data to powder I(Q,E)"
        raw2iqe(mt_nxs, mtiqe_nxs, mtiqe_h5, Eaxis, Qaxis)
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
        C_ms=C_ms, Ei=Ei, initdos=initdos, workdir='work',
        MAX_ITERATION=maxiter)
    doslist = []
    yield "Iterative computation of DOS..."
    for i,dos in enumerate(iterdos):
        yield "Finished round #%s" % (i+1,)
        continue
    yield "Done"
    return


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


def raw2iqe(eventnxs, iqe_nxs, iqe_h5, Eaxis, Qaxis):
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
    # to histogram
    if not os.path.exists(iqe_h5):
        extract_iqe(iqe_nxs, iqe_h5)
    # fix energy axis if necessary
    _fixEaxis(iqe_h5, Eaxis)
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


def notebookUI(samplenxs, mtnxs, initdos=None, options=None, load_options_path=None):
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
    w_mt_fraction = widgets.BoundedFloatText(description="mt_fraction", min=0., max=100., value=options['mt_fraction'])
    w_const_bg_fraction = widgets.BoundedFloatText(description="const_bg_fraction", min=0., max=1., value=options.get('const_bg_fraction', 0.0))
    w_Emin = widgets.BoundedFloatText(description="Emin", min=-1000., max=0., value=options['Emin'])
    w_Emax = widgets.BoundedFloatText(description="Emax", min=0., max=1000., value=options['Emax'])
    w_dE = widgets.BoundedFloatText(description="dE", min=0, max=50., value=options['dE'])
    w_Qmin = widgets.BoundedFloatText(description="Qmin", min=0, max=50., value=options['Qmin'])
    w_Qmax = widgets.BoundedFloatText(description="Qmax", min=0., max=50., value=options['Qmax'])
    w_dQ = widgets.BoundedFloatText(description="dQ", min=0, max=5., value=options['dQ'])
    w_T = widgets.BoundedFloatText(description="Temperature", min=0., max=5000., value=options['T'])
    w_Ecutoff = widgets.BoundedFloatText(description="Max energy of phonons", min=0, max=1000., value=options['Ecutoff'])
    w_ElasticPeakMin = widgets.BoundedFloatText(description="Emin of elastic peak", min=-300., max=0., value=options['ElasticPeakMin'])
    w_ElasticPeakMax = widgets.BoundedFloatText(description="Emax of elastic peak", min=0., max=300., value=options['ElasticPeakMax'])
    w_M = widgets.BoundedFloatText(description="Average atom mass", min=1., max=1000., value=options['M'])
    w_C_ms = widgets.BoundedFloatText(description="C_ms", min=0., max=10., value=options['C_ms'])
    w_Ei = widgets.BoundedFloatText(description="Ei", min=0, max=2000., value=options['Ei'])
    w_workdir = widgets.Text(description="work dir", value=options['workdir'])

    w_inputs = (
        w_mt_fraction, w_const_bg_fraction,
        w_Emin, w_Emax, w_dE,
        w_Qmin, w_Qmax, w_dQ,
        w_T, w_Ecutoff,
        w_ElasticPeakMin, w_ElasticPeakMax,
        w_M, w_C_ms, w_Ei, w_workdir
    )

    w_Run = widgets.Button(description="Run")
    w_all = w_inputs + (w_Run,)

    def submit(b):
        # suppress warning from h5py
        import warnings
        warnings.simplefilter(action = "ignore", category = FutureWarning)
        #
        kargs = dict(
            mt_fraction = w_mt_fraction.value,
            const_bg_fraction = w_const_bg_fraction.value,
            Emin=w_Emin.value, Emax=w_Emax.value, dE=w_dE.value,
            Qmin=w_Qmin.value, Qmax=w_Qmax.value, dQ=w_dQ.value,
            T=w_T.value, Ecutoff=w_Ecutoff.value, 
            elastic_E_cutoff=(w_ElasticPeakMin.value, w_ElasticPeakMax.value),
            M=w_M.value,
            C_ms=w_C_ms.value, Ei=w_Ei.value,
            workdir=w_workdir.value,
            initdos=initdos,
            )
        import pprint, os, yaml
        # pprint.pprint(samplenxs)
        # pprint.pprint(mtnxs)
        # pprint.pprint(kargs)
        workdir = kargs['workdir']
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        options = dict(kargs)
        options['ElasticPeakMin']=w_ElasticPeakMin.value
        options['ElasticPeakMax']=w_ElasticPeakMax.value
        yaml.dump(options, 
                  open(os.path.join(workdir, 'getdos-opts.yaml'), 'wt'))
        maxiter = 10
        close = lambda w: w.close()
        map(close, w_all)
        log_progress(getDOS(samplenxs, mt_nxs=mtnxs, maxiter=maxiter, **kargs), every=1, size=maxiter+2)
        return
    w_Run.on_click( submit )
    display(*w_all)
    return


# modified from https://github.com/alexanderkuk/log-progress
def log_progress(sequence, every=None, size=None):
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)     # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, msg in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = 'Running: {index} / ?: {msg}...'.format(index=index, msg=msg)
                else:
                    progress.value = index
                    label.value = u'Running: {index} / {size}: {msg}...'.format(
                        index=index,
                        size=size,
                        msg=msg
                    )
    except:
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = size
        # label.value = str(index or '?')
        label.value = 'Done.'


default_options = dict(
    mt_fraction = 0.9,
    const_bg_fraction = 0.,
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
