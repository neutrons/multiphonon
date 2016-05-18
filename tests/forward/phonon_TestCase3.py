#!/usr/bin/env python
#


skip = True
interactive = False

import sys, os
sys.path.insert(0, os.path.abspath("../data"))

import unittest
import numpy


class TestCase(unittest.TestCase):


    def test1(self):
        "multiphonon.forward.phonon.computeAnESet: UN N dos"
        E,g = readdos()
        dE = E[1] - E[0]
        # expand E a bit
        E = numpy.arange(E[0], 500, dE)
        g = numpy.concatenate((g, numpy.zeros(len(E)-len(g))))
        
        g/=g.sum()*dE
        from multiphonon.forward.phonon import computeAnESet
        kelvin2mev = 0.0862
        beta = 1./(5*kelvin2mev)
        E, An_set = computeAnESet(N=10, E=E, g=g, beta=beta, dE=dE)
        if interactive:
            import pylab
            for An in An_set:
                pylab.plot(E, An)
                continue
            pylab.show()
        return
        
        
    def test2(self):
        "multiphonon.forward.phonon.sqe: UN N dos"
        E, g= readdos()
        dE = E[1] - E[0]
        #
        from multiphonon.forward.phonon import sqe
        q,e,i = sqe(E, g, T=5, M=14, N=7, Qmax=45.)
        from histogram import plot, histogram
        axes = [('Q', q, 'angstrom**-1'), ('E', e, 'meV')]
        iqe = histogram('iqe', axes, i)
        if interactive:
            plot(iqe)
        return
        
    pass  # end of TestCase


def readdos():
    datapath = os.path.join(
        os.path.dirname(__file__), '../data/UN-N-dos.dat'
        )
    from multiphonon.dos import io
    E, Z, error = io.fromascii(datapath)
    return E,Z


if __name__ == "__main__":
    global interactive
    interactive = True
    unittest.main()
    
# End of file 
