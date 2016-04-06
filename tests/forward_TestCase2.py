#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#                        (C) 2007 All Rights Reserved  
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#



import unittestX as unittest
import journal

#debug = journal.debug( "TestCase" )
#warning = journal.warning( "TestCase" )


import numpy


class TestCase(unittest.TestCase):

    def test1(self):
        "mccomponents.sample.phonon.multiphonon.DWExp"
        from mccomponents.sample.phonon.multiphonon import DWExp
        from dos2 import loadDOS
        E, g = loadDOS()
        dE = E[1]-E[0]
        import numpy as np
        Q = np.arange(0,20,0.1)
        M = 50.94 # vanadium
        M = 58.6934 # nicole
        
        kelvin2mev = 0.0862
        T = 300
        beta = 1./(T*kelvin2mev)
        dwexp = DWExp(Q, M, E,g, beta, dE)
        # print dwexp
        return
        
        
    pass  # end of TestCase


import histogram as H, histogram.hdf as hh
def saveSQE(Q, E, S, name):
    h = H.histogram(
        name,
        [('Q', Q, 'angstrom**-1'),
         ('E', E, 'meV')],
        S)
    hh.dump(h, '%s.h5' % (name,))
    return


def pysuite():
    suite1 = unittest.makeSuite(TestCase)
    return unittest.TestSuite( (suite1,) )

    
    
if __name__ == "__main__":
    unittest.main()
    
# version
__id__ = "$Id$"

# End of file 
