#!/usr/bin/env python
#
import os
import tempfile
import unittest

import histogram.hdf as hh
import numpy as np
import pytest
from multiphonon.sqe import interp

interactive = False
datadir = os.path.join(os.path.dirname(__file__), "../data")


class TestCase(unittest.TestCase):
    @pytest.mark.creates_extra_files
    def test1(self):
        """multiphonon.sqe.interp"""
        sqe = hh.load(os.path.join(datadir, "V-iqe.h5"))
        newsqe = interp(sqe, newE=np.arange(-70, 70, 1.0))
        with tempfile.TemporaryDirectory() as tmpdirname:
            newsqe_filepath = os.path.join(tmpdirname, "V-iqe-interpd.h5")
            hh.dump(newsqe, newsqe_filepath)
            return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()
