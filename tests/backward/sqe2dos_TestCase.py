#!/usr/bin/env python
#


interactive = False

import sys, os
datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)
here = os.path.dirname(__file__)

import unittest, warnings
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.backward import sqe2dos
from dos import loadDOS


class TestCase(unittest.TestCase):


    def test2a(self):
        "sqe2dos: V exp"
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-15, 80, 1.))
        hh.dump(newiqe, 'V-iqe-interped.h5')
        iterdos = sqe2dos.sqe2dos(
            newiqe, T=300, Ecutoff=55., elastic_E_cutoff=(-12., 6.7), M=50.94,
            C_ms=.2, Ei=120., workdir='work-V')
        
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            for i, dos in enumerate(iterdos):
                # print dos
                # plot
                if interactive:
                    # print '*' * 70
                    pylab.plot(dos.E, dos.I, label='%d' % i)
                    pass
            # check warning
            for w in ws:
                assert 'Scaling factor' not in str(w)

        self.assert_(np.allclose(dos.I, hh.load(os.path.join(here, 'expected_results', 'sqe2dos-test2a-final-dos.h5')).I))
        if interactive:
            pylab.legend()
            pylab.show()
        return
        
        
    def test2a2(self):
        "sqe2dos: check energy axis"
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-15.5, 80, 1.))
        iterdos = sqe2dos.sqe2dos(
            newiqe, T=300, Ecutoff=55., elastic_E_cutoff=(-12., 6.7), M=50.94,
            C_ms=.2, Ei=120., workdir='work-V')
        from multiphonon.backward.singlephonon_sqe2dos import EnergyAxisMissingBinCenterAtZero
        with self.assertRaises(EnergyAxisMissingBinCenterAtZero):
            for i, dos in enumerate(iterdos):
                # print dos
                # plot
                if interactive:
                    # print '*' * 70
                    pylab.plot(dos.E, dos.I, label='%d' % i)
        return
        
        
    def test2b(self):
        iqehist = hh.load(os.path.join(datadir, "Al-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-40, 70, 1.))
        hh.dump(newiqe, 'Al-iqe-interped.h5')
        iterdos = sqe2dos.sqe2dos(
            newiqe, T=300, Ecutoff=50., 
            elastic_E_cutoff=(-10., 7), M=26.98,
            C_ms=0.2, Ei=80., workdir='work-Al')
        for i, dos in enumerate(iterdos):
            # print dos
            # plot
            if interactive:
                # print '*' * 70
                pylab.plot(dos.E, dos.I, label='%d' % i)
        self.assert_(np.allclose(dos.I, hh.load(os.path.join(here, 'expected_results', 'sqe2dos-test2b-final-dos.h5')).I))
        if interactive:
            pylab.legend()
            pylab.show()
        return
        
        
    def test2c(self):
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))
        iterdos = sqe2dos.sqe2dos(
            iqehist, T=300, Ecutoff=100., 
            elastic_E_cutoff=(-30., 15), M=12.,
            C_ms=0.02, Ei=130., workdir='work-graphite',
            initdos=initdos
        )
        for i, dos in enumerate(iterdos):
            # print dos
            # plot
            if interactive:
                # print '*' * 70
                pylab.errorbar(dos.E, dos.I, dos.E2**.5, label='%d' % i)
        self.assert_(np.allclose(dos.I, hh.load(os.path.join(here, 'expected_results', 'sqe2dos-test2c-final-dos.h5')).I))
        if interactive:
            dos = hh.load('work-graphite/final-dos.h5')
            pylab.errorbar(dos.E, dos.I, dos.E2**.5, label='final')
            pylab.legend()
            pylab.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    global interactive
    interactive = True
    import pylab
    unittest.main()
    
# End of file 
