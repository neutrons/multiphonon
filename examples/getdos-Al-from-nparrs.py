"""
This is a simple example where I(Q,E) data is already in the form 
of a histogram, reduced from the raw experimental data.
All this script does is to convert I(Q,E) to Density of States
by performing multiphonon correction.
"""
import histogram.hdf as hh, histogram as H, os, numpy as np
from matplotlib import pyplot as plt
# load data
Q = np.load("data/Al-iqe-Q.npy") 
E = np.load("data/Al-iqe-E.npy") 
I = np.load("data/Al-iqe-I.npy") # 2D array of intensities
E2 = np.load("data/Al-iqe-E2.npy") # 2D array of errorbar squares
# create a histogram object from the numpy arrays
iqehist = H.histogram('IQE', [('Q', Q, '1./angstrom'), ('E', E, 'meV')], data=I, errors=E2)
# interpolate data
from multiphonon.sqe import interp
newiqe = interp(iqehist, newE = np.arange(-40, 70, 1.))
# save interpolated data
hh.dump(newiqe, 'data/Al-iqe-interped.h5')
# create processing engine
from multiphonon.backward import sqe2dos
iterdos = sqe2dos.sqe2dos(
    newiqe, T=300, Ecutoff=50., 
    elastic_E_cutoff=(-10., 7), M=26.98,
    C_ms=0.2, Ei=80., workdir='work-Al-from-nparrs')
# process and plot
for i, dos in enumerate(iterdos):
    plt.plot(dos.E, dos.I, label='%d' % i)
plt.legend()
plt.show()
