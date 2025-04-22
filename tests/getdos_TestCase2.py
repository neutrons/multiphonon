#!/usr/bin/env python
#

import os
import tempfile
import unittest
import warnings

import pytest
from multiphonon.getdos import getDOS

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

datadir = os.path.join(os.path.dirname(__file__), "data")


class TestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdirname = tempfile.TemporaryDirectory()
        dest = os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs")
        if os.path.exists(dest):
            return
        else:
            raise RuntimeError("ARCS_V_annulus.nxs is missing.")

    def test1a(self):
        """multiphonon.getdos: check energy axis"""
        workdir = os.path.join(self.tmpdirname.name, "work")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            for _ in getDOS(
                os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs"),
                Emin=-50.5,
                Emax=80,
                dE=1.0,
                workdir=workdir,
            ):
                assert len(w) == 1
                assert "Energy axis modified" in str(w[-1].message)
                break
        return

    def test1b(self):
        """multiphonon.getdos: reuse reduction results"""
        work = os.path.join(self.tmpdirname.name, "work.getdos-reuse-reduction-results")
        arcs_filepath = os.path.join(datadir, "multiphonon-data", "ARCS_V_annulus.nxs")

        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            list(getDOS(arcs_filepath, workdir=work))
            for w in ws:
                self.assertTrue("Reusing old reduction" not in str(w))
                continue
        # get dos again, this time we should see a warning
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            list(getDOS(arcs_filepath, workdir=work))
            warned = False
            for w in ws:
                warned = warned or ("Reusing old reduction" in str(w))
                if warned:
                    break
                continue
            self.assertTrue(warned)
        # get dos using different settings. should not see warning
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            list(getDOS(arcs_filepath, Emin=0, workdir=work))
            for w in ws:
                self.assertTrue("Reusing old reduction" not in str(w))
                continue
            import histogram.hdf as hh

            iqe = hh.load(os.path.join(work, "iqe.h5"))
            self.assertTrue(iqe.E[0] == 0.0)
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
