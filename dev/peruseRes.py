#!/usr/bin/python

import Gnuplot
GD = Gnuplot.Data
# gS = Gnuplot.Gnuplot()
gs = Gnuplot.Gnuplot()
gd = Gnuplot.Gnuplot()

# gS('set grid')
# gS('set title "Affects of Constant" font "Helvetica,30"')
gs('set grid')
gs('set xtics font "Helvetica,20"')
gs('set ytics font "Helvetica,20"')
gs('set title "Scattering(E)" font "Helvetica,30"')
gd('set grid')
gd('set xtics font "Helvetica,20"')
gd('set ytics font "Helvetica,20"')


# gS.replot(GD(sqe0.e,sqe0.se,with='histeps lw 3',\
#             title='S(E)-M(E) '+str(backgroundFrac)+' '+str(constantFrac)))
for i in range(len(res)):
  gs.plot(GD(sqe0.e,sqe0.se,with='histeps lw 3',title='S(E) Exp'))
  gs.replot(GD(sqe0.e,nar(nar(res[i][0][1:])),\
                           with='histeps lw 3',title='S(E) Calc'))
  gs.replot(GD(sqe0.e,nar(nar(res[i][0])),\
                           with='histeps lw 3',title='S(E) Calc'))
  gd('set title "DOS #'+str(i)+' at '+str(C_ms[i])+'" font "Helvetica,30"')
  gd.plot(GD(res[i][1].e,res[i][1].g,with='l lw 5',title='w/ noise'))
  gd.replot(GD(res[i][1].e,res[i][1].gz,with='l lw 5',title='cutoff'))
  raw_input(str(i)+'   '+str(C_ms[i]))





