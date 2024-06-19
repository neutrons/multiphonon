#!/usr/bin/env python
import os

from matplotlib import pyplot as plt

from multiphonon.backward.plotutils import plot_residual

curdir = os.path.dirname(__file__)

plot_residual(curdir)

plt.show()
