# -*- python -*-
#


def process(sample_nxs_list, mt_nxs_list, parameter_yaml):
    """Process a series of files using a fixed set of parameters

    This implementation just shows one way of processing a batch job,
    where the processing parameters stay fixed except for
    the sample and emtpy can nexus files.
    For more complex batch processing, a user could follow this example and
    implement his/her own methods.
    """
    import os

    from ..getdos import getDOS
    from . import Context, context2kargs

    assert len(sample_nxs_list) == len(mt_nxs_list)
    # load parameters
    params = Context()
    params.from_yaml(parameter_yaml)
    if hasattr(params, "iqe_nxs"):
        del params.iqe_nxs
    if hasattr(params, "iqe_h5"):
        del params.iqe_h5
    # process
    for sample_nxs, mt_nxs in zip(sample_nxs_list, mt_nxs_list):
        params.sample_nxs = sample_nxs
        params.mt_nxs = mt_nxs
        kargs = context2kargs(params)
        workdir = "work-%s,%s" % (
            os.path.basename(sample_nxs),
            os.path.basename(mt_nxs) if mt_nxs else mt_nxs,
        )
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        with open(os.path.join(workdir, "log.getdos"), "wt") as log:
            kargs["workdir"] = workdir
            print("* Processing %s, %s" % (sample_nxs, mt_nxs))
            for msg in getDOS(**kargs):
                log.write("%s\n" % (msg,))
        continue
