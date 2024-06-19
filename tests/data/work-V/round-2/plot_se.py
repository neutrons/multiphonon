#!/usr/bin/env python
import os

import matplotlib as mpl
from matplotlib import pyplot as plt

from multiphonon.backward.plotutils import plot_intermediate_result_se as plot

curdir = os.path.dirname(__file__)

mpl.rcParams["figure.figsize"] = 12, 9

plot(curdir)

plt.show()
