#!/usr/bin/env python
#

import os
import tempfile
import unittest

import histogram.hdf as hh
import numpy as np
import pytest
from multiphonon.sqe import load_source
from multiphonon.ui import batch

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

here = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(here, "..", "data")

dataurls = load_source("dataurls", os.path.join(datadir, "dataurls.py"))


class TestCase(unittest.TestCase):
    def test1(self):
        """multiphonon.ui.batch"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = os.path.join(tmpdirname, "tmp.batch")
            os.makedirs(tmpdir)
            dest = os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs")
            if os.path.exists(dest):
                return
            else:
                RuntimeError("file ARCS_V_annulus.nxs is missing")
            exec_cmd("ln -s %s %s/1.nxs" % (dest, tmpdir))
            exec_cmd("ln -s %s %s/2.nxs" % (dest, tmpdir))

            _p = lambda f: os.path.join(tmpdir, f)
            sample_nxs_list = [_p("1.nxs"), _p("2.nxs")]
            mt_nxs_list = [None, None]
            batch.process(sample_nxs_list, mt_nxs_list, os.path.join(here, "V-params.yaml"), tmpdirname)

            self.assertTrue(
                np.allclose(
                    hh.load(os.path.join(tmpdirname, "work-1.nxs,None/final-dos.h5")).I,
                    hh.load(os.path.join(here, "expected_results", "batch-1-final-dos.h5")).I,
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
