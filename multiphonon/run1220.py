#!/usr/bin/python
#---docstring------------------------------------------------------------------
""" 
User defined parameters for the multiphonon code. 

It is assumed that data comes in a pickled tuple, (q,e,seq,sqerr), as from 
the DANSE reduction code.
Assuming your data is in this format, you can use:
   $ use arcs
   $ PlotSqe.py
to determine the appropriate values for the following parameters.  

  Here is a brief desctiption of parameters.  Farther down, there is more
detail about some of the more complicated ones.

Data            Filename for data set as string
MT              Filename for empty pan data as string
C_ms            numpy.array of possible multilpiers for m-phonon
backgroundFrac  Fraction of experimentally determined background to 
                  subtract.
constantFrac    Fraction of total scattering to subtract as constant 
                  background.
cutoff          energy for Elastic cutoff in meV
elasticCutAvg   Use this many bins after the cutoff to get an average 
                  value of S(E) near the cutoff.
longE           Guesstimate of the debye cutoff in meV. Please 
                  overestimate.
T               Temperature in Kelvin
M               Molecular weight for sample in AMU  
eStop           Use this to limit energy range. Units are meV.
N               Number of terms to include in multiphonon expansion...
Tol             How small does LSQ penalty between the incoming and
                  outgoing DOS have to be before we call them equal
interactive     True if you want to see how things are going.  False 
                  if you don't want to be bothered.
viewDirectory   Driectory in which mph.html will be created. When you 
                  run getDOS.py, images (*.png) will also be saved 
                  here.  You may then view the progress of your
                  calculation in your browser. 

  The elastic `cutoff` is the highest energy at at which we assume we are 
in elastic continuum.  We strip lower energy modes from the data, calling 
them Bragg scattering.

  The `longE` value is an approximate value for the cutoff of the 
longitudinal modes (or whatever modes are last before the Debye frequency 
-- could be optical, for example)  You should slightly overestimate this 
paramter -- it will give you a sum over less data, but ensure that you are
using only the data with sufficiently high resolution.

  eStop allows you to crop the data-set at some maximum energy.  This can
be useful as weird stuff tends to happen as the magnitude of the energy 
transfers approach the magnitude of the incident energies.
"""
#---end-docstring--------------------------------------------------------------
import os
from numpy import arange
from constants import amu

#--- Ni  300 K at Pharos ------------------------------------------------------
Data           = "/SNS/users/o3d/reduction/FeSi/sqe1220.pkl"
MT             = "/SNS/users/o3d/reduction/FeSi/sqe1209.pkl"
C_ms           = arange(0.4,1.4,0.2) 
backgroundFrac =    1.2
constantFrac   =    0.0
cutoff         =    8.0
elasticCutAvg  =    3
longE          =   58.0
eStop          =   80.0 
T              =   300.0
M              =   43.5  # 42.0 for FeSi, 43.5 for CoSi
N              =   5
Tol            =   1.0e-5

#--- Output settings ----------------------------------------------------------
interactive    = True
viewDirectory  = '/SNS/users/o3d/reduction/FeSi/dos/tmp'
outputDir      = '/SNS/users/o3d/reduction/FeSi/dos/tmp'
