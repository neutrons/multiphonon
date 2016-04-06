#!/usr/bin/env python
#

import unittest
import numpy


class TestCase(unittest.TestCase):

    def test1(self):
        "multiphonon.forward.DWExp"
        from multiphonon.forward import DWExp
        from dos import loadDOS
        E, g = loadDOS()
        dE = E[1]-E[0]
        import numpy as np
        Q = np.arange(0,20,0.1)
        M = 50.94 # vanadium
        # M = 58.6934 # nicole
        
        kelvin2mev = 0.0862
        T = 300
        beta = 1./(T*kelvin2mev)
        dwexp = DWExp(Q, M, E,g, beta, dE)
        print dwexp
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__": unittest.main()
    
# End of file 
