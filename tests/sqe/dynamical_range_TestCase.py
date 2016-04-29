#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)

import unittest
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.sqe import interp, dynamical_range_mask

class TestCase(unittest.TestCase):


    def test2(self):
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        newsqe = interp(iqehist, newE=np.arange(-50, 50, 1.))
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
    
# End of file 
