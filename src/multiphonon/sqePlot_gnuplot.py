#!/usr/bin/python

import numpy
nar = numpy.add.reduce
import time
timeout=0.5

import os

mypath = os.path.abspath( os.path.split(__file__)[0] )
fontpath=os.path.join( mypath, '../share/fonts/ttf-thryomanes' )
#added by linjiao: to assume installer will copy fonts to sth like /usr/local/share/multiphonon/fonts
import paths
installedfontpath=os.path.join( paths.data, 'fonts/ttf-thryomanes' )
os.environ['GDFONTPATH']="%s:%s" % (fontpath, installedfontpath)
fontString = 'thryb___'

import Gnuplot
gd  = Gnuplot.Data
ggd = Gnuplot.GridData

def plotLSQ(C_ms,lsqSc,lsqMu,lsqSl,LSQ,viewDirectory,TextSize=16):
  C_MS = C_ms - 1.0
  g = Gnuplot.Gnuplot()
  g('set terminal png enhanced size 480,480')
  myfile = os.path.join(viewDirectory,'lsq.png')
  g('set output "' + myfile + '"')
  g('set grid')
  g('set key top left reverse Left')
  title='Cumulative LSQ Penalties' 
  red = 'S(Q,E)'
  green = 'high E scatter'
  blue = 'slope of high E scatter'
  g('set title "'+title+'" font "'+fontString+','+str(TextSize)+'"')
  g('set xtics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set ytics font "'+fontString+','+str(8*TextSize/10)+'"')
  xlabel = "C_{ms} [unitless]"
  g('set xlabel "'+xlabel+'" 0,-0.2 font "'+fontString+','+str(9*TextSize/10)+'"')
  ylabel = "Cumulative Penalty [unitless]" 
  g('set ylabel "'+ylabel+'" -0.5,0 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set size square')
  g('set xzeroaxis -1')
  g.plot(gd(C_MS,lsqSc,with_='l lw 5',title=red))                 # red
  g('set output "' + myfile + '"')
  g.replot(gd(C_MS,lsqMu,with_='l lw 5',title=green))             # green
  g('set output "' + myfile + '"')
  g.replot(gd(C_MS,lsqSl,with_='l lw 5',title=blue))              # blue
  time.sleep(timeout)
  myfile = os.path.join(viewDirectory,'lsq_f.png')
  g('set output "' + myfile + '"')
  title='Final Cumulative LSQ Penalty'
  g('set title "'+title+'" font "'+fontString+','+str(TextSize)+'"')
  g.plot(gd(C_MS,LSQ,with_='l lw 5'))
  time.sleep(timeout)
  return

def plotComp(sqe,sqeCalc,viewDirectory,Erange=False,Srange=False,TextSize=16):
  g = Gnuplot.Gnuplot()
  g('set terminal png enhanced size 480,480')
  myfile = os.path.join(viewDirectory,'seComp.png')
  g('set output "' + myfile + '"')
  g('set grid')
  g('set key top left reverse Left')
  title = 'S(E)' 
  red   = 'experiment'
  blue  = 'calculation'
  green = 'calculated multiphonon'
  g('set title "'+title+'" font "'+fontString+','+str(TextSize)+'"')
  if Erange:
    g('set xrange [' + str(Erange[0])+':'+str(Erange[1])+']')
  if Srange:
    g('set yrange [' + str(Srange[0])+':'+str(Srange[1])+']')
  g('set xtics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set ytics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set xlabel "E [meV]" 0,-0.2 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set ylabel "S(E) [arb]" -0.5,0 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set size square')
  g('set xzeroaxis -1')
  g.plot(gd(sqe.e,sqe.se,with_='histeps lw 3',title=red))
  g('set output "' + myfile + '"')
  g.replot(gd(sqe.e,nar(nar(sqeCalc[1:])),with_='histeps lw 3',title=green))
  g('set output "' + myfile + '"')
  g.replot(gd(sqe.e,nar(nar(sqeCalc)),with_='histeps lw 3',title=blue))
  time.sleep(timeout)
  return

def plotGE(dos,viewDirectory, Erange=False, Srange=False,TextSize=16):
  g = Gnuplot.Gnuplot()
  g('set terminal png enhanced size 480,480')
  myfile = os.path.join(viewDirectory,'dos.png')
  g('set output "' + myfile + '"')
  g('set grid')
  g('set title "g(E)" font "'+fontString+','+str(TextSize)+'"')
  if Erange:
    g('set xrange [' + str(Erange[0])+':'+str(Erange[1])+']')
  if Srange:
    g('set yrange [' + str(Srange[0])+':'+str(Srange[1])+']')
  g('set xtics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set ytics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set xlabel "E [meV]" 0,-0.2 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set ylabel "g(E) [1/meV]" -0.5,0 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set size square')
  g('set xzeroaxis -1')
  g.plot(gd(dos.e,dos.g,with_='histeps lw 3',title='with noise'))
  g('set output "' + myfile + '"')
  g.replot(gd(dos.e,dos.gz,with_='histeps lw 3 lt 3',title='zeroed'))
  time.sleep(timeout)
  return

def plotSE(sqe,viewDirectory, Erange=False, Srange=False,TextSize=16):
  g = Gnuplot.Gnuplot()
  g('set terminal png enhanced size 480,480')
  myfile = os.path.join(viewDirectory,'se.png')
  g('set output "' + myfile + '"')
  g('set grid')
  g('set title "S(E)" font "'+fontString+','+str(TextSize)+'"')
  if Erange:
    g('set xrange [' + str(Erange[0])+':'+str(Erange[1])+']')
  if Srange:
    g('set yrange [' + str(Srange[0])+':'+str(Srange[1])+']')
  g('set xtics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set ytics font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set xlabel "E [meV]" 0,-0.2 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set ylabel "S(E) [arb]" -0.5,0 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set size square')
  g('set xzeroaxis -1')
  g.plot(gd(sqe.e,sqe.se,with_='histeps lw 3'))
  time.sleep(timeout)
  return

def plotSQE(sqe,viewDirectory,filename,title="S(Q,E)",lower=False,\
                                                      upper=False,TextSize=16):
  g = Gnuplot.Gnuplot()
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
  g('set terminal png enhanced size 480,480')
  myfile = os.path.join(viewDirectory,filename)
  g('set output "' + myfile + '"')
  g('unset key')
  g('set pm3d map')
  g('set title "'+title+'" font "'+fontString+','+str(TextSize)+'"')
  g('set ylabel "E [meV]" -2,0 font "'+fontString+','+str(9*TextSize/10)+'"')
  g('set xlabel "Q [1/Angstroms]" 0,-1 font "'+fontString+','+\
                                         str(9*TextSize/10)+'"')
  g('set xtics nomirror font "'+fontString+','+str(8*TextSize/10)+'"')
  g('set ytics nomirror font "'+fontString+','+str(8*TextSize/10)+'"')
  #g('set tics scale -0.7,0.0')
  g('set style data pm3d')
  g('set xrange ['+str(sqe.q[0])+':'+str(sqe.q[-1])+']')
  g('set yrange ['+str(sqe.e[0])+':'+str(sqe.e[-1])+']')
  g('set size square')
  g.splot(ggd(sqe.sqe,sqe.q,sqe.e, with_='pm3d'))
  time.sleep(timeout)
  return

