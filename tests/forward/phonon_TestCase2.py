#!/usr/bin/env python
#

import os
import sys

sys.path.insert(0, os.path.abspath("../data"))

import unittest


class TestCase(unittest.TestCase):
    def test1(self):
        """multiphonon.forward.phonon.DWExp"""
        from dos import loadDOS
        from multiphonon.forward.phonon import DWExp

        E, g = loadDOS()
        dE = E[1] - E[0]
        import numpy as np

        Q = np.arange(0, 20, 0.1)
        M = 50.94  # vanadium
        # M = 58.6934 # nicole

        kelvin2mev = 0.0862
        T = 300
        beta = 1.0 / (T * kelvin2mev)
        dwexp = DWExp(Q, M, E, g, beta, dE)
        print(dwexp)
        return

    pass  # end of TestCase


if __name__ == "__main__":
    unittest.main()
