#!/usr/bin/env python
#


import os
import unittest

import histogram.hdf as hh
import numpy as np

from multiphonon.dos import interp

interactive = False

here = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    def test1(self):
        """Interp"""
        dos = hh.load(os.path.join(here, "dos_to_interp.h5"))
        newE = np.arange(0, 45, 0.5)
        newdos = interp(dos, newE)
        expected = hh.load(os.path.join(here, "./expected/dos_interped.h5"))
        np.testing.assert_allclose(newdos.I, expected.I)
        np.testing.assert_allclose(newdos.E2, expected.E2)
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
