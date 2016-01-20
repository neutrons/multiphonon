#!/usr/bin/python

#==============================================================================
# --- INPUT ---
#------------------------------------------------------------------------------
dosFile = 'tests/dos2sqe/ni.dos.300' 
M = 58.6934 * 1.66053873e-27  # ( kg )
T = 300.0                     # ( K )
N = 10
maxE = 200.00                 # ( meV )
minQ =  0.05                  # ( 1/Angstroms )
dQ   =  0.05                  # ( 1/Angstroms )
maxQ = 12.05                  # ( 1/Angstroms )
cutRange=(1e-20,1e20)         # (meV)
#==============================================================================

#---- Imports and module setup ------------------------------------------------
import os
import sys
mypath = os.path.abspath( os.path.split(__file__)[0] )
srcpath = os.path.join( mypath, 'src' )
sys.path.append( srcpath )
sys.path.append( os.path.join(os.curdir,'src' ) )
import multiphonon.io as io
from multiphonon import expSqe
from multiphonon import densityOfStates
from multiphonon import multiphonon
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
E = numpy.arange(-maxE,maxE+dE,dE)
Q = numpy.arange(minQ,maxQ,dQ)
fakeSqe = numpy.outer(Q,E)
sqe = expSqe.expSqe(Q,E,fakeSqe,fakeSqe,T,M)
e = numpy.arange(0.0,maxE+dE,dE)
dos = numpy.zeros(len(e))
dos[:len(g)] += g
dos = densityOfStates.densityOfStates(e,dos,cutRange=cutRange)
#------------------------------------------------------------------------------

#---- Get multiphonon scattering ----------------------------------------------
ANE = multiphonon.AthroughN(sqe,dos,N)
SNQ = multiphonon.SthroughN(sqe,dos,N)

SN = []
for i in range(len(SNQ)):
  SN.append( numpy.outer(SNQ[i],ANE[i]) )

SN = numpy.array(SN)
S = nar(SN)
#------------------------------------------------------------------------------

#---- Write to file -----------------------------------------------------------
cp.dump((Q,E,S,S),open("tmp/sqe.pkl",'w'))
sum = 0
for i in range(len(ANE)):
  io.write(E,ANE[i],"tmp/ane."+str(i+1))
  io.write(E,nar(SN[i]),"tmp/se."+str(i+1))

io.write(E, nar(S),"tmp/se.in")
#------------------------------------------------------------------------------

#---- Plot --------------------------------------------------------------------
for i in range(len(ANE)):
  G.replot(Gd(E,nar(SN[i]),with='l lw 5'))

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
