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
import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

Imax = np.nanmax(hh.load(os.path.join(curdir, "exp-sqe.h5")).I)
zmin = 0 # -Imax/100
zmax = Imax/30

for index, (title, fn) in enumerate(plots):
    plt.subplot(3, 3, index+1)
    sqe = hh.load(os.path.join(curdir, fn))
    Q = sqe.Q
    E = sqe.E
    Y, X = np.meshgrid(E, Q)
    Z = sqe.I
    Zm = np.ma.masked_where(np.isnan(Z), Z)
    if title=='exp-residual':  zmin,zmax = np.array([-1.,1])/2. * zmax
    plt.pcolormesh(X, Y, Zm, vmin=zmin, vmax=zmax, cmap='hot')
    plt.colorbar()
    plt.title(title)
    continue

plt.tight_layout()
plt.show()
""" % plots_table

plot_intermediate_result_se_code = """#!/usr/bin/env python

import os
curdir = os.path.dirname(__file__)

import histogram.hdf as hh

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 12,9

plots = %r
plots = plots.strip().splitlines()
plots = [p.split() for p in plots]

for index, (title, fn) in enumerate(plots):
    sqe = hh.load(os.path.join(curdir, fn))
    Q = sqe.Q
    E = sqe.E
    I = sqe.I
    I[I!=I] = 0
    E2 = sqe.E2
    E2[E2!=E2] = 0
    se = sqe.sum('Q')
    if title.startswith('sim'):
        plt.plot(E, se.I, '-', label=title)
    else:
        plt.errorbar(E, se.I, se.E2**.5, ls='none', elinewidth=2, label=title)

    # set a reasonable y range
    if title == 'exp':
        max_inel_I = se[(E[-1]*0.1,None)].I.max()
    continue

plt.ylim(-max_inel_I/10., max_inel_I*1.1)
plt.legend()
plt.show()
""" % plots_table

plot_dos_iteration_code = """#!/usr/bin/env python

import histogram.hdf as hh, os
curdir = os.path.dirname(__file__)

import matplotlib.pyplot as plt, matplotlib as mpl, numpy as np
mpl.rcParams['figure.figsize'] = 6,4.5

for round_no in range(%(total_rounds)d): 
    fn = os.path.join(curdir, 'round-' + str(round_no), 'dos.h5')
    dos = hh.load(fn)
    plt.errorbar(dos.E, dos.I, dos.E2**.5, label=str(round_no))
    continue

plt.legend()
plt.show()
"""


plot_residual_code = """#!/usr/bin/env python

import histogram.hdf as hh, os, numpy as np
curdir = os.path.dirname(__file__)

exp_pos_se = hh.load(os.path.join(curdir, 'I_E-exp-posE.h5'))
residual_pos_se = hh.load(os.path.join(curdir, 'residual_E-posE.h5'))
E = exp_pos_se.E

import matplotlib.pyplot as plt
plt.errorbar(E, exp_pos_se.I, exp_pos_se.E2**.5, label='exp S(E)')
plt.errorbar(E, residual_pos_se.I, residual_pos_se.E2**.5, label='residual')
plt.plot([E[0], E[-1]], [0,0], 'k', label='baseline')
plt.legend()
plt.show()
"""
