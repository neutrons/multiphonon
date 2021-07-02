#!/usr/bin/env python
#

import pytest
from functools import reduce
# pytestmark = pytest.mark.skipif(False, reason="only run mannually")
# pytestmark = pytest.mark.needs_mantid

interactive = False

import os
here = os.path.dirname(__file__)
datadir = os.path.join(here, "data")

import numpy as np, histogram.hdf as hh

import unittest
class TestCase(unittest.TestCase):

    def test1(self):
        "multiphonon.flutils"
        from multiphonon.flutils import MDH2Histo
        MDH2Histo(os.path.join(datadir,'Al_md.h5'))
        return
    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
    
# End of file 
