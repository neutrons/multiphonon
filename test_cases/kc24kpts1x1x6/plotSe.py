# this example uses matplotlib to plot se for hydrogen
from pylab import *
from numpy import *
import cPickle as cp
  
q,e,sqe,sqerr = cp.load(open("sqe.pkl",'r'))
print q.shape, e.shape, sqe.shape
se=add.reduce(sqe)


    

plot(e, se, linewidth=2.0)
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

#write to file
f=file('seSummed.txt','w')
for ePart,sePart in zip(e,se):
    f.write('%2.9f %2.9f\n' % (ePart,sePart))
f.close()


savefig('/home/jbk/tex/graphiteKH2/plotSe.png',dpi=600)
show()


#pl.savefig('/home/brandon/tex/graphiteKH2/msdNoK.png')
#pl.savefig('msdNoK.png')
