"""
This is a simple example where I(Q,E) data is already in the form
of a histogram, reduced from the raw experimental data.
All this script does is to convert I(Q,E) to Density of States
by performing multiphonon correction.
The different between this script and the "getdos-Al.py" script
is that here the histogram needs to be constructed from numpy
arrays of Q, E axes and intensity and squared errorbar matrices.
"""

import histogram.hdf as hh
import histogram as H
import os
import numpy as np

# when the system is headless, do not plot
headless = "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
if not headless:
    from matplotlib import pyplot as plt

# change into "examples" dir
here = os.path.dirname(__file__) or os.curdir
os.chdir(here)

# load I(Q,E) data (numpy arrays)
Q = np.load("data/Al-iqe-Q.npy")
E = np.load("data/Al-iqe-E.npy")
I = np.load("data/Al-iqe-I.npy")  # 2D array of intensities
E2 = np.load("data/Al-iqe-E2.npy")  # 2D array of errorbar squares

# create a histogram object from the numpy arrays
iqehist = H.histogram(
    "IQE", [("Q", Q, "1./angstrom"), ("E", E, "meV")], data=I, errors=E2
)

# interpolate I(Q, E) data so that the energy axis has "zero" as a bin center
from multiphonon.sqe import interp

newiqe = interp(iqehist, newE=np.arange(-40, 70, 1.0))

# save interpolated data just in case we need it later
hh.dump(newiqe, "data/Al-iqe-interped.h5")

# create processing engine with processing parameters
from multiphonon.backward import sqe2dos

workdir = "work-Al-from-nparrs"
iterdos = sqe2dos.sqe2dos(
    newiqe,
    T=300,
    Ecutoff=50.0,
    elastic_E_cutoff=(-10.0, 7),
    M=26.98,
    C_ms=0.2,
    Ei=80.0,
    workdir=workdir,
)
# process and plot
for i, dos in enumerate(iterdos):
    print("* Iteration", i)
    if not headless:
        plt.plot(dos.E, dos.I, label="%d" % i)
    continue

if not headless:
    plt.legend()
    plt.show()

print("Intermediate and final results are stored in directory %r" % workdir)
