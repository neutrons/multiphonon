#!/usr/bin/python

import sys
import os
import numpy
import cPickle as cp
Q,E,S,crap = cp.load(open("tmp/sqe.pkl",'r'))

def strToInd(s,X):
  return numpy.argmin( ( X - float(s) )**2 )

try:
  Cb = sys.argv[1]
  Ce = sys.argv[2]
except:
  Cb =  ''
  Ce =  ''

try:
  Eb = strToInd(sys.argv[3],E)
  Ee = strToInd(sys.argv[4],E)
except:
  Eb = 0      
  Ee = len(E)

try:
  Qb = strToInd(sys.argv[5],Q)
  Qe = strToInd(sys.argv[6],Q)
except:
  Qb = 0     
  Qe = len(Q)

import Gnuplot
G = Gnuplot.Gnuplot()
GD = Gnuplot.GridData
G('set pm3d')
G('set pm3d map')
G('set yrange ['+str(E[Eb])+':'+str(E[Ee-1])+']')
G('set xrange ['+str(Q[Qb])+':'+str(Q[Qe-1])+']')
G('set tics out')
G('set mxtics 2')
G('set mytics 2')
G("set palette file 'colors.gp'")
G('set size square')
G("set encoding iso_8859_1")
G("set xlabel 'Q [ \305^{-1} ]'")
G("set ylabel 'E [ meV ]'")
G("set title 'S*_{inc}(Q,E) for Ni at 300 K'")
G('set cbrange ['+ Cb + ':' + Ce + ']')
# G.splot(GD(S[Qb:Qe,Eb:Ee],Q[Qb:Qe],E[Eb:Ee]))
# raw_input("Press <Enter> to plot to file and quit...")
G("set terminal postscript eps enhanced color lw 1 'Helvetica' 24")
G("set output 'fig.eps'")
G.splot(GD(S[Qb:Qe,Eb:Ee],Q[Qb:Qe],E[Eb:Ee]))
