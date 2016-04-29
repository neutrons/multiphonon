#!/usr/bin/env python
#


interactive = False

import os
datadir = os.path.join(os.path.dirname(__file__), "../data")

import unittest
import numpy as np, histogram.hdf as hh
from multiphonon.sqe import interp


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.sqe.interp"
        sqe = hh.load(os.path.join(datadir, "V-iqe.h5"))
        newsqe = interp(sqe, newE=np.arange(-70, 70, 1.))
        hh.dump(newsqe, "V-iqe-interpd.h5")
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
