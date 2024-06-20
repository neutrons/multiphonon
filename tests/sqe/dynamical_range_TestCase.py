#!/usr/bin/env python
#

import os
import sys
import unittest

import histogram.hdf as hh
import numpy as np
from multiphonon.sqe import dynamical_range_mask, interp

interactive = False
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)


class TestCase(unittest.TestCase):
    def test2(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        newsqe = interp(iqehist, newE=np.arange(-50, 50, 1.0))
        mask = dynamical_range_mask(newsqe, Ei=120)
        # plot
        if interactive:
            import pylab

            pylab.imshow(mask.T[::-1])
            pylab.clim(0, None)
            pylab.colorbar()
            pylab.show()
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
