#!/usr/bin/env python
#

interactive = False

import sys, os, warnings
datadir = os.path.join(os.path.dirname(__file__), "../data")
workdir = os.path.join(datadir, 'work-V')
here = os.path.dirname(__file__)


import unittest
class TestCase(unittest.TestCase):


    def setUp(self):
        if not interactive:
            import matplotlib
            matplotlib.use('Agg')
        from multiphonon.backward import plotutils
        from matplotlib import pyplot as plt
        self.pu = plotutils
        self.plt = plt


    def test1(self):
        self.pu.plot_residual(workdir)
        if interactive:
            self.plt.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
