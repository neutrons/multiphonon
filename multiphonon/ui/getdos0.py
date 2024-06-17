def notebookUI(samplenxs, mtnxs, initdos=None, options=None, load_options_path=None):
    import yaml

    if options is not None and load_options_path:
        raise RuntimeError(
            "Both options and load_options_path were set: %s, %s"
            % (options, load_options_path)
        )
    if load_options_path:
        with open(load_options_path) as stream:
            options = yaml.load(stream)
    if options is None:
        options = default_options
    #
    import ipywidgets as widgets
    from IPython.display import display

    w_mt_fraction = widgets.BoundedFloatText(
        description="mt_fraction", min=0.0, max=100.0, value=options["mt_fraction"]
    )
    w_const_bg_fraction = widgets.BoundedFloatText(
        description="const_bg_fraction",
        min=0.0,
        max=1.0,
        value=options.get("const_bg_fraction", 0.0),
    )
    w_Emin = widgets.BoundedFloatText(
        description="Emin", min=-1000.0, max=0.0, value=options["Emin"]
    )
    w_Emax = widgets.BoundedFloatText(
        description="Emax", min=0.0, max=1000.0, value=options["Emax"]
    )
    w_dE = widgets.BoundedFloatText(
        description="dE", min=0, max=50.0, value=options["dE"]
    )
    w_Qmin = widgets.BoundedFloatText(
        description="Qmin", min=0, max=50.0, value=options["Qmin"]
    )
    w_Qmax = widgets.BoundedFloatText(
        description="Qmax", min=0.0, max=50.0, value=options["Qmax"]
    )
    w_dQ = widgets.BoundedFloatText(
        description="dQ", min=0, max=5.0, value=options["dQ"]
    )
    w_T = widgets.BoundedFloatText(
        description="Temperature", min=0.0, max=5000.0, value=options["T"]
    )
    w_Ecutoff = widgets.BoundedFloatText(
        description="Max energy of phonons", min=0, max=1000.0, value=options["Ecutoff"]
    )
    w_ElasticPeakMin = widgets.BoundedFloatText(
        description="Emin of elastic peak",
        min=-300.0,
        max=0.0,
        value=options["ElasticPeakMin"],
    )
    w_ElasticPeakMax = widgets.BoundedFloatText(
        description="Emax of elastic peak",
        min=0.0,
        max=300.0,
        value=options["ElasticPeakMax"],
    )
    w_M = widgets.BoundedFloatText(
        description="Average atom mass", min=1.0, max=1000.0, value=options["M"]
    )
    w_C_ms = widgets.BoundedFloatText(
        description="C_ms", min=0.0, max=10.0, value=options["C_ms"]
    )
    w_Ei = widgets.BoundedFloatText(
        description="Ei", min=0, max=2000.0, value=options["Ei"]
    )
    w_workdir = widgets.Text(description="work dir", value=options["workdir"])

    update_strategy_weights = options.get("update_strategy_weights", (0.5, 0.5))
    w_update_weight_continuity = widgets.BoundedFloatText(
        description='"enforce continuity" weight for DOS update strategy',
        min=0.0,
        max=1.0,
        value=update_strategy_weights[0],
    )
    w_update_weight_area = widgets.BoundedFloatText(
        description='"area conservation" weight for DOS update strategy',
        min=0.0,
        max=1.0,
        value=update_strategy_weights[1],
    )

    w_inputs = (
        w_mt_fraction,
        w_const_bg_fraction,
        w_Emin,
        w_Emax,
        w_dE,
        w_Qmin,
        w_Qmax,
        w_dQ,
        w_T,
        w_Ecutoff,
        w_ElasticPeakMin,
        w_ElasticPeakMax,
        w_M,
        w_C_ms,
        w_Ei,
        w_workdir,
        w_update_weight_continuity,
        w_update_weight_area,
    )

    w_Run = widgets.Button(description="Run")
    w_all = w_inputs + (w_Run,)

    def submit(b):
        # suppress warning from h5py
        import warnings

        warnings.simplefilter(action="ignore", category=FutureWarning)
        dos_update_weights = _get_dos_update_weights(
            w_update_weight_continuity.value, w_update_weight_area.value
        )
        #
        kargs = dict(
            mt_fraction=w_mt_fraction.value,
            const_bg_fraction=w_const_bg_fraction.value,
            Emin=w_Emin.value,
            Emax=w_Emax.value,
            dE=w_dE.value,
            Qmin=w_Qmin.value,
            Qmax=w_Qmax.value,
            dQ=w_dQ.value,
            T=w_T.value,
            Ecutoff=w_Ecutoff.value,
            elastic_E_cutoff=(w_ElasticPeakMin.value, w_ElasticPeakMax.value),
            M=w_M.value,
            C_ms=w_C_ms.value,
            Ei=w_Ei.value,
            workdir=w_workdir.value,
            initdos=initdos,
            update_strategy_weights=dos_update_weights,
        )
        import os
        import yaml

        # pprint.pprint(samplenxs)
        # pprint.pprint(mtnxs)
        # pprint.pprint(kargs)
        workdir = kargs["workdir"]
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        options = dict(kargs)
        options["ElasticPeakMin"] = w_ElasticPeakMin.value
        options["ElasticPeakMax"] = w_ElasticPeakMax.value
        with open(os.path.join(workdir, "getdos-opts.yaml"), "wt") as stream:
            yaml.dump(options, stream)
        maxiter = 10
        close = lambda w: w.close()
        list(map(close, w_all))
        from ..getdos import getDOS

        log_progress(
            getDOS(samplenxs, mt_nxs=mtnxs, maxiter=maxiter, **kargs),
            every=1,
            size=maxiter + 2,
        )
        return

    w_Run.on_click(submit)
    display(*w_all)
    return


def _get_dos_update_weights(*w):
    # w should be all positive
    wsum = sum(w)
    if wsum <= 0:
        N = len(w)
        return [1.0 / N] * N
    return [t / wsum for t in w]


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
                every = int(size / 200)  # every 0.5%
    else:
        assert every is not None, "sequence is iterator, set every"

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = "info"
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
                    label.value = "Running: {index} / ?: {msg}...".format(
                        index=index, msg=msg
                    )
                else:
                    progress.value = index
                    label.value = "Running: {index} / {size}: {msg}...".format(
                        index=index, size=size, msg=msg
                    )
    except:
        progress.bar_style = "danger"
        raise
    else:
        progress.bar_style = "success"
        progress.value = size
        # label.value = str(index or '?')
        label.value = "Done."


default_options = dict(
    mt_fraction=0.9,
    const_bg_fraction=0.0,
    Emin=-70,
    Emax=70,
    dE=1.0,
    Qmin=0.0,
    Qmax=14.0,
    dQ=0.1,
    T=300.0,
    Ecutoff=50.0,
    ElasticPeakMin=-20,
    ElasticPeakMax=7.0,
    M=50.94,
    C_ms=0.3,
    Ei=100.0,
    workdir="work",
)
