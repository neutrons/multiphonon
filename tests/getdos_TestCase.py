#!/usr/bin/env python
#


import os
import tempfile
import unittest

import histogram.hdf as hh
import numpy as np
import pytest
from multiphonon.getdos import getDOS

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")


class TestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdirname = tempfile.TemporaryDirectory()
        dest = os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs")
        if os.path.exists(dest):
            return
        else:
            RuntimeError("file ARCS_V_annulus.nxs is missing")

    def tearDown(self):
        # Close the file, the directory will be removed after the test
        self.tmpdirname.cleanup()

    def test1(self):
        """multiphonon.getdos"""
        workdir = os.path.join(self.tmpdirname.name, "work")
        list(getDOS(os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs"), workdir=workdir))
        self.assertTrue(
            close_hist(
                hh.load(os.path.join(workdir, "final-dos.h5")),
                hh.load(os.path.join(here, "expected_results", "getdos-test1-final-dos.h5")),
            )
        )
        return

    def test2(self):
        """multiphonon.getdos: MT can"""
        workdir = os.path.join(self.tmpdirname.name, "work-MT")
        list(
            getDOS(
                os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs"),
                mt_nxs=os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs"),
                mt_fraction=0.01,
                workdir=workdir,
            )
        )
        self.assertTrue(
            close_hist(
                hh.load(os.path.join(workdir, "final-dos.h5")),
                hh.load(os.path.join(here, "expected_results", "getdos-test2-final-dos.h5")),
            )
        )
        return

    def test3(self):
        """multiphonon.getdos: low T"""
        workdir = os.path.join(self.tmpdirname.name, "work-lowT")
        list(getDOS(os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs"), T=1.5, workdir=workdir))
        self.assertTrue(
            close_hist(
                hh.load(os.path.join(workdir, "final-dos.h5")),
                hh.load(os.path.join(here, "expected_results", "getdos-test3-final-dos.h5")),
            )
        )
        return

    pass  # end of TestCase


def close_hist(h1, h2):
    return np.allclose(h1.I, h2.I) and np.allclose(h1.E2, h2.E2)


if __name__ == "__main__":
    interactive = True
    unittest.main()
