#!/usr/bin/env python
#

import os
import sys
import unittest
import numpy as np
import histogram.hdf as hh
from multiphonon.backward import sqe2dos
from multiphonon.backward.singlephonon_sqe2dos import guess_init_dos
from multiphonon.sqe import interp

interactive = False


here = os.path.dirname(__file__)
datadir = os.path.join(here, "../data")
sys.path.insert(0, datadir)


class TestCase(unittest.TestCase):
    def test1a(self):
        S = hh.load(os.path.join(datadir, "V-iqe-dE_0.2.h5"))
        DOS = sqe2dos.singlephonon_sqe2dos(S, T=300, Ecutoff=55.0, elastic_E_cutoff=(0.0, 0.0), M=50.94)
        E = DOS.E
        g = DOS.I
        # plot
        if interactive:
            import pylab

            pylab.plot(E, g)
            pylab.show()
        return
    def testguess_init_dos(self):
       cutoff=66
       S = hh.load(os.path.join(datadir,'V-iqe.h5'))
       newiqe = interp(S, newE=np.arange(-50,50,1.0))
       dE = newiqe.E[1]-newiqe.E[0]
       Eplus = newiqe.E[newiqe.E>-dE/2.0]
       res = guess_init_dos(Eplus,cutoff)
       unnorm = np.ones(len(Eplus))
       Equadbool = Eplus<cutoff/3
       unnorm[Equadbool] = Eplus[Equadbool]*Eplus[Equadbool]/cutoff/cutoff*9
       dE = Eplus[1]-Eplus[0]
       norm = unnorm.sum()*dE
       gcmp = unnorm/norm
       self.assertTrue(np.all(abs(res.I[1:]-gcmp[1:])/gcmp[1:]<1e-6))
       self.assertTrue(abs(res.I[0])<1e-6)
       self.assertTrue(np.all(abs(res.E[1:]-Eplus[1:])/Eplus[1:]<1e-6))


    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
