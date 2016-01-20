#!/usr/bin/python


#engine = "gnuplot"
engine = "pylab"

if engine == "pylab":
  from sqePlot_pylab import *
elif engine == "gnuplot":
  from sqePlot_gnuplot import *
else:
  raise NotImplementedError

