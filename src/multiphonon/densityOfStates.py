#!/usr/bin/python

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
  cutoff    = energy of cutoff
  cutRange  = (minimimum possible, maximum possible) values of cuttoff
  cutoffInd = index in energy array of cutoff
"""
#---end-docstring--------------------------------------------------------------
  def plotDOS(self,viewDirectory,Erange=False,Srange=False,TextSize=16):
    plotGE(self,viewDirectory,Erange=Erange,Srange=Srange,TextSize=16)
    return

  def __init__(self,*args,**keys):
    """ 
creates a dos from an expSqe instance or from an energy and a dos 
array using _initFromSqe or _initFromArrays respectively.
"""
    try:
      self.cutRange=keys['cutRange']
    except:
      self.cutRange=(1e-20,1e20)
    if args[0].__class__.__name__ == 'expSqe':
      self._initFromSqe(args[0])
    else:
      self._initFromArrays(args[0],args[1])
    return

  def _initFromSqe(self,sqe):
    """ initialize from an sqe object to a bogus DOS with the right shape"""
    debug.log( "sqe.zeroInd=%s" % (sqe.zeroInd,) )
    self.cutRange=sqe.cutRange
    e = sqe.e[sqe.zeroInd:]
    self._initFromArrays(e,e)
    return

  def _initFromArrays(self,e,g):
    """ initialize from an energy and a dos array """
    self.e = numpy.array(e)
    self.g = numpy.array(g)
    self.de = self.e[1]-self.e[0]
    self.cutoffInd = self.findCutoffInd()
    self.cutoff    = self.findCutoff()
    self.posify()
    self.normalize()
    self.gz = self.zero()
    return

  def findCutoff(self):
    """ finds cutoff energy """
    if self.cutoffInd == len(self.e):
      res = 1e20 # should be numpy.inf, but that makes pickle blow up.
    else:
      res = self.e[self.cutoffInd]
    return res

  def findCutoffInd(self):
    """finds index in energy array of cutoff energy"""
    cutmin = self.cutRange[0]
    i = numpy.argmin( (self.e - cutmin)**2 )
    if i==0:
      i += 1
    try:
      while self.g[i] > 0.0 and self.e[i] < self.cutRange[1]:
        i += 1
    except:
      i = len(self.e)
    return i

  def posify(self):
    """Zeros any negative values below the cutoff."""
    i=0
    while i < self.cutoffInd:
      if self.g[i] < 0.0:
        self.g[i] = 0.0
      i += 1
    return

  def zero(self):
    """ zeros dos after cutoff """
    debug.log("self.g.shape=%s" % (self.g.shape,) )
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


try:
  import journal
  debug = journal.debug( "multiphonon.densityOfStates" )
except ImportError:
  class _Debug:
    def log(self, msg): return #print msg
    line = log
  debug = _Debug()
  pass
#debug.activate()
