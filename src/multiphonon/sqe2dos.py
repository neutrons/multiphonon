#!/usr/bin/python
""" Function to take 1-phonon scattering to a phonon DOS """

import numpy
nar = numpy.add.reduce

from densityOfStates import densityOfStates
from multiphonon     import debyeWallerExp,gamma0

def sqe2dos(sqe):
  """ 
Takes an instance `sqe` of class expSqe and returns `res`, an instance 
of class densityOfStates, assuming that `sqe` is 1-phonon scattering 
only. 
""" 
  dos = densityOfStates(sqe)
  g0 = gamma0( sqe, dos )
  DW2 = debyeWallerExp(sqe,dos)
  res = nar( sqe.e*sqe.sqe*g0*(1 - numpy.exp(-sqe.e*sqe.beta)))[sqe.zeroInd:]
  res = densityOfStates(dos.e,res,cutRange=sqe.cutRange)
  return res

