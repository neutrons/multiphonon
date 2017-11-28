#!/usr/bin/env python
#

interactive = False

import sys, os, warnings
from multiphonon.backward import plotutils
datadir = os.path.join(os.path.dirname(__file__), "../data")
workdir = os.path.join(datadir, 'work-V')
here = os.path.dirname(__file__)


import unittest
class TestCase(unittest.TestCase):


    def test1(self):
        plotutils.plot_residual(workdir)
        if interactive:
            plt.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    global interactive
    interactive = True
    from matplotlib import pyplot as plt
    unittest.main()
    
# End of file 
