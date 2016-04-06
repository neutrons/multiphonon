#!/usr/bin/env python
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


if __name__ == "__main__": unittest.main()
    
# End of file 
