#!/usr/bin/env python
#
import os
import unittest

import histogram.hdf as hh
import numpy as np

from multiphonon.sqe import interp

interactive = False
datadir = os.path.join(os.path.dirname(__file__), "../data")


class TestCase(unittest.TestCase):
    def test1(self):
        """multiphonon.sqe.interp"""
        sqe = hh.load(os.path.join(datadir, "V-iqe.h5"))
        newsqe = interp(sqe, newE=np.arange(-70, 70, 1.0))
        hh.dump(newsqe, "V-iqe-interpd.h5")
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
