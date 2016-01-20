#!/usr/bin/python

import sys
import os
mypath = os.path.abspath( os.path.split(__file__)[0] )
srcpath = os.path.join( mypath, 'src' )
sys.path.append( srcpath )
sys.path.append( os.path.join(os.curdir,'src' ) )
import io

e0,d0 = io.load("dos")
D0 = d0.copy()
D0[104:124] = 0
R0 = D0.copy()

import random
for i in range(104,124):
  R0[i] += 0.02*(random.random() - 0.5)

import Gnuplot
g = Gnuplot.Gnuplot()
gd = Gnuplot.Data
g('set grid')
# g.plot(gd(e0,d0,with='l lw 5'))
# g.replot(gd(e0,D0,with='l lw 5'))
# g.replot(gd(e0,R0,with='l lw 5'))

import densityOfStates
d = densityOfStates.densityOfStates(e0,d0)
D = densityOfStates.densityOfStates(e0,D0)
R = densityOfStates.densityOfStates(e0,R0)

# g.replot(gd(d.e,d.g,with='l lw 3'))
# g.replot(gd(D.e,D.g,with='l lw 3'))
# g.replot(gd(R.e,R.g,with='l lw 3'))

d = densityOfStates.densityOfStates(e0,d0,cutRange=(30,40))
D = densityOfStates.densityOfStates(e0,D0,cutRange=(32,40))
R = densityOfStates.densityOfStates(e0,R0,cutRange=(32,40))
G = densityOfStates.densityOfStates(e0,R0,cutRange=(21,21))

g.plot(gd(d.e,d.gz,with='l lw 3'))
g.replot(gd(D.e,D.gz,with='l lw 3'))
g.replot(gd(R.e,R.gz,with='l lw 3'))
g.replot(gd(G.e,G.gz,with='l lw 3'))
print "The red dos should look like nickel...      cutoff 36.5 meV"
print "The green dos should have a bandgap...      cutoff 36.5 meV"
print "The blue dos should have a noisy bandgap... cutoff 36.5 meV"
print "The magenta dos should look like crap...    cutoff 21.0 meV"
raw_input("Press <Enter> to close up shop...")
