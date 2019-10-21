#!/usr/bin/env python
#

import pytest
# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
pytestmark = pytest.mark.needs_mantid

interactive = False

import os
here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")

import imp
dataurls = imp.load_source('dataurls', os.path.join(datadir, 'dataurls.py'))

import numpy as np, histogram.hdf as hh
from multiphonon.getdos import getDOS

import unittest
class TestCase(unittest.TestCase):

    def setUp(self):
        dest = os.path.join(datadir, 'ARCS_V_annulus.nxs')
        if os.path.exists(dest): return
        url = dataurls.ARCS_V_annulus
        cmd = 'wget --quiet %r -O %r' % (url, dest)
        if os.system(cmd):
            raise RuntimeError("%s failed" % cmd)
        return

    def test1(self):
        "multiphonon.getdos"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs")))
        self.assert_(close_hist(
            hh.load('work/final-dos.h5'),
            hh.load(os.path.join(here, 'expected_results', 'getdos-test1-final-dos.h5'))
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
        self.assert_(close_hist(
            hh.load('work-MT/final-dos.h5'),
            hh.load(os.path.join(here, 'expected_results', 'getdos-test2-final-dos.h5'))
        ))
        return
        
    def test3(self):
        "multiphonon.getdos: low T"
        list(getDOS(os.path.join(datadir, "ARCS_V_annulus.nxs"), T=1.5, workdir='work-lowT'))
        self.assert_(close_hist(
            hh.load('work-lowT/final-dos.h5'),
            hh.load(os.path.join(here, 'expected_results', 'getdos-test3-final-dos.h5'))
        ))
        return
        
    pass  # end of TestCase


def close_hist(h1, h2):
    return np.allclose(h1.I, h2.I) and np.allclose(h1.E2, h2.E2)


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
