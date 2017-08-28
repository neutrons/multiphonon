[![Build Status](https://travis-ci.org/sns-chops/multiphonon.svg?branch=master)](https://travis-ci.org/sns-chops/multiphonon) 
# multiphonon
This is a rewrite of multiphonon (getDOS) code that was originally authored by 
Max Kresch during the [DANSE project](http://danse.us/) and
was then revised by several authors including Brandon, Chen, Jennifer, and Dipanshu
(their work were recorded as branches in this repo).

main functionality: **Compute phonon Density of States (DOS) from powder Inelastic Neutron Scattering (INS) spectrum**

It fixes some problems in the earlier versions of getDOS code and implemented new features.
The original requirements of this project is captured at [this ticket](https://github.com/sns-chops/multiphonon/issues/32).
And details of the features of this code can be found below.

## Features

* Handle inputs in nxs and nxspe files for sample and empty can measurements
* Can be used with data measured at multiple incident energies to progressivley obtain better density of states
* Intermediate results are saved for further investigation
* The full I(Q,E) dynamic range measured is utilized

## Installation
SNS users can skip this step and use this software package directly at SNS analysis cluster (see below). 

The multiphonon package can be installed using conda on a 64bit linux machine:

      $ conda config --add channels conda-forge
      $ conda config --add channels mantid
      $ conda config --add channels mcvine
      $ conda config --add channels neutrons
      $ conda install multiphonon

## Usage

### GetDOS at SNS analysis cluster using jupyter 
For SNS users, GetDOS can be performed at SNS analysis cluster through the jupyter.sns.gov website.
* First log into SNS analysis cluster using thinlinc. The instructions for that can be found at https://analysis.sns.gov/
* Inside the thinlinc session of analysis.sns.gov, open a browser window and connect to https://jupyter.sns.gov, and login with your XCAMS/UCAMS account credentials
* Follow the tutorial videos below:
  - [For the first time users, a setup is necessary](https://www.youtube.com/embed/5XOX8RdHBnQ?start=0&end=36&version=3)
  - [Run GetDOS2](https://www.youtube.com/embed/uTEEyifpG-k) (this works for SNS data only)

### GetDOS using local installation
For any user, GetDOS can be performed with a local installation of GetDOS and jupyter.
Examples and instructions can be found [here](/examples)

### Python scripting
If you want to use multiphonon without jupyter notebook, it is easy to write a python script for that.
The following script is an example of working with a SQE histogram already reduced from raw data.

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

# References
* Max Kresch et al., https://journals.aps.org/prb/abstract/10.1103/PhysRevB.75.104301
* Brent Fultz et al., http://www.cacr.caltech.edu/projects/danse/doc/Inelastic_Book.pdf
