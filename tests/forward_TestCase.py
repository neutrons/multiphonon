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


interactive = False


import unittestX as unittest
import journal

#debug = journal.debug( "TestCase" )
#warning = journal.warning( "TestCase" )


import numpy


class TestCase(unittest.TestCase):


    def test1(self):
        "mccomponents.sample.phonon.multiphonon.computeAnESet"
        from dos import loadDOS
        dos = loadDOS()
        E = dos.energy
        dE = E[1] - E[0]
        g = dos.I
        # expand E a bit
        E = numpy.arange(E[0], 70, dE)
        g = numpy.concatenate((g, numpy.zeros(len(E)-len(g))))

        g/=g.sum()*dE
        from mccomponents.sample.phonon.multiphonon import computeAnESet
        kelvin2mev = 0.0862
        beta = 1./(300*kelvin2mev)
        E, An_set = computeAnESet(N=5, E=E, g=g, beta=beta, dE=dE)
        if interactive:
            import pylab
            for An in An_set:
                pylab.plot(E, An)
                continue
            pylab.show()
        return
        
        
    def test2(self):
        "mccomponents.sample.phonon.multiphonon.computeSQESet"
        from dos import loadDOS
        dos = loadDOS()
        E = dos.energy; g = dos.I
        # expand E a bit
        dE = E[1] - E[0]
        E = numpy.arange(E[0], 70, dE)
        g = numpy.concatenate((g, numpy.zeros(len(E)-len(g))))
        int_g = numpy.sum(g) * dE
        g/=int_g
        
        Q = numpy.arange(0, 10, 0.1)
        dQ = Q[1] - Q[0]
        
        kelvin2mev = 0.0862
        beta = 1./(300*kelvin2mev)

        M = 50.
        
        from mccomponents.sample.phonon.multiphonon import computeSQESet
        Q, E, S_set= computeSQESet(5, Q, dQ, E, dE, M, g, beta)

        import histogram as H, histogram.hdf as hh
        def save(S, name): saveSQE(Q,E,S,name)
        # import pylab
        for i, Sn in enumerate(S_set):
            # pylab.imshow(Sn.T)
            # pylab.show()
            save(Sn, 'S%s' % (i+1))
            continue
        summed = S_set.sum(axis=0)
        save(summed, 'S')
        return
        

    def test3(self):
        "mccomponents.sample.phonon.multiphonon.sqe"
        from dos import loadDOS
        dos = loadDOS()
        assert dos.__class__.__name__ == 'Histogram', "%s is not a histogram" % (dos,)
        E = dos.energy
        g = dos.I
        from mccomponents.sample.phonon.multiphonon import sqe
        Q, E, S = sqe(E,g, N=4)
        saveSQE(Q,E,S, 'S_2..5')
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


def main():
    #debug.activate()
    #journal.debug('phonon_coherent_inelastic_polyxtal_kernel').activate()
    #journal.debug('random').activate()
    pytests = pysuite()
    alltests = unittest.TestSuite( (pytests, ) )
    res = unittest.TextTestRunner(verbosity=2).run(alltests)
    import sys; sys.exit(not res.wasSuccessful())

    
    
if __name__ == "__main__":
    interactive = True
    unittest.main()
    #  main()
    
# version
__id__ = "$Id: dispersion_TestCase.py 1126 2011-04-10 03:05:40Z linjiao $"

# End of file 
