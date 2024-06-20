# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

plots_table = """
exp exp-sqe.h5
sim-singlephonon sp-sqe.h5
sim-multiphonon mp-sqe.h5
sim-multiple-scattering ms-sqe.h5
sim-correction sqe_correction.h5
exp-corrected-single-phonon corrected_sqe.h5
sim-total-inel total-inel-sqe.h5
exp-residual residual-sqe.h5
"""

plot_intermediate_result_sqe_code = """#!/usr/bin/env python
import os
curdir = os.path.dirname(__file__)
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = 12,9
from multiphonon.backward.plotutils import plot_intermediate_result_sqe as plot
plot(curdir)
from matplotlib import pyplot as plt
plt.show()
"""

plot_intermediate_result_se_code = """#!/usr/bin/env python
import os
curdir = os.path.dirname(__file__)
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = 12,9
from multiphonon.backward.plotutils import plot_intermediate_result_se as plot
plot(curdir)
from matplotlib import pyplot as plt
plt.show()
"""


plot_dos_iteration_code = """#!/usr/bin/env python
import os
curdir = os.path.dirname(__file__)

import matplotlib as mpl
mpl.rcParams['figure.figsize'] = 6,4.5

from multiphonon.backward.plotutils import plot_dos_iteration
plot_dos_iteration(curdir, %(total_rounds)d)
from matplotlib import pyplot as plt
plt.show()
"""


plot_residual_code = """#!/usr/bin/env python
import os
curdir = os.path.dirname(__file__)
from multiphonon.backward.plotutils import plot_residual
plot_residual(curdir)
from matplotlib import pyplot as plt
plt.show()
"""
