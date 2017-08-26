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
SNS users can skip this step and [use this software package directly at SNS analysis cluster](https://github.com/sns-chops/multiphonon/wiki#getdos-at-sns-analysis-cluster-using-jupyter). 

The multiphonon package can be installed using conda on a 64bit linux machine:

      $ conda config --add channels conda-forge
      $ conda config --add channels mantid
      $ conda config --add channels mcvine
      $ conda config --add channels neutrons
      $ conda install multiphonon

## Usage

See https://github.com/sns-chops/multiphonon/wiki

