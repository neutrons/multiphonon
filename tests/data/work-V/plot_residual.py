#!/usr/bin/env python
import os

curdir = os.path.dirname(__file__)
from multiphonon.backward.plotutils import plot_residual

plot_residual(curdir)
from matplotlib import pyplot as plt

plt.show()
