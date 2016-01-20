#!/usr/bin/python
#---docstring------------------------------------------------------------------
"""
  This is the `main` function for finding a DOS and a multiphonon/
multiple scattering correction from experimental scattering.

user.py contains the user modifiable parameters.
"""
#---end-docstring--------------------------------------------------------------

#--- Import stuff -------------------------------------------------------------
import time
time1 = time.time()

import cPickle as cp

import sys
import os
mypath = os.path.abspath( os.path.split(__file__)[0] )
srcpath = os.path.join( mypath, 'src' )
sys.path.append( srcpath )
sys.path.append( os.path.join(os.curdir,'src' ) )

import multiphonon.io as io
from user import *
from multiphonon.expSqe import expSqe
from multiphonon.correction import *
from multiphonon.sqePlot import *

import numpy
nar = numpy.add.reduce

#--- Prep S(Q,E)for calculation -----------------------------------------------
sqe = expSqe(Data,T,M,cutRange=cutRange)
mqe = expSqe(  MT,T,M,cutRange=cutRange)

sqe.removeBackground(mqe,backgroundFrac,constantFrac)
sqe.cropForCalc(cutoff,longE,eStop,elasticCutAvg)
sqe.norm2one()
sqe.expand(2.0)
sqe0 = expSqe(sqe)

sqe.plotSE(viewDirectory) 
sqe.plotSQE(viewDirectory,lower=1e-30,upper=2.5e-4) 
sqe.plotMask(viewDirectory) 

#--- Fitting ------------------------------------------------------------------
C_ms += 1.0  # This is a hack, until the internal rep of C_ms is changed.
#------------------------------------------------------------------------------
res = getCorrectedScatter(sqe,C_ms,N,Tol,maxIter,interactive,vd=viewDirectory)
sqeCalc,dosCalc,cmsCalc,res,C_ms,lsqSc,lsqMu,lsqSl,LSQ \
                                                    = getBestSol(sqe0,res,C_ms)

dosCalc.plotDOS(viewDirectory)

#--- Output to file and pickle ------------------------------------------------
cp.dump((sqe0,C_ms,res,lsqSc,lsqMu,lsqSl,LSQ),\
         open( os.path.join( outputDir,"all.pkl") ,'wb'),-1)
cp.dump((sqe0,sqeCalc,dosCalc,cmsCalc),\
         open( os.path.join( outputDir,"sol.pkl") ,'wb'),-1)

f = open( os.path.join( outputDir,"C_ms" ),'w')
f.write( "C_ms = %lf\n" % (C_ms[numpy.argmin( numpy.array(LSQ)**2 )]-1.0) )
f.close()
io.write(dosCalc.e,dosCalc.g,         os.path.join( outputDir,"Dos"      ) )
io.write(dosCalc.e,dosCalc.gz,        os.path.join( outputDir,"Dos.z"    ) )
io.write(sqe0.e,sqe0.se,              os.path.join( outputDir,"Se.exp"   ) )
io.write(sqe0.e,nar(nar(sqeCalc)),    os.path.join( outputDir,"Se.clc"   ) )
io.write(sqe0.e,nar(nar(sqeCalc[1:])),os.path.join( outputDir,"Multi.clc") )
io.write(sqe0.e,nar(nar(sqeCalc[1:]))/(cmsCalc),\
                                      os.path.join( outputDir,"Mph.clc"  ) )
io.write(sqe0.e,(cmsCalc-1.0)*nar(nar(sqeCalc[1:]))/cmsCalc\
                                     ,os.path.join( outputDir,"Msc.clc"  ) )

#--- `Interactive` Output -----------------------------------------------------
SQE = expSqe(sqe0.q,sqe0.e,nar(sqeCalc),sqe0.sqerr,sqe0.T,sqe0.M,cutRange=cutRange)

plotComp(sqe0,sqeCalc,viewDirectory)
plotLSQ(C_ms,lsqSc,lsqMu,lsqSl,LSQ,viewDirectory)
plotSQE(SQE,viewDirectory,'sqeCalc.png',title='S(Q,E) Calculated',\
        lower=1e-30,upper=2.5e-4) 
