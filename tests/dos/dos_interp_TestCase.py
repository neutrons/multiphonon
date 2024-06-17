#!/usr/bin/env python
#

interactive = False

import os
import numpy as np
import histogram.hdf as hh

here = os.path.dirname(__file__)

from multiphonon.dos import interp

import unittest


class TestCase(unittest.TestCase):
    def test1(self):
        "interp"
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

# End of file
