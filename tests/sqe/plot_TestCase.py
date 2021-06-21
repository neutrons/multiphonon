#!/usr/bin/env python
#


interactive = False

import os
datadir = os.path.join(os.path.dirname(__file__), "../data")

import unittest
import numpy as np, histogram.hdf as hh
from multiphonon.sqe import plot


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.sqe.plot"
        sqe = hh.load(os.path.join(datadir, "V-iqe.h5"))
        if not interactive:
            import matplotlib
            matplotlib.use('Agg')
        plot(sqe)
        if interactive:
            from matplotlib import pyplot as plt
            plt.show()
        return

    def test2(self):
        "multiphonon.sqe.plot with existing axis"
        import matplotlib
        from matplotlib import pyplot as plt
        if not interactive:
            matplotlib.use('Agg')
        sqe = hh.load(os.path.join(datadir, "V-iqe.h5"))
        f, ax = plt.subplots()
        plot(sqe,ax=ax)
        if interactive:
            f.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
