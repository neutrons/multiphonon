#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)

import unittest
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.backward import sqe2dos
from dos import loadDOS


class TestCase(unittest.TestCase):


    def test1a(self):
        S = hh.load(os.path.join(datadir, "V-S1.h5"))
        DOS = sqe2dos.singlephonon_sqe2dos(
            S, T=300, Ecutoff=55., elastic_E_cutoff=(0.,0.), M=50.94)
        E = DOS.E
        g = DOS.I
        # compare to the original dos data
        E1, g1 = loadDOS()
        ginterp = np.interp(E1, E, g)
        self.assert_(np.allclose(g1, ginterp))
        # plot
        if interactive:
            import pylab
            pylab.plot(E1, g1, label="Original DOS")
            pylab.plot(E1, ginterp, label="DOS from SQE")
            pylab.legend()
            pylab.show()
        return
        
        
    def test1b(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-50, 50, 1.))
        DOS = sqe2dos.singlephonon_sqe2dos(
            newiqe, T=300, Ecutoff=65., elastic_E_cutoff=(-20., 6.7), M=50.94)
        # plot
        if interactive:
            H.plot(DOS)
        return
        
        
    def test1b2(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-50.5, 50, 1.))
        from multiphonon.backward.singlephonon_sqe2dos import EnergyAxisMissingBinCenterAtZero
        with self.assertRaises(EnergyAxisMissingBinCenterAtZero):
            DOS = sqe2dos.singlephonon_sqe2dos(
                newiqe, T=300, Ecutoff=65., elastic_E_cutoff=(-20., 6.7), M=50.94)
        return
        
        
    def test1c(self):
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))
        newdos = sqe2dos.singlephonon_sqe2dos(
            iqehist, T=300, Ecutoff=125., elastic_E_cutoff=(-30., 15), M=12., initdos=initdos)
        # plot
        if interactive:
            pylab.plot(initdos.E, initdos.I)
            pylab.plot(newdos.E, newdos.I)
            pylab.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    global interactive
    interactive = True
    import pylab
    unittest.main()
    
# End of file 
