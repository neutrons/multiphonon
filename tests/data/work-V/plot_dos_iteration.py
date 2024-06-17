#!/usr/bin/env python
import os

curdir = os.path.dirname(__file__)

import matplotlib as mpl

mpl.rcParams["figure.figsize"] = 6, 4.5

from multiphonon.backward.plotutils import plot_dos_iteration

plot_dos_iteration(curdir, 6)
from matplotlib import pyplot as plt

plt.show()
