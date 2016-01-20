# this example uses matplotlib to plot se for hydrogen
from pylab import *
from numpy import *
import cPickle as cp
  
q,e,sqe,sqerr = cp.load(open("sqe.pkl",'r'))
f=file('sqe.txt')
for i in range(q.shape):
    for j in range(e.shape):
        f.write(sqe[i,j]+'\n')
f.close()

#print q.shape, e.shape, sqe.shape
se=add.reduce(sqe)



#pl.savefig('/home/brandon/tex/graphiteKH2/msdNoK.png')
#pl.savefig('msdNoK.png')
