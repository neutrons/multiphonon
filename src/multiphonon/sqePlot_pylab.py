#!/usr/bin/python

import numpy, os
nar = numpy.add.reduce


#import pylab
import matplotlib
matplotlib.interactive(False)
matplotlib.use("Agg")
from matplotlib import pylab

def TexInstalled():
  "test whether tex is usable"
  pylab.rcParams['text.usetex'] = 1
  pylab.rcParams['backend'] = 'ps'
  try:
    pylab.plot( [1,2,3])
    pylab.xlabel( '$\alpha$' )
    import tempfile
    pylab.savefig( tempfile.mktemp() )
  except:
    print 'latex not installed'
    return 0
  return 1


#use latex to create math texts
uselatex = TexInstalled()
#set figure size to 480X480
points_per_inch = 72.27
size_pt = 480
size = size_pt/points_per_inch
fig_size = size, size
params = {
  'backend': 'ps',
  'axes.labelsize': 20,
  'axes.titlesize': 22,
  'text.fontsize': 20,
  'xtick.labelsize': 16,
  'ytick.labelsize': 16,
  'text.usetex': uselatex,
  'figure.figsize': fig_size}
pylab.rcParams.update( params )


def plotLSQ(C_ms,lsqSc,lsqMu,lsqSl,LSQ,viewDirectory,TextSize=16):
  C_MS = C_ms - 1.0
  #480x480
  myfile = os.path.join(viewDirectory,'lsq.png')
  title='Cumulative LSQ Penalties' 
  red = 'S(Q,E)'
  green = 'high E scatter'
  blue = 'slope of high E scatter'
  xlabel = r"$C_{ms}$ [unitless]"
  ylabel = "Cumulative Penalty [unitless]"
  pylab.clf()
  pylab.plot( C_MS, lsqSc, 'r-', linewidth=5 )
  pylab.plot( C_MS, lsqMu, 'g-', linewidth=5 )
  pylab.plot( C_MS, lsqSl, 'b-', linewidth=5 )
  pylab.grid( 1 )
  pylab.legend( (red, green, blue), loc="upper left" )
  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title(title)
  pylab.savefig( myfile )
  
  myfile = os.path.join(viewDirectory,'lsq_f.png')
  pylab.clf()
  title='Final Cumulative LSQ Penalty'
  pylab.plot( C_MS,LSQ, 'b-', linewidth = 5)
  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title( title )
  pylab.grid(1)
  pylab.savefig( myfile )
  return

def plotComp(sqe,sqeCalc,viewDirectory,Erange=False,Srange=False,TextSize=16):
  myfile = os.path.join(viewDirectory,'seComp.png')
  title = 'S(E)' 
  red   = 'experiment'
  blue  = 'calculation'
  green = 'calculated multiphonon'
  if Erange: xlim(Erange)
  if Srange: ylim(Srange)

  xlabel =  "E [meV]"
  ylabel =  "S(E) [arb]"

  pylab.clf()
  pylab.plot( sqe.e, sqe.se, 'r-', linewidth=3 )
  pylab.plot( sqe.e, nar(nar(sqeCalc[1:])), 'g-', linewidth=3 )
  pylab.plot( sqe.e, nar(nar(sqeCalc)), 'b-', linewidth=3 )

  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title( title )
  pylab.legend( (red, green, blue), loc="upper left" )
  pylab.grid(1)
  pylab.savefig( myfile )
  return

def plotGE(dos,viewDirectory, Erange=False, Srange=False,TextSize=16):
  myfile = os.path.join(viewDirectory,'dos.png')
  if Erange: xlim(Erange)
  if Srange: ylim(Srange)
  title = "g(E)"
  xlabel = "E [meV]"
  ylabel = "g(E) [1/meV]"

  red = "with noise"
  blue = "zeroed"

  pylab.clf()
  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title( title )
  pylab.grid(1)

  pylab.plot( dos.e, dos.g, 'r-', linewidth=3 )
  pylab.plot( dos.e, dos.gz, 'b-', linewidth=3 )

  pylab.legend( (red, blue), loc="upper right" )
  pylab.savefig( myfile )
  return

def plotSE(sqe,viewDirectory, Erange=False, Srange=False,TextSize=16):
  myfile = os.path.join(viewDirectory,'se.png')
  title = "S(E)"
  xlabel = "E [meV]"
  ylabel = "S(E) [arb]"
  if Erange: xlim(Erange)
  if Srange: ylim(Srange)

  pylab.clf()
  pylab.axes( (0.15, 0.1, 0.8, 0.8 ) )
  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title( title )
  pylab.grid(1)

  pylab.plot( sqe.e, sqe.se, 'r-', linewidth=3 )

  pylab.savefig( myfile )
  return

def plotSQE(sqe,viewDirectory,filename,title="S(Q,E)",lower=False,\
                                                      upper=False,TextSize=16):

  pylab.clf()
  pylab.axes( (0.15, 0.1, 0.8, 0.8 ) )
  
  if upper:
    for q in range(len(sqe.q)):
      for e in range(len(sqe.e)):
        if sqe.sqe[q,e] > upper:
          sqe.sqe[q,e] = upper
  if lower:
    for q in range(len(sqe.q)):
      for e in range(len(sqe.e)):
        if sqe.sqe[q,e] < lower:
          sqe.sqe[q,e] = lower
  myfile = os.path.join(viewDirectory,filename)

  
  x = sqe.q; y = sqe.e; z = numpy.transpose(sqe.sqe)
  X,Y = pylab.meshgrid(x,y)
  image = pylab.pcolor( X,Y, z, shading="flat")

  ylabel = "E [meV]"
  xlabel = "Q [1/Angstroms]"

  pylab.xlim( x[0], x[-1] )
  pylab.ylim( y[0], y[-1] )
  
  pylab.xlabel( xlabel )
  pylab.ylabel( ylabel )
  pylab.title( title )
  pylab.colorbar()

  pylab.savefig( myfile )
  return

