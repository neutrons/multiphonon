#!/SNS/software/bin/python

from expSqe import expSqe
import numpy
nar = numpy.add.reduce

from sqePlot import *

class densityOfStates(object):
#---docstring------------------------------------------------------------------
  """
  Simple class to hold a phonon density of states and directly relevant 
properties and methods. 

Members defined here:

  e         = numpy.array{ energies }
  de        = energy increment
  g         = numpy.array{ density of states, with noise after cutoff }
  gz        = numpy.array{ density of states, with zeros after cutoff }
  cutoff    = energy of debye cutoff
  cutoffInd = index in energy array of cutoff
"""
#---end-docstring--------------------------------------------------------------
  def plotDOS(self,viewDirectory,Erange=False,Srange=False,TextSize=16):
    plotGE(self,viewDirectory,Erange=Erange,Srange=Srange,TextSize=16)
    return

  def __init__(self,*args):
    """ 
creates a dos from an expSqe instance or from an energy and a dos 
array using _initFromSqe or _initFromArrays respectively.
"""
#    if isinstance(args[0],expSqe):
    if args[0].__class__.__name__ == 'expSqe':
      self._initFromSqe(args[0])
    else:
      self._initFromArrays(args[0],args[1])
    return

  def _initFromSqe(self,sqe):
    """ initialize from an sqe object to a bogus DOS with the right shape"""
    e = sqe.e[sqe.zeroInd:]
    self._initFromArrays(e,e)
    return

  def _initFromArrays(self,e,g):
    """ initialize from an energy and a dos array """
    self.e = numpy.array(e)
    self.g = numpy.array(g)
    self.de = e[1]-e[0]
    self.cutoffInd = self.findCutoffInd()
    self.cutoff    = self.findCutoff()
    self.normalize()
    self.gz = self.zero()
    return

  def findCutoff(self):
    """ finds debye cutoff energy """
    if self.cutoffInd == len(self.e):
      res = 1e20 # should be numpy.inf, but that makes pickle blow up.
    else:
      res = self.e[self.cutoffInd]
    return res

  def findCutoffInd(self):
    """finds index in energy array of debye cutoff energy"""
    i = 1
    try:
      while self.g[i] > 0.0:
        i += 1
    except:
      i = len(self.e)
    return i

  def zero(self):
    """ zeros dos after cutoff """
    res = numpy.array(self.g)
    res[self.cutoffInd:] = 0.0
    return res

  def normalize(self):
    """ normalizes dos up to cutoff """
    if self.cutoffInd == len(self.e):
      self.g /= nar(self.g)*self.de
    else:
      self.g /= nar(self.g[:self.cutoffInd])*self.de
    return

  def writeToFile(self,filename):
    """ saves dos output to csv file. """
    numpy.savetxt(filename,numpy.c_[self.e,self.g,self.gz],delimiter=',',header="e,g,zeroed_g")
    return

