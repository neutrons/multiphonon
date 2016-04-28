#!/usr/bin/env python
#


interactive = False


import unittest
import numpy as np


class TestCase(unittest.TestCase):


    def test1(self):
        import histogram.hdf as hh
        S = hh.load("V-S1.h5")
        from multiphonon.backward.sqe2dos import sqe2dos
        E, g = sqe2dos(S, T=300, Ecutoff=55., M=50.94)
        # compare to the original dos data
        from dos import loadDOS
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
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
