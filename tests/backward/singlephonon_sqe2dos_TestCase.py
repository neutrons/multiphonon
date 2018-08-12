#!/usr/bin/env python
#


interactive = False

import sys, os
here = os.path.dirname(__file__)
datadir = os.path.join(here, "../data")
sys.path.insert(0, datadir)

import unittest, warnings
import numpy as np, histogram.hdf as hh, histogram as H
from multiphonon.backward import sqe2dos
from dos import loadDOS


class TestCase(unittest.TestCase):


    def test1a(self):
        "singlephonon_sqe2dos: simulated vanadium SQE -> DOS"
        S = hh.load(os.path.join(datadir, "V-S1.h5"))
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            DOS = sqe2dos.singlephonon_sqe2dos(
                S, T=300, Ecutoff=55., elastic_E_cutoff=(0.,0.), M=50.94)
            for w in ws:
                assert 'Scaling factor' not in str(w)
        E = DOS.E
        g = DOS.I
        # compare to the original dos data
        E1, g1 = loadDOS()
        ginterp = np.interp(E1, E, g)
        self.assert_(np.allclose(g1, ginterp))
        # plot
        if interactive:
            import pylab
            pylab.plot(E1, g1, label="Original DOS")
            pylab.plot(E1, ginterp, label="DOS from SQE")
            pylab.legend()
            pylab.show()
        return
        
        
    def test1b(self):
        "singlephonon_sqe2dos: exp vanadium SQE -> DOS"
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-50, 50, 1.))
        DOS = sqe2dos.singlephonon_sqe2dos(
            newiqe, T=300, Ecutoff=65., elastic_E_cutoff=(-20., 6.7), M=50.94)
        path = os.path.join(here, 'expected_results', 'test1b-dos.h5')
        expected = hh.load(path)
        self.assert_(np.allclose(DOS.I, expected.I))
        self.assert_(np.allclose(DOS.E2, expected.E2))
        # plot
        if interactive:
            H.plot(DOS)
        return
        
        
    def test1b2(self):
        "singlephonon_sqe2dos: check energy axis"
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        from multiphonon.sqe import interp
        newiqe = interp(iqehist, newE = np.arange(-50.5, 50, 1.))
        from multiphonon.backward.singlephonon_sqe2dos import EnergyAxisMissingBinCenterAtZero
        with self.assertRaises(EnergyAxisMissingBinCenterAtZero):
            DOS = sqe2dos.singlephonon_sqe2dos(
                newiqe, T=300, Ecutoff=65., elastic_E_cutoff=(-20., 6.7), M=50.94)
        return
        
        
    def test1c(self):
        "singlephonon_sqe2dos: partial update"
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))
        newdos = sqe2dos.singlephonon_sqe2dos(
            iqehist, T=300, Ecutoff=100., elastic_E_cutoff=(-30., 15), M=12., initdos=initdos)
        # plot
        if interactive:
            pylab.plot(initdos.E, initdos.I)
            pylab.plot(newdos.E, newdos.I)
            pylab.show()
        return
        
        
    def test1c1(self):
        "singlephonon_sqe2dos: partial update -- keep area"
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))
        newdos = sqe2dos.singlephonon_sqe2dos(
            iqehist, T=300, Ecutoff=110., elastic_E_cutoff=(-30., 15), M=12., initdos=initdos, update_weights=[0., 1.])
        path = os.path.join(here, 'expected_results', 'test1c1-dos.h5')
        # hh.dump(newdos, path)
        expected = hh.load(path)
        self.assert_(np.allclose(newdos.I, expected.I))
        self.assert_(np.allclose(newdos.E, expected.E))
        self.assert_(np.allclose(newdos.E2, expected.E2))
        # plot
        if interactive:
            pylab.errorbar(initdos.E, initdos.I, initdos.E2**.5, label='init')
            pylab.errorbar(newdos.E, newdos.I, newdos.E2**.5, label='new')
            # pylab.errorbar(expected.E, expected.I, expected.E2**.5, label='expected')
            pylab.legend()
            pylab.show()
        return
        
        
    def test1c2(self):
        "singlephonon_sqe2dos: partial update -- force continuous"
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))
        newdos = sqe2dos.singlephonon_sqe2dos(
            iqehist, T=300, Ecutoff=110., elastic_E_cutoff=(-30., 15), M=12., initdos=initdos, update_weights=[1., 0.])
        path = os.path.join(here, 'expected_results', 'test1c2-dos.h5')
        # hh.dump(newdos, path)
        expected = hh.load(path)
        self.assert_(np.allclose(newdos.I, expected.I))
        self.assert_(np.allclose(newdos.E, expected.E))
        # self.assert_(np.allclose(newdos.E2, expected.E2))
        # plot
        if interactive:
            pylab.errorbar(initdos.E, initdos.I, initdos.E2**.5, label='init')
            pylab.errorbar(newdos.E, newdos.I, newdos.E2**.5, label='new')
            # pylab.errorbar(expected.E, expected.I, expected.E2**.5, label='expected')
            pylab.legend()
            pylab.show()
        return
        
        
    def test1d(self):
        "singlephonon_sqe2dos: partial update -- warnings"
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_30-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_130-dos.h5"))
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            newdos = sqe2dos.singlephonon_sqe2dos(
                iqehist, T=300, Ecutoff=20., elastic_E_cutoff=(-10., 8), M=12., initdos=initdos)
            has_scaling_factor_warning = False
            for w in ws:
                has_scaling_factor_warning = has_scaling_factor_warning or ('Scaling factor' in str(w))
                continue
            self.assert_(has_scaling_factor_warning)
        # plot
        if interactive:
            pylab.plot(initdos.E, initdos.I)
            pylab.plot(newdos.E, newdos.I)
            pylab.show()
        return
        
        
    pass  # end of TestCase


if __name__ == "__main__":
    global interactive
    interactive = True
    import pylab
    unittest.main()
    
# End of file 
