#!/usr/bin/python


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# this is obsolete. getDOS.py is the one to use
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# --- Import stuff -------------------------------------------------------------
#import cPickle as cp
import pickle as cp

import sys, os, shutil

# *** LJ ***
import io as io
from expSqe import expSqe
from correction import *
from sqePlot import *
# **********

import numpy
nar = numpy.add.reduce


# *** LJ ***
# handle paths
import paths
# globals
magic_html = "mph.html"
# **********


# *** LJ ***
# make a method out of Max's getDOS.py
def getDOS(
    Data           = "test_cases/ni_0300/sqe.pkl",
    MT             = "test_cases/ni_0300/mqe.pkl",
    C_ms           = numpy.arange(0.0,2.0,0.1),
    backgroundFrac =    0.90,
    constantFrac   =    0.00,
    cutoff         =    8.5,
    elasticCutAvg  =    3,
    longE          =   40.0,
    cutRange       =  (1e-20,1e20),
    eStop          =   60.0 ,
    T              =  300.0,
    M              =   58.6934,
    N              =   10,
    Tol            =    1.0e-7,
    maxIter        =  50,
    interactive    = True,
    viewDirectory  = 'tmp',
    outputDir      = 'tmp',
    ):

    """
      This is the `main` function for finding a DOS and a multiphonon/
    multiple scattering correction from experimental scattering.

    user.py contains the user modifiable parameters.
    """

    # *** LJ ***
    # check output dirs
    _checkOutdir( viewDirectory )
    _checkOutdir( outputDir )

    # copy the magic html file
    shutil.copy( os.path.join(paths.data, magic_html ), viewDirectory )

    if interactive:
        # open a browser
        viewhtml = os.path.abspath( os.path.join( viewDirectory, magic_html ) )
        bthread = BrowserThread( 'file://' + viewhtml )
        bthread.start()

    # record time
    import time
    time1 = time.time()
    # **********


    # --- Prep S(Q,E)for calculation -----------------------------------------------
    sqe = expSqe(Data,T,M,cutRange=cutRange)

    # *** LJ ***
    if not MT: mqe = None
    else: mqe = expSqe(  MT,T,M,cutRange=cutRange)
    # **********

    if mqe: sqe.removeBackground(mqe,backgroundFrac,constantFrac)
    sqe.cropForCalc(cutoff,longE,eStop,elasticCutAvg)
    sqe.norm2one()
    sqe.expand(2.0)
    sqe0 = expSqe(sqe)
    
    sqe.plotSE(viewDirectory) 
    sqe.plotSQE(viewDirectory,lower=1e-30,upper=2.5e-4) 
    sqe.plotMask(viewDirectory) 
    
    # --- Fitting ------------------------------------------------------------------
    C_ms += 1.0  # This is a hack, until the internal rep of C_ms is changed.
    # ------------------------------------------------------------------------------
    res = getCorrectedScatter(sqe,C_ms,N,Tol,maxIter,interactive,vd=viewDirectory)
    sqeCalc,dosCalc,cmsCalc,res,C_ms,lsqSc,lsqMu,lsqSl,LSQ \
                                                           = getBestSol(sqe0,res,C_ms)
    
    dosCalc.plotDOS(viewDirectory)
    
    # --- Output to file and pickle ------------------------------------------------
    cp.dump((sqe0,C_ms,res,lsqSc,lsqMu,lsqSl,LSQ),\
            open( os.path.join( outputDir,"all.pkl") ,'wb'),-1)
    cp.dump((sqe0,sqeCalc,dosCalc,cmsCalc),\
         open( os.path.join( outputDir,"sol.pkl") ,'wb'),-1)
    # *** LJ ***
    saveDOSasHistogram( dosCalc, os.path.join( outputDir, "doshist.pkl") )
    # **********
    
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
    
    # --- `Interactive` Output -----------------------------------------------------
    SQE = expSqe(sqe0.q,sqe0.e,nar(sqeCalc),sqe0.sqerr,sqe0.T,sqe0.M,cutRange=cutRange)
    
    plotComp(sqe0,sqeCalc,viewDirectory)
    plotLSQ(C_ms,lsqSc,lsqMu,lsqSl,LSQ,viewDirectory)
    plotSQE(SQE,viewDirectory,'sqeCalc.png',title='S(Q,E) Calculated',\
            lower=1e-30,upper=2.5e-4) 
    return



def saveDOSasHistogram( dos, filename ):
    e = dos.e
    g = dos.g
    from histogram import makeHistogram
    name = 'dos'
    eaxis = 'Energy', e
    data = g
    import numpy
    errs = numpy.zeros( len(g ) )
    h = makeHistogram(name, [eaxis], data, errs )
    from pickle import dump
    dump( h, open(filename, 'w') )
    return



from threading import Thread
import webbrowser
class BrowserThread ( Thread ):

    def __init__(self, link):
        Thread.__init__(self)
        self.link = link
        return

    def run(self):
        print "open %s" % self.link
        webbrowser.open( self.link )
        return

    pass # end of BrowserThread


def _checkOutdir( dir ):
    if not os.path.exists(dir) :
        os.makedirs( dir )
    elif not os.path.isdir(dir):
        raise IOError , "%s is not a directory" % dir
    return
