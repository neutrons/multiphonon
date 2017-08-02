[![Build Status](https://travis-ci.org/sns-chops/multiphonon.svg?branch=master)](https://travis-ci.org/sns-chops/multiphonon) 
# multiphonon
This is a rewrite of multiphonon (getDOS) that was originally authored by 
Max Kresch during the [DANSE project](http://danse.us/) and
was then revised by several authors including Brandon, Chen, Jennifer, and Dipanshu
(their work were recorded as branches in this repo).

main functionality: **Compute phonon Density of States (DOS) from powder Inelastic Neutron Scattering (INS) spectrum**

It fixes some problems in the earlier versions of getDOS code and implemented new features.
The original requirements of this project is captured at [this ticket](https://github.com/sns-chops/multiphonon/issues/32).
And details of the features of this code can be found below.

## Installation
### Use conda

      $ conda install -c mantid mantid-framework
      $ conda install -c mcvine multiphonon

## Usage

### Python scripting

      import histogram.hdf as hh, os, pylab
      # load data
      iqehist = hh.load("Al-iqe.h5") 
      # interpolate data
      from multiphonon.sqe import interp
      newiqe = interp(iqehist, newE = np.arange(-40, 70, 1.))
      # save interpolated data
      hh.dump(newiqe, 'Al-iqe-interped.h5')
      # create processing engine
      from multiphonon.backward import sqe2dos
      iterdos = sqe2dos.sqe2dos(
        newiqe, T=300, Ecutoff=50., 
        elastic_E_cutoff=(-10., 7), M=26.98,
        C_ms=0.2, Ei=80., workdir='work-Al')
      # process and plot
      for i, dos in enumerate(iterdos):
        pylab.plot(dos.E, dos.I, label='%d' % i)
      pylab.show()

### Through jupyter.sns.gov for SNS users
https://www.youtube.com/watch?v=5XOX8RdHBnQ

## Features

* Handle inputs in nxs and nxspe files for sample and empty can measurements
* Can be used with data measured at multiple incident energies to progressivley obtain better density of states
* Intermediate results are saved for further investigation
* The full I(Q,E) dynamic range measured is utilized
