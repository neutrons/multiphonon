#!/usr/bin/env python
import os

import matplotlib as mpl
from matplotlib import pyplot as plt

from multiphonon.backward.plotutils import plot_dos_iteration

curdir = os.path.dirname(__file__)

mpl.rcParams["figure.figsize"] = 6, 4.5

plot_dos_iteration(curdir, 6)

plt.show()
