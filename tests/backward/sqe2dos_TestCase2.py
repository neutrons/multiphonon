#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)
here = os.path.dirname(__file__)

import unittest, warnings
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.backward import sqe2dos
from dos import loadDOS


class TestCase(unittest.TestCase):


    def test2a(self):
        "sqe2dos: V exp"
        iqehist = hh.load(os.path.join(datadir, 'XYZ2-iqe-Ei_20.h5'))
        initdos = hh.load(os.path.join(datadir, 'XYZ2-initdos-Ei_80.h5'))
        iterdos = sqe2dos.sqe2dos(
            iqehist, T=300,
            Ecutoff=17.1, elastic_E_cutoff=(-3., 1.1), M=79.452,
            C_ms=.05, Ei=20., workdir='work-XYZ2',
            initdos = initdos)
        list(iterdos)
        if interactive:
            dos = hh.load('work-XYZ2/final-dos.h5')
            pylab.errorbar(dos.E, dos.I, dos.E2**.5, label='final')
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
