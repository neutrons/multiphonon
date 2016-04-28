#!/usr/bin/env python
#


interactive = False


import unittest
import numpy


class TestCase(unittest.TestCase):


    def test1(self):
        import histogram.hdf as hh
        S = hh.load("V-S1.h5")
        from multiphonon.backward.sqe2dos import sqe2dos
        dos = sqe2dos(S, T=300, Ecutoff=55., M=50.94)
        import pylab
        pylab.plot(dos)
        pylab.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
