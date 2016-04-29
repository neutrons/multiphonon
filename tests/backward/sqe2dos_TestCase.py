#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)

import unittest
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.backward.sqe2dos import sqe2dos
from dos import loadDOS


class TestCase(unittest.TestCase):


    def test1(self):
        S = hh.load(os.path.join(datadir, "V-S1.h5"))
        DOS = sqe2dos(S, T=300, Ecutoff=55., elastic_E_cutoff=0., M=50.94)
        E = DOS.E
        g = DOS.I
        # compare to the original dos data
        E1, g1 = loadDOS()
        ginterp = np.interp(E1, E, g)
        self.assert_(np.allclose(g1, ginterp))
        # plot
        if interactive:
            import pylab
            pylab.plot(E1, g1)
            pylab.plot(E1, ginterp)
            pylab.show()
        return
        
        
    def test2(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-50, 50, 1.))
        DOS = sqe2dos(newiqe, T=300, Ecutoff=65., elastic_E_cutoff=6.7, M=50.94)
        # plot
        if interactive:
            H.plot(DOS)
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
