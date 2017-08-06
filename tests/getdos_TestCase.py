#!/usr/bin/env python
#

import pytest
pytestmark = pytest.mark.skipif(True, reason="only run mannually")

interactive = False

import os
datadir = os.path.join(os.path.dirname(__file__), "data")

from multiphonon.getdos import getDOS

import unittest
class TestCase(unittest.TestCase):

    def test1(self):
        "multiphonon.getdos"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs")))
        return
        
    def test1a(self):
        "multiphonon.getdos: check energy axis"
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            for  _ in getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), Emin=-50.5, Emax=80, dE=1.):
                assert len(w)==1
                assert "Energy axis modified" in str(w[-1].message)
                break
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
