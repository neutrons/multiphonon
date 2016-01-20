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


import unittest, os
from multiphonon.expSqe import *



class expSqe_TestCase(unittest.TestCase):

    def testCtor1(self):
        "expSqe: constructor from sqe.pkl"
        path = "test_cases/ni_0575"
        expSqe( os.path.join( path, 'sqe.pkl' ), 300., 50. )
        return
        
    def testCtor2(self):
        "expSqe: constructor from sqehist.pkl"
        path = "test_cases/4849-4844"
        expSqe( os.path.join( path, '4849-sqehist.pkl' ), 300., 50. )
        
        path = "test_cases/4849-4844"
        expSqe( os.path.join( path, '4844-sqehist.pkl' ), 300., 50. )
        return

    def testCtor3(self):
        "expSqe: constructor from T,M,q,e,sqe,sqeerr"
        path = "test_cases/4849-4844"
        import pickle
        fn = os.path.join( path, '4844-sqehist.pkl' )
        sqehist = pickle.load( open(fn) )
        q = sqehist.axisFromName( 'Q' ).binCenters()
        e = sqehist.axisFromName( 'energy' ).binCenters()
        s = sqehist.data().storage().asNumarray().copy()
        se = sqehist.errors().storage().asNumarray().copy()
        T = 300.
        M = 50.
        expSqe( q, e, s, se, T, M )
        return
    
    
    pass # end of expSqe_TestCase

    
def pysuite():
    suite1 = unittest.makeSuite(expSqe_TestCase)
    return unittest.TestSuite( (suite1,) )

def main():
    import journal
##     journal.debug('instrument').activate()
##     journal.debug('instrument.elements').activate()
    pytests = pysuite()
    alltests = unittest.TestSuite( (pytests, ) )
    unittest.TextTestRunner(verbosity=2).run(alltests)
    return


if __name__ == '__main__': main()
    

# version
__id__ = "$Id: expSqey_TestCase.py 834 2006-03-03 14:39:02Z linjiao $"

# End of file 
