#!/usr/bin/python

import numpy as np
import pickle
import sys

#filename = "sqe_bulk_300K.xyie"

def makeSqePickle(mslicexyiefilename, picklefilename):
    """write a pickle file from an Mslice xyie sqe file."""
    infile = open(mslicexyiefilename, 'r')

    dimstring = infile.readline().strip().split()
    nq, ne = int(dimstring[0]), int(dimstring[1])

    q = np.zeros(nq)
    e = np.zeros(ne)
    i = np.zeros((ne,nq))
    r = np.zeros((ne,nq))

    infile.readline()

    # read the q values

    for iq in range(nq):
        line = infile.readline()
        q[iq] = float(line.strip())

    infile.readline()

    # read the e values
    for ie in range(ne):
        line = infile.readline()
        e[ie] = float(line.strip())

    infile.readline()

    # read the intensity
    for ie in range(ne):
        line = infile.readline()
        data = line.strip().split()
        for iq in range(nq):
            i[ie,iq] = float(data[iq])


    infile.readline()
    
    # read the errors
    for ie in range(ne):
        line = infile.readline()
        data = line.strip().split()
        for iq in range(nq):
            r[ie,iq] = float(data[iq])

    # write output to pickle sqe:
    pickle.dump((q,e,i,r), open(picklefilename, 'w'))
    pass

if __name__ == '__main__':
    mslicexyiefilename = sys.argv[1]
    picklefilename = sys.argv[2]
    makeSqePickle(mslicexyiefilename, picklefilename)
    pass




