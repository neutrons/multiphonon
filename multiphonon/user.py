#!/SNS/software/bin/python
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
#-------------------------------------------------------------------
import os
from numpy import arange
from constants import amu

#---------------------------------------------------------
Data           = "/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/Mo3Sb7_and_Mo3Sb5.5Te1.5/pkl_files/Mo3Sb7_55meV_100K_Feb.pkl"
#Data           = "/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/SnSe_and_SnS/pkl_files/Mo3Sb7_55mev_300K.pkl"
MT             = "/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/Empty_can/pkl_files/emptycan_55meV_100K_Feb.pkl"
C_ms           = [1.0] #arange(0.0,0.4,0.2) 
backgroundFrac =    1.0
constantFrac   =    0.0
cutoff         =    3.5
elasticCutAvg  =    3
longE          =   33.0 
eStop          =   45.0
Qmin           =   2.5
Qmax           =   8.0
T              =   300.0
M              =   113.2
# Mo3Sb7 = 114.014
# Mo3Sb5.5Te1.5 = 114.89
# Cu7PSe6 = 67.825 
# Cu10Zn2Sb4S13 = 57.59
# Cu12Sb4S13 = 57.46
# Ag8GeS6 = 75.213
# SnS = 75.38
# SnSe = 98.83
N              =   5
Tol            =   1.0e-3

#--- Output settings ----------------------------------------------------------
interactive    = True
plot           = False
viewDirectory  = '/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/Mo3Sb7_and_Mo3Sb5.5Te1.5/Mo3Sb7_55meV_100K_Feb/dos/'
outputDir      = '/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/Mo3Sb7_and_Mo3Sb5.5Te1.5/Mo3Sb7_55meV_100K_Feb/dos/'
