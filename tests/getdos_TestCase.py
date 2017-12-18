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
        "multiphonon.getdos"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs")))
        self.assert_(np.allclose(
            hh.load('work/final-dos.h5').I,
            hh.load(os.path.join(here, 'expected_results', 'getdos-test1-final-dos.h5')).I
        ))
        return
    
    def test2(self):
        "multiphonon.getdos: MT can"
        list(getDOS(
            os.path.join(datadir, "ARCS_V_annulus.nxs"),
            mt_nxs = os.path.join(datadir, "ARCS_V_annulus.nxs"),
            mt_fraction = 0.01,
            workdir='work-MT'
        ))
        self.assert_(np.allclose(
            hh.load('work-MT/final-dos.h5').I,
            hh.load(os.path.join(here, 'expected_results', 'getdos-test2-final-dos.h5')).I
        ))
        return
        
    def test3(self):
        "multiphonon.getdos: low T"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), T=1.5, workdir='work-lowT'))
        self.assert_(np.allclose(
            hh.load('work-lowT/final-dos.h5').I,
            hh.load(os.path.join(here, 'expected_results', 'getdos-test3-final-dos.h5')).I
        ))
        return
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
