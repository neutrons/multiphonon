#!/usr/bin/env python
#


import os
import unittest

interactive = False

datadir = os.path.join(os.path.dirname(__file__), "../data")
workdir = os.path.join(datadir, "work-V")
here = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    def setUp(self):
        if not interactive:
            import matplotlib

            matplotlib.use("Agg")
        from matplotlib import pyplot as plt

        from multiphonon.backward import plotutils

        self.pu = plotutils
        self.plt = plt

    def test1(self):
        """plot_residual"""
        self.pu.plot_residual(workdir)
        if interactive:
            self.plt.show()
        return

    def test2(self):
        """plot_dos_iteration"""
        self.pu.plot_dos_iteration(workdir)
        if interactive:
            self.plt.show()
        return

    def test3(self):
        """plot_intermediate_result_sqe"""
        self.pu.plot_intermediate_result_sqe(os.path.join(workdir, "round-5"))
        if interactive:
            self.plt.show()
        return

    def test4(self):
        """plot_intermediate_result_se"""
        self.pu.plot_intermediate_result_se(os.path.join(workdir, "round-5"))
        if interactive:
            self.plt.show()
        return

    pass  # end of TestCase


if __name__ == "__main__":
    interactive = True
    unittest.main()

# End of file
