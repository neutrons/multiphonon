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

* The full I(Q,E) dynamic range measured is utilized, leading to better statistics
* Can be used with data measured at multiple incident energies to progressivley obtain better density of states
* Intermediate results are saved for further investigation
* Handle inputs in nxs and nxspe files for sample and empty can measurements

## Installation
**NOTE:** SNS users can skip this step and use this software package directly at SNS analysis cluster (see below). 

The multiphonon package can be installed using conda on a recent 64bit linux (ubuntu/fedora/centos) distribution:

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

## References
* Max Kresch et al., https://journals.aps.org/prb/abstract/10.1103/PhysRevB.75.104301, Appendix
* Brent Fultz et al., http://www.cacr.caltech.edu/projects/danse/doc/Inelastic_Book.pdf, Section 6.5 "Calculation of Multiphonon Scattering"

## History
[Releases](https://github.com/sns-chops/multiphonon/releases)
