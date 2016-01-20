#!/usr/bin/python

#TODO: get rid of this annoying 'must be symmetric around zero and contain zero requirement for the energy'

from constants import *
#import cPickle as cp
import pickle
import numpy
nar = numpy.add.reduce
import numpy as n

from sqePlot import *
TOL = 1e-20

class expSqe(object):
#---docstring------------------------------------------------------------------
  """
  Class to hold an experimental measurement of S(Q,E) and some highly
relevant ancillary data.

Note:  A `false member` is a data member that is calculated on the fly, 
and cannot, therefore, be set by the user. The work for these functions
happens in `_function(...)`, and there are placeholder definitions in
`function(...)` so that the false members show up when the user 
attempts tab completion.

Members defined here:

  T         = Temperature of measurement                [K]
  M         = Molecular weight of the sample            [kg]
  e         = Energy array                              [meV]
  q         = Momentum transfer array                   [1/Angstroms]
  sqe       = S(Q,E)                                    [arb]
  sqerr     = Error from counting statistics for S(Q,E) [arb]
  mask      = 0 for no data, 1 for data

`False members` defined here
  
  de        = energy increment                          [meV]
  se        = S(E) = sum_Q{ S(Q,E) }                    [arb]
  sq        = S(Q) = sum_E{ S(Q,E) }                    [arb]
  beta      = 1 / k_b T                                 [1/meV]
  zeroInd   = Index of e = 0                            []
  shape     = Tuple with ( len(q),len(e) )              []
"""
#---end-docstring--------------------------------------------------------------

  def slopeCut(self):
    """Returns index of data cutoff for the slope of the high E scatter."""
    se = self.se
    z  = self.zeroInd 
    while z < len(se) and se[z] > 0.0:
      z += 1
    return z+1

  def expand(self,eMul):
    """ expands the e-range by a factor eMul. Adjusts all data members 
appropriately. """
    newE     = numpy.arange(self.e[0]*eMul,self.e[-1]*eMul+self.de,self.de)
    newSqe   = numpy.zeros( (self.q.shape[0],newE.shape[0]) )
    newSqerr = numpy.zeros( (self.q.shape[0],newE.shape[0]) )
    start    = (( newE - self.e[0] )**2).argmin()
    stop     = (( newE - self.e[-1]-self.de )**2).argmin()
    newSqe[:,start:stop] = self.sqe
    newSqerr[:,start:stop] = self.sqerr
    self.e     = newE
    self.sqe   = newSqe
    self.sqerr = newSqerr
    self.updateMask()
    return

  def updateMask(self):
    """ Creates a mask for the data set -- 0 wherever there is no data, 1 
wherever data exists."""
    mask = numpy.zeros(self.shape,'i') + 1
    for q in range(len(self.q)):
      for e in range(len(self.e)):
        if self.sqe[q,e] == 0:
          mask[q,e] = 0
    self.mask = mask
    debug.log( "mask shape = %s" % (mask.shape,) )
    return 
  
  def plotSE(self,viewDirectory,Erange=False,Srange=False,TextSize=16):
    plotSE(self,viewDirectory,Erange=Erange,Srange=Srange,TextSize=TextSize)
    return

  def plotMask(self,viewDirectory,TextSize=16):
    mask = expSqe(self)
    mask.sqe = mask.mask
    filename = 'mask.png'
    title = 'Mask(Q,E)'
    plotSQE(mask,viewDirectory,filename,title=title,TextSize=TextSize)
    return

  def plotSQE(self,viewDirectory,lower=False,upper=False,TextSize=16):
    """
lower = lower limit for z-axis of plot.  Typically 1e-20 is good.
upper = upper limit for z-axis of plot.  Typically 1e-10 is good.

Displays a color intensity plot of S(Q,E), cropped with `lower` and
`upper` if requested.
"""
    sqe = expSqe(self)
    filename = 'sqe.png'
    plotSQE(sqe,viewDirectory,filename,lower=lower,\
                                        upper=upper,TextSize=TextSize)
    return

  def removeBackground(self,mqe,backgroundFrac,constantFrac):
    """
mqe            = Experimentally determined background in instance 
                   of expSqe
backgroundFrac = Fraction of background to be removed.  
                   0.95 typical.
constantFrac   = Fraction of counts to be removed as a constant 
                   background.  Ideally, should be 0.0, but may 
                   need to be larger in order to converge.

Background correction done in place
  sqe =  sqe - backgroundFrac mqe 
             - constantFrac sum_Q{sum_E{ S(E,Q) }} / len(q) len(e)
"""
    if mqe :
      self.sqe   -= mqe.sqe*backgroundFrac
      self.sqerr += mqe.sqerr*backgroundFrac*backgroundFrac
      pass
    C = nar(nar(self.sqe))*constantFrac/float(len(self.e)*len(self.q))
    self.sqe -= self.mask*C
    return

  def cropForCalc(self,cutoff,eStop,elasticCutAvg,longE=None,QHi=None,QLow=None): #CHANGE
    """  
cutoff = Cutoff of for elastic peak.                       [meV]
longE  = cutoff at high energy                             [meV]
eStop  = Arbitrary user defined cutoff at very high energy [meV]

  All in one data prep.  Performs cropE(eStop), cropQhi(longE), 
cropQlo(), removeElastic(cutoff), and DBify -- in that order and 
all in place.  Please see docs for those members for further info.
"""
    self.cropE(eStop)
    if longE:
        self.cropQhi(longE=longE)
        self.cropQlo(longE=longE)
    else:
        self.cropQhi(QHi=QHi)
        self.cropQlo(QLow=QLow)       
    self.removeElastic(cutoff,elasticCutAvg)
    self.DBify()
    return

  def DBify(self):
    """
Take the higher resolution data from E > 0, and apply detailed 
balance to set S(Q,-E) = exp(beta*E)*S(Q,E)
"""
    other = self.dbReverse()
    self.sqe[:,:self.zeroInd] = other.sqe[:,:other.zeroInd]
    self.updateMask()
    return

  def cropE(self,eStop):
    """
eStop  = Arbitrary user defined cutoff at very high energy [meV]

Remove all data with energy e > eStop.  Useful if there is 
unbearable noise at energies near the incident energy
"""
    if eStop and eStop < self.e[-1]:
      ind = numpy.argmin(self.e**2)
      if self.e[ind]**2 < TOL:
        self.e -= self.e[ind]
      else:
        raise("Zero not in energy array.")
      start = numpy.argmin( (self.e + eStop)**2 )
      stop  = numpy.argmin( (self.e - eStop)**2 ) + 1
      self.e     = self.e[start:stop]
      self.sqe   = self.sqe[:,start:stop]
      self.sqerr = self.sqerr[:,start:stop]
    self.updateMask()
    return

  def cropQlo(self,longE=None,QLow=None): #CHANGE
    """
Crop all momentum transfers Q for which there are Q,E pairs 
at low Q with no counts (probably due to kinematics of 
instrument)
"""
    if longE:
        longEInd = 0
        while self.e[longEInd] < longE:
          longEInd += 1
        start = 0
        while self.sqe[start][longEInd] == 0.0:
          start += 1
    else:
        closest=1000000
        closestInd=None
        for i,q in enumerate(self.q):
            diff = abs(q-QLow)
            if diff < closest:
                closest = diff
                closestInd = i
        start = closestInd
    self.q     = self.q[start:]
    self.sqe   = self.sqe[start:]
    self.sqerr = self.sqerr[start:]
    self.updateMask()
    return

  def cropQhi(self, longE=None, QHi=None): #CHANGE
    """
longE  = cutoff at high energy                       [meV]

Crop all momentum transfers Q for which there are Q,E pairs 
at high Q with no counts anywhere E < longE (probably due to 
kinematics of instrument).  Do this before fillS(), to keep
the high energy data all high-res.
"""
    if longE:
        longEInd = 0
        while self.e[longEInd] < longE:
          longEInd += 1
    #    start = 0
    # Why were these values not 0 for LRMECS data??
    #   while self.sqe[start][longEInd] == 0.0 \
    #      or self.sqe[start][longEInd] == self.sqe[0][longEInd]:
    #     start += 1
    #    stop = start
    #    while self.sqe[stop][longEInd] != 0.0 \
    #      and self.sqe[stop][longEInd] != self.sqe[-1][longEInd]:
    #      stop += 1
        stop = -1
        while self.sqe[stop][longEInd] == 0.0 \
          and self.sqe[stop][longEInd] == self.sqe[-1][longEInd]:
          stop -= 1
        stop += 1
    else:
        closest=1000000
        closestInd=None
        for i,q in enumerate(self.q):
            diff = abs(q-QHi)
            if diff < closest:
                closest = diff
                closestInd = i
        stop = closestInd
    self.q     = self.q[:stop]
    self.sqe   = self.sqe[:stop]
    self.sqerr = self.sqerr[:stop]
    self.updateMask()
    return

  def dbReverse(self):
    """ Returns S'(Q,E) = exp(beta*E)*S(Q,-E) as from detailed balance.  """
    sqe = self.sqe.tolist()
    sqerr = self.sqerr.tolist()
    for q in range(len(sqe)):
      sqe[q].reverse()
      sqerr[q].reverse()
    sqe = numpy.array(sqe)
    sqerr = numpy.array(sqerr)
    sqe *= numpy.exp(self.e*self.beta)
    sqerr *= ( numpy.exp(self.e*self.beta) )**2.0
    return expSqe(self.q,self.e,sqe,sqerr,self.T,self.M)

  def fillS(self):
    """
Use detailed balance to flesh out the data.  For all points 
S(Q,E) == 0 S(Q,-E) != 0, set S(Q,E) = exp(beta*E)*S(Q,-E)
"""
    other = self.dbReverse()
    for e in range(len(self.sqe)):
      for q in range(len(self.sqe[e])):
        if self.sqe[e,q] == 0.0:
          self.sqe[e,q] = other.sqe[e,q]
          self.sqerr[e,q] = other.sqerr[e,q]
    return

  def removeElastic(self,cutoff,elasticCutAvg):
    """
cutoff = Cutoff of for elastic peak.                       [meV]

Removes elastic peak from data out to `cutoff`, replacing with
a straight line with constant slope near e = 0.0
"""
    z = self.zeroInd
    stop = self.zeroInd
    while self.e[stop] < 0.0+cutoff:
      stop += 1
    start = self.zeroInd
    while self.e[start] > 0.0-cutoff:
      start -= 1
    middle = self.e/( 1.0 - numpy.exp( -1.0 * self.e * self.beta ) )
    middle *= self.se[stop:stop+elasticCutAvg].mean()/middle[stop]
    middle[z] = middle[z-1] + middle[z+1]
#-----------------------------------------------------------------------------
# The "11" below should probably be passed in by a user or determined on the
#   fly.  It says that 10 bins past the elastic cutoff should be used to 
#   determine how to weight the contribution of a given q to the low energy
#   inelastic scattering. 
#-----------------------------------------------------------------------------
#   norms = nar( self.sqe[:,start:stop] ,1 )    # weights by elastic line
#-----------------------------------------------------------------------------
    norms = nar( self.sqe[:,stop+1:stop+11] ,1 ) # weights by inelastic
#-----------------------------------------------------------------------------
    norms /= nar(norms)
    middle = numpy.outer(norms,middle)
    self.sqe[:,start:stop+1] = middle[:,start:stop+1]
# These error operation are totally BS.
    self.sqerr = self.sqerr.T
    self.sqerr[self.zeroInd:stop+1] += self.sqerr[stop+1]
    self.sqerr = self.sqerr.T
    self.sqerr[:,self.zeroInd] *= 4.0
    return

  def removeElasticStraight(self,cutoff):
    """
cutoff = Cutoff of for elastic peak.                       [meV]

Removes elastic peak from data out to `cutoff`, replacing with
a straight line to e = 0.0 
"""
    self.sqe = self.sqe.T
    self.sqerr = self.sqerr.T
    cut = self.zeroInd
    while self.e[cut] < 0.0+cutoff:
      cut += 1
    self.sqe[self.zeroInd:cut+1] = self.sqe[cut+1]
    self.sqerr[self.zeroInd:cut+1] += self.sqerr[cut+1]
    self.sqe = self.sqe.T
    self.sqerr = self.sqerr.T
    self.sqe[:,self.zeroInd] *= 2.0
    self.sqerr[:,self.zeroInd] *= 4.0
    return

  def norm2one(self):
    """ Normalize such that sum_Q{sum_E{ S(Q,E) } == 1.0 """
    norm = nar(nar(self.sqe))
    self.sqe /= norm
    self.sqerr /= norm*norm
    return

  def __init__(self,*args,**keys):
    """ 
Initialize from string holding filename, expSqe, or values 
for members using  _initFromFile, _initCopt, or 
_initFromVals respectively.
"""
    errmsg = "Invalid inputs for expSqe constructor: %s" % (args,)
    try: 
      self.cutRange=keys['cutRange']
    except:
      self.cutRange=(1e-20,1e20)
    if '__iter__' not in dir(self.cutRange) or len(self.cutRange)!=2:
      raise ValueError, 'cutRange must be a tuple of 2 real numbers: %s' % (self.cutRange,)
    if len(args) == 3 and args[0].__class__.__name__ == 'str':
      self._initFromFile(args[0],args[1],args[2])
      pass
    #    elif isinstance(args[0],expSqe):
    elif len(args)==1 and args[0].__class__.__name__ == 'expSqe':
      self._initCopy(args[0])
      pass
    elif len(args) == 6:
      self._initFromVals(*args)
      pass
    else:
      raise ValueError, errmsg
    # self._sanitize()
    self.updateMask()
    return

  def _initFromVals(self,q,e,sqe,sqerr,T,M):
    """  
Initialize from:
  T         = Temperature of measurement                [K]
  M         = Molecular weight of the sample            [kg] 
  e         = Energy array                              [meV]
  q         = Momentum transfer array                   [1/Angstroms]
  sqe       = S(Q,E)                                    [arb]
  sqerr     = Error from counting statistics for S(Q,E) [arb]
"""
    self.q     = numpy.array(q)
    self.e     = numpy.array(e)
    self.sqe   = numpy.array(sqe)
    self.sqerr = numpy.array(sqerr)
    self.T     = T
    self.M     = M
    return

  def _initCopy(self,other):
    """ Just copy data members from other.  """
    self.cutRange = other.cutRange
    self.q     = numpy.array(other.q)
    self.e     = numpy.array(other.e)
    self.sqe   = numpy.array(other.sqe)
    self.sqerr = numpy.array(other.sqerr)
    self.T     = other.T
    self.M     = other.M
    return


  def _dataFromSqehistPkl(self, filename):
    sqehist = pickle.load( open(filename, 'r' ) )
    Q = sqehist.axisFromName( 'Q' ).binCenters()
    E = sqehist.axisFromName( 'energy' ).binCenters()
    s = sqehist.data().storage().asNumarray().copy()
    se = sqehist.errors().storage().asNumarray().copy()
    return Q, E, s, se

  def _dataFromSqePkl(self, filename):
    Q,E,sT,seT = pickle.load(open(filename,'r'))
    return Q,E, numpy.array(sT).T, numpy.array(seT).T

  def _initFromFile(self,filename,T,M):
    """ 
Initialize from sqe.pkl file produced by DANSE reduction code, as
well as a temperature and a molecular weight.
"""
    try:
      Q,E,s,se = self._dataFromSqehistPkl( filename )
    except Exception, msg:
      debug.log( msg )
      Q,E,s,se = self._dataFromSqePkl( filename )
      pass
    self.q,self.e,self.sqe,self.sqerr = Q,E,s,se
    self.q     = numpy.array(self.q)
    self.e     = numpy.array(self.e)
    self.sqe   = numpy.array(self.sqe)
    self.sqerr = numpy.array(self.sqerr)
    self.T     = T
    self.M     = M*amu
    return

  def beta(self):
    """ placeholder for false member beta """
    pass 
  def _beta(self):
    """ returns 1/ k_b T """
    return 1.0/self.T/k_b/J2meV

  def zeroInd(self):
    """ placeholder for false member zeroInd """
    pass 
  def _zeroInd(self):
    """  returns index of e = 0.0 """
    debug.log('self.e=%s' % self.e)
    TOL = 1e-10
    i = numpy.argmin( self.e**2 )
    if self.e[i]**2 > TOL:
      raise("Zero not in energy array.")
    return i

  def de(self):
    """ placeholder for false member de """
    pass 
  def _de(self):
    """  returns energy increment """
    return self.e[1]-self.e[0]

  def shape(self):
    """ placeholder for false member shape """
    pass 
  def _shape(self):
    """ returns shape of sqe, ( len(q),len(e) ) """
    return self.sqe.shape

  def se(self):
    """ placeholder for false member se """
    pass 
  def _se(self):
    """ returns sum_Q{ S(Q,E) } """
    return nar(self.sqe)

  def sq(self):
    """ placeholder for false member sq """
    pass 
  def _sq(self):
    """ returns sum_E{ S(Q,E) } """
    return nar(self.sqe,1)

  def __getattribute__(self,attr):
    """
Implements the following false member functions:

  de        = energy increment              [meV]
  se        = S(E) = sum_Q{ S(Q,E) }        [arb]
  sq        = S(Q) = sum_E{ S(Q,E) }        [arb]
  beta      = 1 / k_b T                     [1/meV]
  zeroInd   = Index of e = 0                []
  shape     = Tuple with ( len(q),len(e) )  []
"""
    attributesFromFunction = [
      'beta',
      'zeroInd',
      'de',
      'shape',
      'se',
      'sq',
      ]
    if attr in attributesFromFunction:
      return getattr(self, '_%s' % attr)()
    
    res = object.__getattribute__(self,attr)
    return res

  def _sanitize(self):
    """sanitize data members
    The purpose is to make the energy axis an axis that is
    symmetric about e=0.
    """
    #e: energy axis.
    #assume it is evenly spaced
    #it is something like range(-E, E, de). it may not be exactly so, but very close.
    #we want to chop the e axis to
    # -E1, -E1+de, ..., E1
    e = self.e
    if min(e**2) > TOL: #  e[len(e)/2]**2 > TOL:
      C = numpy.argmin(e**2)
      raise ValueError,"zero is not in energy axis: %s" % e[C-3:C+3]
    de = e[1]-e[0]
    negativeE = e[0]
    absnegativeE = abs(negativeE)
    positiveE= e[-1]
    E1= min( positiveE, absnegativeE )
    nchop = (max(positiveE, absnegativeE) - E1)/de
    if nchop**2 > TOL:
      if absnegativeE > positiveE:
        self.e = e[nchop:]
        self.sqe = self.sqe[ :, nchop: ]
        self.sqerr = self.sqerr[ :, nchop: ]
      else:
        self.e = e[:-nchop]
        self.sqe = self.sqe[ :, :-nchop ]
        self.sqerr = self.sqerr[ :, :-nchop ]
        pass
      pass
    e = self.e
    assert (e[-1] + e[0])**2 < TOL, "insane energy axis: %s" % (e, )
    self.e -= self.e[len(self.e)/2]
    return


try:
  import journal
  debug = journal.debug( "multiphonon.expSqe" )
except ImportError:
  class _Debug:
    def log(self, msg): return #print msg
    line = log
  debug = _Debug()
  pass
#debug.activate()
