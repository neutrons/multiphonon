"""
This is a simple example where I(Q,E) data is already in the form 
of a histogram, reduced from the raw experimental data.
All this script does is to convert I(Q,E) to Density of States
by performing multiphonon correction.
"""
import histogram.hdf as hh, os, numpy as np

# when the system is headless, do not plot
headless = 'DISPLAY' not in os.environ or not os.environ['DISPLAY']
if not headless:
    from matplotlib import pyplot as plt

# change into "examples" dir
here = os.path.dirname(__file__) or os.curdir
os.chdir(here)

# load I(Q,E) data
iqehist = hh.load("data/Al-iqe.h5")

# interpolate I(Q, E) data so that the energy axis has "zero" as a bin center
from multiphonon.sqe import interp
newiqe = interp(iqehist, newE = np.arange(-40, 70, 1.))

# save interpolated data just in case we need it later
hh.dump(newiqe, 'data/Al-iqe-interped.h5')

# create processing engine with processing parameters
from multiphonon.backward import sqe2dos
workdir = 'work-Al'
iterdos = sqe2dos.sqe2dos(
    newiqe, T=300, Ecutoff=50., 
    elastic_E_cutoff=(-10., 7), M=26.98,
    C_ms=0.2, Ei=80., workdir=workdir)

# process
for i, dos in enumerate(iterdos):
    print "* Iteration", i
    if not headless:
        plt.plot(dos.E, dos.I, label='%d' % i)
    continue

if not headless:
    plt.legend()
    plt.show()

print "Intermediate and final results are stored in directory %r" % workdir
