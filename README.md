[![Build Status](https://travis-ci.org/sns-chops/multiphonon.svg?branch=master)](https://travis-ci.org/sns-chops/multiphonon) 
# multiphonon
Intended to be a rewrite of multiphonon (getDOS) originally authored by Max Kresch during the
[DANSE project](http://danse.us/) and
revised by several authors Brandon, Chen, Jennifer, and Dipanshu.

* Main functionality: Compute phonon Density of States (DOS) from powder Inelastic Neutron Scattering (INS) spectrum

## Installation
### Use conda
$ conda install -c mcvine multiphonon

### From source
Download src tarball and extract, then

$ python setup.py install

## Usage

### Through jupyter.sns.gov
https://www.youtube.com/watch?v=5XOX8RdHBnQ

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
