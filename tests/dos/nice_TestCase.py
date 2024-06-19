#!/usr/bin/env python
#

import os
import unittest

import numpy as np

from multiphonon.dos import nice

interactive = False
here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")


class TestCase(unittest.TestCase):
    def test1(self):
        """Smooth"""
        t = np.linspace(-4, 4, 100)
        x = np.sin(t)
        xn = x + np.random.randn(len(t)) * 0.1
        y = nice.smooth(xn)
        assert np.std(y - x) < np.std(x - xn)
        if interactive:
            from matplotlib import pyplot as plt

            plt.plot(t, xn, "+")
            plt.plot(t, y)
            plt.show()
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()

# End of file
