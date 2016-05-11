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
            pylab.plot(E1, g1)
            pylab.plot(E1, ginterp)
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
        
        
    def test2a(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-55, 80, 1.))
        hh.dump(newiqe, 'V-iqe-interped.h5')
        iterdos = sqe2dos.sqe2dos(
            newiqe, T=300, Ecutoff=45., elastic_E_cutoff=(-12., 6.7), M=50.94,
            C_ms=0.2, Ei=120., workdir='work-V')
        for i, dos in enumerate(iterdos):
            # print dos
            # plot
            if interactive:
                # print '*' * 70
                pylab.plot(dos.E, dos.I, label='%d' % i)
        if interactive:
            pylab.legend()
            pylab.show()
        return
        
        
    def test2b(self):
        iqehist = hh.load(os.path.join(datadir, "Al-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-40, 70, 1.))
        hh.dump(newiqe, 'Al-iqe-interped.h5')
        iterdos = sqe2dos.sqe2dos(
            newiqe, T=300, Ecutoff=50., 
            elastic_E_cutoff=(-10., 7), M=26.98,
            C_ms=0.2, Ei=80., workdir='work-Al')
        for i, dos in enumerate(iterdos):
            # print dos
            # plot
            if interactive:
                # print '*' * 70
                pylab.plot(dos.E, dos.I, label='%d' % i)
        if interactive:
            pylab.legend()
            pylab.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    global interactive
    interactive = True
    import pylab
    unittest.main()
    
# End of file 
