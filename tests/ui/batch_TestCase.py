#!/usr/bin/env python
#

import pytest

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

import os

here = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(here, "..", "data")

import imp

dataurls = imp.load_source("dataurls", os.path.join(datadir, "dataurls.py"))

import numpy as np
import histogram.hdf as hh
from multiphonon.ui import batch

import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        dest = os.path.join(datadir, "ARCS_V_annulus.nxs")
        if not os.path.exists(dest):
            url = dataurls.ARCS_V_annulus
            cmd = "wget --quiet %r -O %r" % (url, dest)
            exec_cmd(cmd)
        # create temp dir
        self.tmpdir = tmpdir = os.path.abspath("tmp.batch")
        if os.path.exists(tmpdir):
            import shutil

            shutil.rmtree(tmpdir)
        os.makedirs(tmpdir)
        # make symlinks to create "a series of" data files
        exec_cmd("ln -s %s %s/1.nxs" % (dest, tmpdir))
        exec_cmd("ln -s %s %s/2.nxs" % (dest, tmpdir))
        return

    def test1(self):
        "multiphonon.ui.batch"
        _p = lambda f: os.path.join(self.tmpdir, f)
        sample_nxs_list = [_p("1.nxs"), _p("2.nxs")]
        mt_nxs_list = [None, None]
        batch.process(sample_nxs_list, mt_nxs_list, os.path.join(here, "V-params.yaml"))
        self.assertTrue(
            np.allclose(
                hh.load("work-1.nxs,None/final-dos.h5").I,
                hh.load(
                    os.path.join(here, "expected_results", "batch-1-final-dos.h5")
                ).I,
            )
        )
        return

    pass  # end of TestCase


def exec_cmd(cmd):
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)


if __name__ == "__main__":
    interactive = True
    unittest.main()

# End of file
