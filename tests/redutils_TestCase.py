#!/usr/bin/env python
#

import pytest
# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

import os
here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")

import numpy as np, histogram.hdf as hh
from multiphonon.getdos import getDOS

import unittest
class TestCase(unittest.TestCase):

    def setUp(self):
        dest = os.path.join(datadir, 'ARCS_V_annulus.nxs')
        if os.path.exists(dest): return
        url = "https://www.dropbox.com/s/tbh4jcwiags410d/ARCS_V_annulus.nxs?dl=1"
        cmd = 'wget %r -O %r' % (url, dest)
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
        return

    def test1(self):
        "multiphonon.redutils"
        from multiphonon.redutils import reduce
        Qaxis = 0, 0.1, 14
        reduce(os.path.join(datadir, 'ARCS_V_annulus.nxs'), Qaxis, 'iqe.nxs')
        return
    
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
