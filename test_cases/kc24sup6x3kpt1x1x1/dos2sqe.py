#!/usr/bin/python

#==============================================================================
# --- INPUT ---
#------------------------------------------------------------------------------
dosFile = 'meV_phon6x3FineMeshVecs1x1x1.dens'
M = 2.02 * 1.66053873e-27  # ( kg )
T = 30.0                     # ( K )
N = 10
maxE =  100.0                  # ( meV )
minQ =  0.05                  # ( 1/Angstroms )
dQ   =  0.05                  # ( 1/Angstroms )
maxQ = 12.05                  # ( 1/Angstroms )
cutRange=(50,1e20) # Bounds on high energy cutoff

#==============================================================================

#---- Imports and module setup ------------------------------------------------
from math import floor,ceil
import os
import sys
mypath = os.path.abspath( os.path.split(__file__)[0] )
#srcpath = os.path.join( mypath, 'src' )
#sys.path.append( srcpath )
#sys.path.append( os.path.join(os.curdir,'src' ) )
import io
import expSqe
import densityOfStates
import multiphonon
import cPickle as cp
import numpy
nar = numpy.add.reduce
import Gnuplot
G = Gnuplot.Gnuplot()
Gd = Gnuplot.Data
G('set grid')
#------------------------------------------------------------------------------

#---- Setup objects -----------------------------------------------------------
e,g = io.load(dosFile)
dE = e[1] - e[0]
E = numpy.arange(floor(-maxE/dE)*dE, (ceil(maxE/dE)+1)*dE, dE)
#if e[0]==0.0: #dos contains 0 point
#    E = numpy.concatenate((-1*e[::-1],e[1:]))
#else: #dos does not contain 0 point
#    E = numpy.concatenate((numpy.append(-1*e[::-1],0.0),e))
Q = numpy.arange(minQ, maxQ, dQ)
fakeSqe = numpy.outer(Q,E)
sqe = expSqe.expSqe(Q,E,fakeSqe,fakeSqe,T,M,cutRange=cutRange)
e = numpy.arange(0.0, maxE+dE, dE)
dos = numpy.zeros(len(e))
if len(g) <= len(dos):
  dos[:len(g)] += g
else:
  dos += g[:len(dos)]

dos = densityOfStates.densityOfStates(e,dos,cutRange=cutRange)
#------------------------------------------------------------------------------

#---- Get multiphonon scattering ----------------------------------------------
ANE = multiphonon.AthroughN(sqe,dos,N)
#for i in range(len(ANE)):
#    print 'ane',ANE[i]
SNQ = multiphonon.SthroughN(sqe,dos,N)
#for i in range(len(SNQ)):
#    print SNQ[i]
    
SN = []
for i in range(len(SNQ)):
  SN.append( numpy.outer(SNQ[i],ANE[i]) )

SN = numpy.array(SN)
S = nar(SN)
#------------------------------------------------------------------------------

#---- Write to file -----------------------------------------------------------
cp.dump((Q,E,S,S),open("sqe.pkl",'w'))
sum = 0
for i in range(len(ANE)):
  io.write(E,ANE[i],"se."+str(i+1))
io.write(E, nar(S),"se.in")
#

#------------------------------------------------------------------------------

#---- Plot --------------------------------------------------------------------
for i in range(len(ANE)):
  G.replot(Gd(E,ANE[i],with='l lw 5'))

raw_input("Press <Enter> to continue...")
#------------------------------------------------------------------------------

#==============================================================================
# --- Notes ---
#------------------------------------------------------------------------------
# 1) There is a strong tendency to have numerical noise and instability near
#      E = 0 for the 1-phonon spectrum.  We may need to take care of this. One 
#      thing that helps is fitting DOS to C*E^2 (C a constant) at low E. This 
#      may even be sufficient.
# 2) Code is slow
#==============================================================================
