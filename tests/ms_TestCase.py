#!/usr/bin/env python
#


interactive = False

import os

datadir = os.path.join(os.path.dirname(__file__), "data")

import unittest
import histogram.hdf as hh
import histogram as H
from multiphonon import ms


class TestCase(unittest.TestCase):
    def test1(self):
        "multiphonon.ms"
        mpsqe = hh.load(os.path.join(datadir, "V-S2..5.h5"))
        mssqe = ms.sqe(mpsqe, Ei=110.0)
        if interactive:
            H.plot(mssqe, min=0)
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()

# End of file
