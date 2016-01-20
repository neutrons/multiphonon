#!/usr/bin/python

import cPickle as cp
import numpy   
nar = numpy.add.reduce
import Gnuplot
g = Gnuplot.Gnuplot()
gd = Gnuplot.Data

q,e,sqe,sqerr = cp.load(open("tmp/sqe.pkl",'r'))

g('set grid')
g.plot(gd(e,nar(sqe),with='l lw 3'))

raw_input("Hit <Enter> to close up shop...")
