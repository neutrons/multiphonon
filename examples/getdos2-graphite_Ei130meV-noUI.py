# This is a more advanced example for a demonatration of stitching.
# Please see http://sns-chops.github.io/multiphonon/usage.html#working-with-datasets-from-multiple-incident-energies
# for a detailed explanation.
#
# In this example, we are working with a system with phonon energies up to 220meV,
# we measured the spectrum at two different incident energies at ARCS:
# 300meV and 130meV.
#
#
import os

import histogram.hdf as hh
from multiphonon.backward import sqe2dos

# when the system is headless, do not plot
headless = "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
if not headless:
    from matplotlib import pyplot as plt
    from multiphonon.sqe import plot as plot_sqe


print("* Reading DOS from $E_i=300$...")
dos_300 = hh.load("./data/graphite-Ei_300-dos.h5")
#
if not headless:
    print("* Plotting DOS from $E_i=300$...")
    plt.figure()
    plt.plot(dos_300.E, dos_300.I)
    plt.show()

print("* Reading S(Q,E) from $E_i=130$...")
iqe_130 = hh.load("data/graphite-Ei_130-iqe.h5")
if not headless:
    print("* Plotting S(Q,E) from $E_i=130$...")
    plt.figure()
    plot_sqe(iqe_130)
    plt.xlim(0, 18)
    plt.ylim(-100, 120)
    plt.clim(0, 1e-4)
    plt.show()
# It is clear here only phonons with $E<120meV$ were measured in this dataset.


print("* Processing and stitching...")
iterdos = sqe2dos.sqe2dos(
    iqe_130,
    T=300,
    Ecutoff=100.0,
    elastic_E_cutoff=(-30.0, 15),
    M=12.0,
    C_ms=0.02,
    Ei=130.0,
    workdir="work-graphite",
    initdos=dos_300,
)
doslist = list(iterdos)
lastdos = doslist[-1]
# plot the partial DOS
partial_dos = lastdos[(None, 100)]
if not headless:
    print("* Plotting the partial DOS from Ei=130 ...")
    plt.figure()
    plt.plot(partial_dos.E, partial_dos.I)
    plt.show()
# plot the final DOS
if not headless:
    print("* Plotting the stitched DOS...")
    plt.figure()
    plt.plot(lastdos.E, lastdos.I)
    plt.show()
