#!/SNS/software/bin/python
"""
Some functions for input and output to and from file.
"""

import time
import numpy
nar = numpy.add.reduce

def load(filename):
  """ Reads two column, space separated ASCII file `filename` into numpy e 
and d. """
  fi = open(filename,'r')
  f = fi.readlines()
  fi.close()
  for i in range(len(f)):
    f[i] = f[i].split()
    for j in range(len(f[i])):
      f[i][j] = float(f[i][j])
  f = numpy.array(f)
  e = numpy.array( f[:,0] )
  d = numpy.array( f[:,1] )
  return e,d

def write(e,d,filename):
  """ Writes two column, space separated ASCII file `filename`, with e in the 
first column and d in the second column. """
  F = open(filename,'w')
  for i in range(len(e)):
    F.write( str( e[i] ) + " " + str( d[i] ) + "\n" )
  F.close()
  return

