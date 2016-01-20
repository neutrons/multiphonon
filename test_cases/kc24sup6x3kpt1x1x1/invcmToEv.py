import os

datafile='phon6x3FineMeshVecs1x1x1.dens'
outfile='meV_'+datafile#os.path.splitext(datafile)[0]

f=file(datafile)
fout=file(outfile,'w')

for line in f.readlines():
    if line[0]=="#": continue
    coord,g=line.split()
    print >>fout, float(coord)*0.124,g