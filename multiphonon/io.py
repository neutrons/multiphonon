#!/usr/bin/python
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
  fRaw = fi.readlines()
  f=[]
  fi.close()
  for i in range(len(fRaw)):
    fRaw[i] = fRaw[i].split()
    if fRaw[i]==[]:continue # do this if at the end of the file and no more numbers
    #print fRaw[i]
    f.append([float(fRaw[i][0]),float(fRaw[i][1])])
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

