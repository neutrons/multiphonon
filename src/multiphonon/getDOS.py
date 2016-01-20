#!/usr/bin/python


"""
run method takes a set of parameters. 

this is an example of a parameter set:

class:
    #--- zro2 ----------------------------------------
    Data           = "sqe.pkl"
    MT             = None
    C_ms           = arange(0.0,1.0,0.1)
    backgroundFrac =    0.90 #ignore
    constantFrac   =    0.07
    cutoff         =    8.5
    elasticCutAvg  =    3
    longE          =   None#100.0
    QHi            = 10
    QLow           = 1
    eStop          =   145.0 
    T              =  315.0
    M              =   40.8
    N              =   5
    Tol            =    1.0e-7
    maxIter        =   50
    cutRange       =  [85.0, 120.0]

    #--- Output settings -----------------------------
    interactive    = True
    viewDirectory  = os.path.abspath('.')
    outputDir      = os.path.abspath('.')

"""



from .correction import *
from .sqePlot import *


def run(parameters):
    #--- Import stuff -------------------------------------------------------------
    import time
    time1 = time.time()

    import cPickle as cp

    import sys
    import os
    if not os.path.exists(parameters.viewDirectory):
        os.makedirs(parameters.viewDirectory)
    if not os.path.exists(parameters.outputDir):
        os.makedirs(parameters.outputDir)        

    from . import io
    from .expSqe import expSqe

    import numpy
    nar = numpy.add.reduce

    #--- Prep S(Q,E)for calculation -----------------------------------------------
    sqe = expSqe(parameters.Data,parameters.T,parameters.M,cutRange=parameters.cutRange)
    if parameters.MT is None:
        mqe = None
    else:
        mqe = expSqe(parameters.MT,parameters.T,parameters.M,cutRange=parameters.cutRange)

    sqe.removeBackground(mqe,parameters.backgroundFrac,parameters.constantFrac)
    if parameters.longE:
        sqe.cropForCalc(parameters.cutoff,parameters.eStop,parameters.elasticCutAvg,longE=parameters.longE)
    else:
        sqe.cropForCalc(parameters.cutoff,parameters.eStop,parameters.elasticCutAvg,QHi=parameters.QHi,QLow=parameters.QLow)
    sqe.norm2one()
    sqe.expand(2.0)
    sqe0 = expSqe(sqe)

    sqe.plotSE(parameters.viewDirectory) 
    sqe.plotSQE(parameters.viewDirectory,lower=1e-30,upper=2.5e-4) 
    sqe.plotMask(parameters.viewDirectory) 

    #--- Fitting ------------------------------------------------------------------
    parameters.C_ms += 1.0  # This is a hack, until the internal rep of C_ms is changed.
    #------------------------------------------------------------------------------
    res = getCorrectedScatter(sqe,parameters.C_ms,parameters.N,parameters.Tol,parameters.maxIter,parameters.interactive,vd=parameters.viewDirectory)
    try:
        sqeCalc,dosCalc,cmsCalc,res,parameters.C_ms,lsqSc,lsqMu,lsqSl,LSQ = getBestSol(sqe0,res,parameters.C_ms)

        dosCalc.plotDOS(parameters.viewDirectory)

        #--- Output to file and pickle ------------------------------------------------

        cp.dump((sqe0,parameters.C_ms,res,lsqSc,lsqMu,lsqSl,LSQ),\
                 open( os.path.join( parameters.outputDir,"all.pkl") ,'wb'),-1)
        cp.dump((sqe0,sqeCalc,dosCalc,cmsCalc),\
                 open( os.path.join( parameters.outputDir,"sol.pkl") ,'wb'),-1)

        f = open( os.path.join( parameters.outputDir,"C_ms" ),'w')
        f.write( "C_ms = %lf\n" % (parameters.C_ms[numpy.argmin( numpy.array(LSQ)**2 )]-1.0) )
        f.close()
        io.write(dosCalc.e,dosCalc.g,         os.path.join( parameters.outputDir,"Dos"      ) )
        io.write(dosCalc.e,dosCalc.gz,        os.path.join( parameters.outputDir,"Dos.z"    ) )
        io.write(sqe0.e,sqe0.se,              os.path.join( parameters.outputDir,"Se.exp"   ) )
        io.write(sqe0.e,nar(nar(sqeCalc)),    os.path.join( parameters.outputDir,"Se.clc"   ) )
        io.write(sqe0.e,nar(nar(sqeCalc[1:])),os.path.join( parameters.outputDir,"Multi.clc") )
        io.write(sqe0.e,nar(nar(sqeCalc[1:]))/(cmsCalc),\
                                              os.path.join( parameters.outputDir,"Mph.clc"  ) )
        io.write(sqe0.e,(cmsCalc-1.0)*nar(nar(sqeCalc[1:]))/cmsCalc\
                                             ,os.path.join( parameters.outputDir,"Msc.clc"  ) )

        #--- `Interactive` Output -----------------------------------------------------
        SQE = expSqe(sqe0.q,sqe0.e,nar(sqeCalc),sqe0.sqerr,sqe0.T,sqe0.M,cutRange=parameters.cutRange)

        plotComp(sqe0,sqeCalc,parameters.viewDirectory)
        plotLSQ(parameters.C_ms,lsqSc,lsqMu,lsqSl,LSQ,parameters.viewDirectory)
        plotSQE(SQE,parameters.viewDirectory,'sqeCalc.png',title='S(Q,E) Calculated',\
                lower=1e-30,upper=2.5e-4) 
    except:
        pass

    cp.dump((sqe0,parameters.C_ms,res),\
             open( os.path.join( parameters.outputDir,"allCalcs.pkl") ,'wb'),-1)
    
    return
