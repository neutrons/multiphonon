#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#              (C) 2005 All Rights Reserved  All Rights Reserved
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#


import unittest, os, pickle, webbrowser
from multiphonon.sqePlot import *

data_dir = "sqePlot"
output_dir = 'sqePlot.outputs'

class sqePlot_TestCase(unittest.TestCase):

    def test_plotLSQ(self):
        self._test_func( plotLSQ, "plotLSQ.inputs.pkl" ,
                         ['lsq.png', 'lsq_f.png'] )
        return
    
    def test_plotComp(self):
        self._test_func( plotComp, "plotComp.inputs.pkl", ['seComp.png'] )
        return
    
    def test_plotGE(self):
        self._test_func( plotGE, "plotGE.inputs.pkl", ['dos.png'] )
        return
    
    def test_plotSE(self):
        self._test_func( plotSE, "plotSE.inputs.pkl",  ['se.png'] )
        return
    
    def test_plotSQE(self):
        self._test_func( plotSQE, "plotSQE.inputs.pkl", ['sqe.png'] )
        return
    
    def _test_func(self, func, inputs_file, output_files):
        f = os.path.join( data_dir, inputs_file )
        inputs = pickle.load( open( f ) )
        func(*inputs)

        for o in output_files:
            f = os.path.join( output_dir, o )
            webbrowser.open( f )
            continue
        return
    
    pass # end of sqePlot_TestCase

    
def pysuite():
    suite1 = unittest.makeSuite(sqePlot_TestCase)
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
__id__ = "$Id: sqePloty_TestCase.py 834 2006-03-03 14:39:02Z linjiao $"

# End of file 
