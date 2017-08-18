#!/usr/bin/env python
#

# import pytest
# pytestmark = pytest.mark.skipif(True, reason="only run mannually")

interactive = False

import os
datadir = os.path.join(os.path.dirname(__file__), "data")

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
        "multiphonon.getdos"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs")))
        return
        
    def test2(self):
        "multiphonon.getdos: MT can"
        list(getDOS(
            os.path.join(datadir, "ARCS_V_annulus.nxs"),
            mt_nxs = os.path.join(datadir, "ARCS_V_annulus.nxs"),
            mt_fraction = 0.01,
        ))
        return
        
    def test3(self):
        "multiphonon.getdos: low T"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), T=1.5))
        return
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
