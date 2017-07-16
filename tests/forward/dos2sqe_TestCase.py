#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "..", "data")
sys.path.insert(0, datadir)

import unittest
import numpy as np
import histogram.hdf as hh, histogram as H


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.forward.dos2sqe"
        from dos import loadDOS
        E, g = loadDOS()
        Eaxis = H.axis('E', unit='meV', centers=E)
        doshist = H.histogram('DOS', [Eaxis], g)
        dE = E[1]-E[0]
        iqe = hh.load(os.path.join(datadir, 'V-iqe.h5'))
        from multiphonon.sqe import interp
        newiqe = interp(iqe, newE = np.arange(iqe.energy[0], 80., dE))
        hh.dump(newiqe, 'V-iqe-interped.h5')
        from multiphonon.forward import dos2sqe
        sqe = dos2sqe(doshist, 0.01, newiqe, 300, 50.94, 120.)
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
