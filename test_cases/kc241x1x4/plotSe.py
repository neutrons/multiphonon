# this example uses matplotlib to plot se for hydrogen
from pylab import *

import cPickle as cp
  
q,e,sqe,sqerr = cp.load(open("sqe.pkl",'r'))

plot(e, add.reduce(sqe), linewidth=2.0)
axis([-0.05, 50, 0, 9])
#legend(('90 K','70 K','35 K','10 K') )

x=xlabel('E (meV)')
x.set_fontsize(18)
y=ylabel('S(Q,E) (arbitrary units)')
y.set_fontsize(18)
xlabels = getp(gca(), 'xticklabels')
setp(xlabels, fontsize=20)
ylabels = getp(gca(), 'yticklabels')
setp(ylabels, fontsize=20)

#savefig('/home/jbk/tex/graphiteKH2/plotSe.png',dpi=600)
show()


#pl.savefig('/home/brandon/tex/graphiteKH2/msdNoK.png')
#pl.savefig('msdNoK.png')
