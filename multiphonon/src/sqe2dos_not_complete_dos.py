#!/SNS/software/bin/python
""" Function to take 1-phonon scattering to a phonon DOS """

import numpy
nar = numpy.add.reduce

from densityOfStates import densityOfStates
from multiphonon_not_complete_dos import debyeWallerExp
#from multiphonon import *
from multiphonon_not_complete_dos import gamma0

def sqe2dos(sqe,g0):
  """ 
Takes an instance `sqe` of class expSqe and g0 thermal factor from full dos results, and returns `res`, an instance 
of class densityOfStates, assuming that `sqe` is 1-phonon scattering 
only. 
""" 
  dos = densityOfStates(sqe)
  #g0 = gamma0( sqe, dos )
  #print g0
  #DW2 = debyeWallerExp(sqe,dos,g0)
  res = nar( sqe.e*sqe.sqe*g0*(1 - numpy.exp(-sqe.e*sqe.beta)))[sqe.zeroInd:]
  res = densityOfStates(dos.e,res)
  return res

