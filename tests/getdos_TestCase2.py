#!/usr/bin/env python
#

import pytest

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

import os

datadir = os.path.join(os.path.dirname(__file__), "data")

import imp

dataurls = imp.load_source("dataurls", os.path.join(datadir, "dataurls.py"))

from multiphonon.getdos import getDOS

import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        dest = os.path.join(datadir, "ARCS_V_annulus.nxs")
        if os.path.exists(dest):
            return
        url = dataurls.ARCS_V_annulus
        cmd = "wget --quiet %r -O %r" % (url, dest)
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
        return

    def test1a(self):
        "multiphonon.getdos: check energy axis"
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            for _ in getDOS(
                os.path.join(datadir, "ARCS_V_annulus.nxs"), Emin=-50.5, Emax=80, dE=1.0
            ):
                assert len(w) == 1
                assert "Energy axis modified" in str(w[-1].message)
                break
        return

    def test1b(self):
        "multiphonon.getdos: reuse reduction results"
        work = "work.getdos-reuse-reduction-results"
        if os.path.exists(work):
            import shutil

            shutil.rmtree(work)
        import warnings

        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), workdir=work))
            for w in ws:
                self.assertTrue("Reusing old reduction" not in str(w))
                continue
        # get dos again, this time we should see a warning
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always")
            list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), workdir=work))
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
            list(
                getDOS(
                    os.path.join(datadir, "ARCS_V_annulus.nxs"), Emin=0, workdir=work
                )
            )
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

# End of file
