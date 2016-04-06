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


skip = True


import unittestX as unittest
import journal

#debug = journal.debug( "TestCase" )
#warning = journal.warning( "TestCase" )


import numpy


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.computeAnESet: UN N dos"
        dos = readdos()
        E = dos.energy
        dE = E[1] - E[0]
        g = dos.I
        # expand E a bit
        E = numpy.arange(E[0], 500, dE)
        g = numpy.concatenate((g, numpy.zeros(len(E)-len(g))))
        
        g/=g.sum()*dE
        from mccomponents.sample.phonon.multiphonon import computeAnESet
        kelvin2mev = 0.0862
        beta = 1./(5*kelvin2mev)
        E, An_set = computeAnESet(N=10, E=E, g=g, beta=beta, dE=dE)
        import pylab
        for An in An_set:
            pylab.plot(E, An)
            continue
        pylab.show()
        return
        
        
    def test2(self):
        "multiphonon.sqe: UN N dos"
        dos = readdos()
        E = dos.energy
        dE = E[1] - E[0]
        g = dos.I
        #
        from mccomponents.sample.phonon.multiphonon import sqe
        q,e,i = sqe(E, g, T=5, M=14, N=7, Qmax=45.)
        from histogram import plot, histogram
        axes = [('Q', q, 'angstrom**-1'), ('E', e, 'meV')]
        iqe = histogram('iqe', axes, i)
        plot(iqe)
        return
        
        
    pass  # end of TestCase


def readdos():
    from mccomponents.sample.phonon.read_dos import doshist_fromascii
    datapath = 'UN-N-dos.dat'
    dos = doshist_fromascii(datapath)
    return dos


def pysuite():
    suite1 = unittest.makeSuite(TestCase)
    return unittest.TestSuite( (suite1,) )


def main():
    #debug.activate()
    #journal.debug('phonon_coherent_inelastic_polyxtal_kernel').activate()
    #journal.debug('random').activate()
    pytests = pysuite()
    alltests = unittest.TestSuite( (pytests, ) )
    res = unittest.TextTestRunner(verbosity=2).run(alltests)
    import sys; sys.exit(not res.wasSuccessful())

    
    
if __name__ == "__main__":
    unittest.main()
    #  main()
    
# version
__id__ = "$Id: dispersion_TestCase.py 1126 2011-04-10 03:05:40Z linjiao $"

# End of file 
