#!/usr/bin/env python
#

import os
import tempfile
import unittest

import pytest
from multiphonon.sqe import load_source

# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")

dataurls = load_source("dataurls", os.path.join(datadir, "dataurls.py"))


class TestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdirname = tempfile.TemporaryDirectory()
        dest = os.path.join(self.tmpdirname.name, "ARCS_V_annulus.nxs")
        url = dataurls.ARCS_V_annulus
        cmd = "wget --quiet %r -O %r" % (url, dest)
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
        return

    def test1(self):
        """multiphonon.redutils"""
        from multiphonon.redutils import reduce

        Qaxis = 0, 0.1, 14
        reduce(
            os.path.join(self.tmpdirname.name, "ARCS_V_annulus.nxs"), Qaxis, os.path.join(self.tmpdirname.name, "iqe.nxs")
        )
        return

    def test2(self):
        """multiphonon.redutils"""
        from multiphonon.redutils import reduce

        Qaxis = -0.05, 0.1, 14.95001
        Eaxis = -100.5, 1.0, 99.5001
        reduce(
            os.path.join(self.tmpdirname.name, "ARCS_V_annulus.nxs"),
            Qaxis,
            os.path.join(self.tmpdirname.name, "iqe.nxs"),
            eaxis=Eaxis,
        )
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
