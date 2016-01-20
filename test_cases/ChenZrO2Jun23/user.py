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
longE           Guesstimate of the cutoff in meV. Please 
                  overestimate.
cutRange        min and max energy of high energy cutoff in meV
T               Temperature in Kelvin
M               Molecular weight for sample in AMU  
eStop           Use this to limit energy range. Units are meV.
N               Number of terms to include in multiphonon expansion...
Tol             How small does LSQ penalty between the incoming and
                  outgoing DOS have to be before we call them equal
maxIter         For a given C_ms, the maximum number of iterations 
                  before giving up on convergence.
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
longitudinal modes (or whatever modes are last before the cutoff frequency 
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
from multiphonon.constants import amu

#--- zro2 ------------------------------------------------------
Data           = "sqe.pkl"
MT             = None
C_ms           = arange(0.1,2.0,0.1)
backgroundFrac =    0.90 #ignore
constantFrac   =    0.00
cutoff         =    8.5
elasticCutAvg  =    3
longE          =   None#100.0
QHi            = 7
QLow           = 0
eStop          =  28.0 
T              =  320.0
M              =   23.24
N              =   5
Tol            =    1.0e-7
maxIter        =   50
cutRange       =  [26.0, 27.0]

#--- Output settings ----------------------------------------------------------
interactive    = True
viewDirectory  = os.path.abspath('.')
outputDir      = os.path.abspath('.')
