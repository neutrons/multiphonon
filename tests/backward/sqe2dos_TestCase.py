#!/usr/bin/env python
#
import os
import sys
import tempfile
import unittest
import warnings

import histogram.hdf as hh
import numpy as np
import pylab
from multiphonon.backward import sqe2dos
from multiphonon.sqe import interp

interactive = False

datadir = os.path.join(os.path.dirname(__file__), "../data")
sys.path.insert(0, datadir)
here = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    def test2a(self):
        """sqe2dos: V exp"""
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))
        with tempfile.TemporaryDirectory() as tmpdirname:
            newiqe = interp(iqehist, newE=np.arange(-15, 80, 1.0))
            hh.dump(newiqe, os.path.join(tmpdirname, "V-iqe-interped.h5"))
            work_dir = os.path.join(tmpdirname, "work-V")
            iterdos = sqe2dos.sqe2dos(
                newiqe,
                T=300,
                Ecutoff=55.0,
                elastic_E_cutoff=(-12.0, 6.7),
                M=50.94,
                C_ms=0.2,
                Ei=120.0,
                workdir=work_dir,
            )

            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter("always")
                for i, dos in enumerate(iterdos):
                    # print dos
                    # plot
                    if interactive:
                        # print '*' * 70
                        pylab.plot(dos.E, dos.I, label="%d" % i)
                        pass
                # check warning
                for w in ws:
                    assert "Scaling factor" not in str(w)

            path = os.path.join(here, "expected_results", "sqe2dos-test2a-final-dos.h5")
            # hh.dump(dos, path)
            expected = hh.load(path)
            self.assertTrue(np.allclose(dos.I, expected.I))
            self.assertTrue(np.allclose(dos.E2, expected.E2))
            if interactive:
                pylab.figure()
                pylab.errorbar(dos.E, dos.I + dos.I.max() / 5.0, dos.E2**0.5, label="new")
                pylab.errorbar(expected.E, expected.I, expected.E2**0.5, label="expected")
                pylab.legend()
                pylab.show()
            return

    def test2a2(self):
        """sqe2dos: check energy axis"""
        iqehist = hh.load(os.path.join(datadir, "V-iqe.h5"))

        with tempfile.TemporaryDirectory() as tmpdirname:
            work_dir = os.path.join(tmpdirname, "work-V")

            newiqe = interp(iqehist, newE=np.arange(-15.5, 80, 1.0))
            iterdos = sqe2dos.sqe2dos(
                newiqe,
                T=300,
                Ecutoff=55.0,
                elastic_E_cutoff=(-12.0, 6.7),
                M=50.94,
                C_ms=0.2,
                Ei=120.0,
                workdir=work_dir,
            )
            from multiphonon.backward.singlephonon_sqe2dos import (
                EnergyAxisMissingBinCenterAtZero,
            )

            with self.assertRaises(EnergyAxisMissingBinCenterAtZero):
                for i, dos in enumerate(iterdos):
                    # print dos
                    # plot
                    if interactive:
                        # print '*' * 70
                        pylab.plot(dos.E, dos.I, label="%d" % i)
            return

    def test2b(self):
        iqehist = hh.load(os.path.join(datadir, "Al-iqe.h5"))

        with tempfile.TemporaryDirectory() as tmpdirname:
            work_dir = os.path.join(tmpdirname, "work-Al")

            newiqe = interp(iqehist, newE=np.arange(-40, 70, 1.0))

            hh.dump(newiqe, os.path.join(tmpdirname, "Al-iqe-interped.h5"))
            iterdos = sqe2dos.sqe2dos(
                newiqe,
                T=300,
                Ecutoff=50.0,
                elastic_E_cutoff=(-10.0, 7),
                M=26.98,
                C_ms=0.2,
                Ei=80.0,
                workdir=work_dir,
            )
            for i, dos in enumerate(iterdos):
                # print dos
                # plot
                if interactive:
                    # print '*' * 70
                    pylab.plot(dos.E, dos.I, label="%d" % i)
            path = os.path.join(here, "expected_results", "sqe2dos-test2b-final-dos.h5")
            # hh.dump(dos, path)
            expected = hh.load(path)
            self.assertTrue(np.allclose(dos.I, expected.I))
            self.assertTrue(np.allclose(dos.E2, expected.E2))
            if interactive:
                pylab.figure()
                pylab.errorbar(dos.E, dos.I + dos.I.max() / 5, dos.E2**0.5, label="new")
                pylab.errorbar(expected.E, expected.I, expected.E2**0.5, label="expected")
                pylab.legend()
                pylab.show()
            return

    def test2c(self):
        iqehist = hh.load(os.path.join(datadir, "graphite-Ei_130-iqe.h5"))
        initdos = hh.load(os.path.join(datadir, "graphite-Ei_300-dos.h5"))

        with tempfile.TemporaryDirectory() as tmpdirname:
            work_dir = os.path.join(tmpdirname, "work-graphite")

            iterdos = sqe2dos.sqe2dos(
                iqehist,
                T=300,
                Ecutoff=100.0,
                elastic_E_cutoff=(-30.0, 15),
                M=12.0,
                C_ms=0.02,
                Ei=130.0,
                workdir=work_dir,
                initdos=initdos,
            )
            for i, dos in enumerate(iterdos):
                # print dos
                # plot
                if interactive:
                    # print '*' * 70
                    pylab.errorbar(dos.E, dos.I, dos.E2**0.5, label="%d" % i)
            path = os.path.join(here, "expected_results", "sqe2dos-test2c-final-dos.h5")
            # hh.dump(dos, path)
            expected = hh.load(path)
            self.assertTrue(np.allclose(dos.I, expected.I))
            # self.assert_(np.allclose(dos.E2, expected.E2))
            if interactive:
                pylab.figure()
                pylab.errorbar(dos.E, dos.I + dos.I.max() / 5, dos.E2**0.5, label="new")
                pylab.errorbar(expected.E, expected.I, expected.E2**0.5, label="expected")
                pylab.legend()
                pylab.show()
            return

    def test2c2(self):
        iqehist = hh.load(os.path.join(datadir, "DJX-iqe-Ei_20.h5"))
        # iqehist -= hh.load(os.path.join(datadir, "DJX-mtiqe-Ei_20.h5"))*(0.1, 0)

        with tempfile.TemporaryDirectory() as tmpdirname:
            work_dir = os.path.join(tmpdirname, "work-DJX")

            initdos = hh.load(os.path.join(datadir, "DJX-dos-Ei_80.h5"))
            iterdos = sqe2dos.sqe2dos(
                iqehist,
                T=300,
                Ecutoff=17.1,
                elastic_E_cutoff=(-3.0, 2),
                M=79.452,
                C_ms=0.02,
                Ei=20.0,
                workdir=work_dir,
                initdos=initdos,
            )
            for i, dos in enumerate(iterdos):
                # print dos
                # plot
                if interactive:
                    # print '*' * 70
                    pylab.errorbar(dos.E, dos.I, dos.E2**0.5, label="%d" % i)
            return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True

    unittest.main()
