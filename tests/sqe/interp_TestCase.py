#!/usr/bin/env python
#


interactive = False


import unittest
import numpy as np, histogram.hdf as hh
from multiphonon.sqe import interp


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.sqe.interp"
        sqe = hh.load("../V-iqe.h5")
        newsqe = interp(sqe, newE=np.arange(-50, 50, 1.))
        hh.dump(newsqe, "V-iqe-interpd.h5")
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
