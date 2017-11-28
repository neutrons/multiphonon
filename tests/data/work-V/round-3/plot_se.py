#!/usr/bin/env python
import os
curdir = os.path.dirname(__file__)
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = 12,9
from multiphonon.backward.plotutils import plot_intermediate_result_se as plot
plot(curdir)
from matplotlib import pyplot as plt
plt.show()
