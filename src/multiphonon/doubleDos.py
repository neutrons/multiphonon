#!/usr/bin/python

import numpy
nar = numpy.add.reduce

class doubleDos(object):
#---docstring------------------------------------------------------------------
  """
  Simple class to hold a phonon density of states that has been 
reflected about E=0 to form an even function.

Members defined here:

  e         = numpy.array{ energies }
  de        = energy increment
  g         = numpy.array{ density of states, with noise after cutoff }
  gz        = numpy.array{ density of states, with zeros after cutoff }
  cutoff    = energy of cutoff
  cutoffInd = index in energy array of cutoff
"""
#---end-docstring--------------------------------------------------------------

  def __init__(self,dos):
    """ Initinitializes from an instance of class densityOfStates """
    self.e         = self.double(dos.e,-1.0)
    self.g         = self.double(dos.g)
    self.gz        = self.double(dos.gz)
    self.cutoffInd = dos.cutoffInd
    self.cutoff    = dos.cutoff
    self.de        = dos.de

  def double(self,array,multi=1.0):
    """ 
Takes an array and returns that array reflected about array[0].
If multi = 1.0, even reflection, if multi = -1.0, odd.
"""
    res = (multi*array).tolist()
    res.reverse()
    return numpy.array( res + array[1:].tolist() )
