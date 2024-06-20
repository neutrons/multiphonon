#!/usr/bin/env python
#

import os
import sys
import unittest

import histogram.hdf as hh

from multiphonon.backward import sqe2dos

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

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
