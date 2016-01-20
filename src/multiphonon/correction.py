#!/usr/bin/python
import sys
#-----------------------------------------------------------------
#----For outputing named files---------
#-----------------------------------------------------------------
import os
import sys
#-----------------------------------------------------------------

#---docstring------------------------------------------------------------------
"""
  These two functions implement finding the best DOS for a fixed contribution 
from multiple scattering, and selecting one of those DOSs as the overall
optimum solution.  

getCorrectedScatter(...) performs the former.
         getBestSol(...) performs the latter.
"""
#---end-docstring--------------------------------------------------------------

from copy import deepcopy as dc
import numpy
nar = numpy.add.reduce

import mfit
from expSqe import expSqe
from densityOfStates import densityOfStates as Dos
from sqe2dos import sqe2dos
from multiphonon import getSQE
from sqePlot import plotSQE, plotComp

def getCorrectedScatter(sqe,C_ms,N,Tol,maxIter,interactive,vd=False):
#---docstring------------------------------------------------------------------
  """
sqe  = experimental S(Q,E) in instance of class expSqe
C_ms = list of multipliers
        C_ms[i]*S_2+(Q,E) = S_2+(Q,E) + multiple scattering
N    = number of terms to evaluate in multiphonon expansion 
Tol  = convergence at iteration N+1 when (g_{N+1}(E) - g_N(E))^2 < Tol
interactive = if True, print information while iterating 

Returns a list `res` of self consistent solutions for the DOS from the 
scattering, one for each value in C_ms.   
        res[i] = [ S(Q,E), dos, C_ms[i] ]
        where S(Q,E) = numpy.array{ S_1(Q,E), S_2(Q,E), ..., S_N(Q,E) }
"""
#---end-docstring--------------------------------------------------------------
  sqe0 = expSqe(sqe)
  res = []
  i = 0
  tot = len(C_ms)
  cmsStrLen = 0
#-----------------------------------------------------------------
#----For outputing named files---------
#-----------------------------------------------------------------
  for x in C_ms:
    if len(str(x)) > cmsStrLen:
      cmsStrLen = len(str(x))
#-----------------------------------------------------------------
  for x in C_ms:
    i += 1
    if interactive:
      print " "
      print "--- Multiple scattering Factor "+str(i)+" of "+str(tot)\
           +" -------------------------------"
      print "Dos converged to ... "
      sys.stdout.flush()
    dos = sqe2dos(sqe0)
    dos0 = Dos(dos.e,dos.g,cutRange=sqe.cutRange)
    another = True
    iter = 0
    while another == True:
      SQE  = getSQE(sqe0,dos,N,x)
      sqe.sqe = sqe0.sqe - nar(SQE[1:])
      dos = sqe2dos(sqe)
      if nar( (dos.gz-dos0.gz)**2.0 ) > Tol and iter < maxIter:
        print "Penalty = %le" %nar( (dos.gz-dos0.gz)**2 )
        sys.stdout.flush()
        dos0 = Dos(dos.e,dos.g,cutRange=sqe.cutRange)
        iter += 1
      else:
        if iter == maxIter:
          print "NOT CONVERGED AFTER %d ITERATIONS" % iter
        print "Final penalty: %le" % nar( (dos.gz-dos0.gz)**2 )
        sys.stdout.flush()
        another = False
    res.append( [SQE, dos , x] )
    if interactive:
      plotSQE(expSqe(sqe0.q,sqe0.e,nar(res[-1][0]),sqe0.sqerr,sqe0.T,sqe0.M),\
           vd,'sqeCalc.png',title='S(Q,E) Calculated at '+str(x),lower=1e-30,\
           upper=2.5e-4)
      plotComp(sqe0,res[-1][0],vd)
      res[-1][1].plotDOS(vd)
#-----------------------------------------------------------------
#----For outputing named files---------
#------ This probably doesn't work in windows, b/c "cp" ---------
#-----------------------------------------------------------------
      cmsStr = str(x)
      while len(cmsStr) < cmsStrLen:
        cmsStr += '0'
      os.system("cp " + os.path.join(vd,"dos.png") + " " + \
                        os.path.join(vd,"dos-" + cmsStr + ".png") )
      os.system("cp " + os.path.join(vd,"sqeCalc.png") + " " + \
                        os.path.join(vd,"sqeCalc-" + cmsStr + ".png") )
      os.system("cp " + os.path.join(vd,"seComp.png") + " " + \
                        os.path.join(vd,"seComp-" + cmsStr + ".png") )
#-----------------------------------------------------------------
      print " --- "
      print " "
  return res

def getBestSol(sqe,Res,c_ms):
#---docstring------------------------------------------------------------------
  """
sqe  = experimental S(Q,E) in instance of class expSqe
c_ms = list of multipliers
        C_ms[i]*S_2+(Q,E) = S_2+(Q,E) + multiple scattering
Res  = output from getCorrectedScatter() above.
        res[i] = [ S(Q,E), dos, C_ms[i] ]
        where S(Q,E) = numpy.array{ S_1(Q,E), S_2(Q,E), ..., S_N(Q,E) }

Returns the "optimal values" out of `res` and some fitting info.:
sqeCalc = S(Q,E) = numpy.array{ S_1(Q,E), S_2(Q,E), ... S_N(Q,E) }
dosCalc = instance of class densityOfStates
cmsCalc = cmsCalc*S_2+(Q,E) = S_2+(Q,E) + multiple scattering
res     = shortened list of results *    
C_ms    = shortened list of multipliers * 
lsqSc   = cumulative of least squared penalty of fit to scattering
lsqMu   = cumulative of least squared penalty of line fit to high E 
          noise (after cutoff) and multiphonon/multiple scattering **
lsqSl   = cumulative of least squared penalty of slope of line fit to 
          high E noise (after cutoff) and slope of line fit 
          multiphonon/multiple scattering **
LSQ     = average of 3 preceding cumulatives

Notes:  * dosses with no cutoffs are rejected.
       ** These last two `lsq` criterion are related, but not the same.
"""
#---end-docstring--------------------------------------------------------------
  res = dc(Res)
  C_ms = dc(c_ms)
  lsqSc = numpy.zeros(len(res),'d') + numpy.inf 
  lsqMu = numpy.zeros(len(res),'d') + numpy.inf 
  lsqSl = numpy.zeros(len(res),'d') + numpy.inf
  for i in range(len(res)):
    try:
      zeroCut   = sqe.zeroInd + 1
      sqeCut    = sqe.zeroInd+res[i][1].cutoffInd
      slopeCut  = sqe.slopeCut()
      sqeLin    = sqe.se[sqeCut:slopeCut]
      mulSqeLin = nar(nar(res[i][0][1:]))[sqeCut:slopeCut]
      eLin      = sqe.e[sqeCut:slopeCut]
      sqeSlope,inter =                     mfit.poly(eLin,sqeLin   ,1)
      mulSlope,inter =                     mfit.poly(eLin,mulSqeLin,1)
      line           = mfit.poly_of_x(eLin,mfit.poly(eLin,sqeLin   ,1) )
      lsqSl[i] =            (sqeSlope-mulSlope)**2.0
      lsqMu[i] =       nar( (mulSqeLin - line )**2.0 /float(len(line)) )
      lsqSc[i] =  nar( nar( (sqe.sqe - nar(res[i][0]) )**2.0 ) )
    except:
      pass

  start = 0
  while start<len(lsqSc) and \
     (numpy.isnan(lsqSc[start]) or numpy.isinf(lsqSc[start]) \
     or numpy.isnan(lsqMu[start]) or numpy.isinf(lsqMu[start]) \
     or numpy.isnan(lsqSl[start]) or numpy.isinf(lsqSl[start])):
       start += 1

  C_ms  =  C_ms[start:]
  res   =   res[start:]
  lsqSc = lsqSc[start:]
  lsqMu = lsqMu[start:]
  lsqSl = lsqSl[start:]
  lsqSc_copy = numpy.array(lsqSc)
  lsqMu_copy = numpy.array(lsqMu)
  lsqSl_copy = numpy.array(lsqSl)
  numBetter = lambda x,c : len(filter(lambda y : y < 0.98*x,c) )
  for i in range(len(C_ms)):
    lsqSc_copy[i] = numBetter(lsqSc[i],lsqSc)
    lsqMu_copy[i] = numBetter(lsqMu[i],lsqMu)
    lsqSl_copy[i] = numBetter(lsqSl[i],lsqSl)
  lsqSc= numpy.array(lsqSc_copy )
  lsqMu= numpy.array(lsqMu_copy )
  lsqSl= numpy.array(lsqSl_copy )
  
  LSQ = (lsqSc + lsqMu + lsqSl)/3.0

  best = LSQ.argmin()
  sqeCalc = res[best][0]
  dosCalc = res[best][1]
  cmsCalc = res[best][2]
  return sqeCalc,dosCalc,cmsCalc,res,C_ms,lsqSc,lsqMu,lsqSl,LSQ
