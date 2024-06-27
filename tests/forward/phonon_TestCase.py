#!/usr/bin/env python
#

import os
import sys
import tempfile
import unittest

import histogram as H
import histogram.hdf as hh
import numpy as np

interactive = False
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))
expected_results_dir = os.path.join(os.path.dirname(__file__), "expected_results")


class TestCase(unittest.TestCase):
    def test1(self):
        """multiphonon.forward.phonon.computeAnESet"""
        from dos import loadDOS

        E, g = loadDOS()
        dE = E[1] - E[0]
        # expand E a bit
        E = np.arange(E[0], 70, dE)
        g = np.concatenate((g, np.zeros(len(E) - len(g))))
        g /= g.sum() * dE
        from multiphonon.forward.phonon import computeAnESet

        kelvin2mev = 0.0862
        beta = 1.0 / (300 * kelvin2mev)
        E, An_set = computeAnESet(N=5, E=E, g=g, beta=beta, dE=dE)
        self._check(E, np.load(os.path.join(expected_results_dir, "phonon.test1.E.npy")))
        self._check(
            An_set,
            np.load(os.path.join(expected_results_dir, "phonon.test1.An_set.npy")),
        )
        if interactive:
            import pylab

            for An in An_set:
                pylab.plot(E, An)
                continue
            pylab.show()
        return

    def test2(self):
        """multiphonon.forward.phonon.computeSQESet"""
        from dos import loadDOS

        E, g = loadDOS()
        # expand E a bit
        dE = E[1] - E[0]
        E = np.arange(E[0], 70, dE)
        g = np.concatenate((g, np.zeros(len(E) - len(g))))
        int_g = np.sum(g) * dE
        g /= int_g

        Q = np.arange(0, 10, 0.1)
        dQ = Q[1] - Q[0]

        kelvin2mev = 0.0862
        beta = 1.0 / (300 * kelvin2mev)

        M = 50.0

        from multiphonon.forward.phonon import computeSQESet

        Q, E, S_set = computeSQESet(5, Q, dQ, E, dE, M, g, beta)

        import histogram.hdf as hh

        def save(S, name):
            saveSQE(Q, E, S, name)

        # import pylab
        for i, Sn in enumerate(S_set):
            # pylab.imshow(Sn.T)
            # pylab.show()
            # save(Sn, 'S%s' % (i+1))
            self._check(Sn, hh.load(os.path.join(expected_results_dir, "S%s.h5" % (i + 1,))).I)
            continue
        summed = S_set.sum(axis=0)
        save(summed, "S")
        return

    def test3(self):
        """multiphonon.forward.phonon.sqe"""
        from dos import loadDOS

        E, g = loadDOS()
        from multiphonon.forward.phonon import sqe

        Q, E, S = sqe(E, g, N=4)
        # saveSQE(Q,E,S, 'S_2..5')
        self._check(S, hh.load(os.path.join(expected_results_dir, "S_2..5.h5")).I)
        return

    def _check(self, a1, a2):
        self.assertTrue(np.allclose(a1, a2))

    pass  # end of TestCase


def saveSQE(Q, E, S, name):
    with tempfile.TemporaryDirectory() as tmpdirname:
        h = H.histogram(name, [("Q", Q, "angstrom**-1"), ("E", E, "meV")], S)
        hh_filename = "%s.h5" % (name,)
        hh_filepath = os.path.join(tmpdirname, hh_filename)
        hh.dump(h, hh_filepath)
        return


if __name__ == "__main__":
    interactive = True
    unittest.main()
