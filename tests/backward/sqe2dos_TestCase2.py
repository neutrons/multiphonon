#!/usr/bin/env python
#

import os
import sys
import unittest

import histogram.hdf as hh
import pylab
from multiphonon.backward import sqe2dos

interactive = False

datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)
here = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    def test2a(self):
        """sqe2dos: V exp"""
        iqehist = hh.load(os.path.join(datadir, "XYZ2-iqe-Ei_20.h5"))
        initdos = hh.load(os.path.join(datadir, "XYZ2-initdos-Ei_80.h5"))
        iterdos = sqe2dos.sqe2dos(
            iqehist,
            T=300,
            Ecutoff=17.1,
            elastic_E_cutoff=(-3.0, 1.1),
            M=79.452,
            C_ms=0.05,
            Ei=20.0,
            workdir="work-XYZ2",
            initdos=initdos,
        )
        list(iterdos)
        if interactive:
            dos = hh.load("work-XYZ2/final-dos.h5")
            pylab.errorbar(dos.E, dos.I, dos.E2**0.5, label="final")
            pylab.legend()
            pylab.show()
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True

    unittest.main()
