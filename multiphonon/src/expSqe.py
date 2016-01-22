#!/SNS/software/bin/python

from constants import *
import cPickle as cp
import numpy
nar = numpy.add.reduce

from sqePlot import *

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
    # !!! this is not robust: the resulting array shape depends on rounding errors !!!
    #newE     = numpy.arange(self.e[0]*eMul,self.e[-1]*eMul+self.de,self.de)
    # fix, which should work ok as long as de does not have too many meaningful decimals... :
    newE     = numpy.arange(int(numpy.round(self.e[0]*eMul,9) * 1e9),int(numpy.round(self.e[-1]*eMul+self.de,9)*1e9),int(numpy.round(self.de,9)*1e9)) / 1.0e9
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
    print self.q.shape,self.e.shape
    for q in range(len(self.q)):
      for e in range(len(self.e)):
        if self.sqe[q,e] == 0:
          mask[q,e] = 0
    self.mask = mask
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
    self.sqe   -= mqe.sqe*backgroundFrac
    self.sqerr += mqe.sqerr*backgroundFrac*backgroundFrac
    C = nar(nar(self.sqe))*constantFrac/float(len(self.e)*len(self.q))
    self.sqe -= self.mask*C
    return

  def cropForCalc(self,cutoff,longE,eStop,elasticCutAvg):
    """  
cutoff = Cutoff of for elastic peak.                       [meV]
longE  = Debye-cutoff at high energy                       [meV]
eStop  = Arbitrary user defined cutoff at very high energy [meV]

  All in one data prep.  Performs cropE(eStop), cropQhi(longE), 
cropQlo(), removeElastic(cutoff), and DBify -- in that order and 
all in place.  Please see docs for those members for further info.
"""
    self.cropE(eStop)
    self.cropQhi(longE)
    self.cropQlo(longE)
    self.removeElastic(cutoff,elasticCutAvg)
    self.DBify()
    return

  def cropQEForCalc(self,cutoff,Qmin,Qmax,eStop,elasticCutAvg):
    """  
cutoff = Cutoff of for elastic peak.                       [meV]
eStop  = Arbitrary user defined cutoff at very high energy [meV]
Qmin = min Q value to keep                                 [A-1]
Qmax = max Q value to keep                                 [A-1]

  All in one data prep.  Performs cropE(eStop), cropQhi(longE), 
cropQlo(), removeElastic(cutoff), and DBify -- in that order and 
all in place.  Please see docs for those members for further info.
"""
    self.cropE(eStop)
    self.cropQmin(Qmin)
    self.cropQmax(Qmax)
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
    if eStop:
      start = 0
      while self.e[start] < -eStop:
        start += 1
      stop = start
      while self.e[stop] <= eStop:
        stop += 1
      self.e     = self.e[start:stop]
      self.sqe   = self.sqe[:,start:stop]
      self.sqerr = self.sqerr[:,start:stop]
    self.updateMask()
    return

  def cropQlo(self,longE):
    """
Crop all momentum transfers Q for which there are Q,E pairs 
at low Q with no counts (probably due to kinematics of 
instrument)
"""
    longEInd = 0
    while self.e[longEInd] < longE:
      longEInd += 1
    start = 0
    while self.sqe[start][longEInd] == 0.0:
      start += 1
    self.q     = self.q[start:]
    self.sqe   = self.sqe[start:]
    self.sqerr = self.sqerr[start:]
    self.updateMask()
    return

  def cropQmin(self,Qmin):
    """Crop all momentum transfers Q below Qmin."""
    start = self.q[self.q < Qmin].shape[0]
    self.q     = self.q[start:]
    self.sqe   = self.sqe[start:]
    self.sqerr = self.sqerr[start:]
    self.updateMask()
    return

  

  def cropQhi(self,longE):
    """
longE  = Debye-cutoff at high energy                       [meV]

Crop all momentum transfers Q for which there are Q,E pairs 
at high Q with no counts anywhere E < longE (probably due to 
kinematics of instrument).  Do this before fillS(), to keep
the high energy data all high-res.
"""
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
    self.q     = self.q[:stop]
    self.sqe   = self.sqe[:stop]
    self.sqerr = self.sqerr[:stop]
    self.updateMask()
    return

  def cropQmax(self,Qmax):
    """Crop all momentum transfers Q larger than Qmax. """
    stop = self.q[self.q <= Qmax].shape[0]
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

  def __init__(self,*args):
    """ 
Initialize from string holding filename, expSqe, or values 
for members using  _initFromFile, _initCopt, or 
_initFromVals respectively.
"""
#    if isinstance(args[0],str):
    if args[0].__class__.__name__ == 'str':
      self._initFromFile(args[0],args[1],args[2])
#    elif isinstance(args[0],expSqe):
    elif args[0].__class__.__name__ == 'expSqe':
      self._initCopy(args[0])
    else:
      self._initFromVals(args[0],args[1],args[2],args[3],args[4],args[5])
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
    self.M     = M*amu
    return

  def _initCopy(self,other):
    """ Just copy data members from other.  """
    self.q     = numpy.array(other.q)
    self.e     = numpy.array(other.e)
    self.sqe   = numpy.array(other.sqe)
    self.sqerr = numpy.array(other.sqerr)
    self.T     = other.T
    self.M     = other.M
    return

  def _initFromFile(self,filename,T,M):
    """ 
Initialize from sqe.pkl file produced by DANSE reduction code, as
well as a temperature and a molecular weight.
"""
    self.q,self.e,self.sqe,self.sqerr = cp.load(open(filename,'r'))
    self.q     = numpy.array(self.q)
    self.e     = numpy.array(self.e)
    self.sqe   = numpy.array(self.sqe).T
    self.sqerr = numpy.array(self.sqerr).T
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
    i = 0
    while self.e[i] < 0.0:
      i += 1
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
    if attr == 'beta' :
      res = self._beta()
    elif attr == 'zeroInd' :
      res = self._zeroInd()
    elif attr == 'de' :
      res = self._de()
    elif attr == 'shape' :
      res = self._shape()
    elif attr == 'se' :
      res = self._se()
    elif attr == 'sq' :
      res = self._sq()
    else:
      res = object.__getattribute__(self,attr)
    return res
