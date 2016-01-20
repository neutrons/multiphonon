#!/usr/bin/env python

from histogram import *
import histogram.hdf as hh
from histogram.hdf.utils import getOnlyEntry
import pickle as pkl


def convert(input, out):
    entry = getOnlyEntry(input)
    hist = hh.load(input, entry)
    Q = hist.Q
    E = hist.energy
    I = hist.I.T
    E2 = hist.E2.T
    todump = Q,E, I, E2
    pkl.dump(todump, open(out, 'w'))
    return
 

def main():
    import sys
    h5 = sys.argv[1]
    out = sys.argv[2]
    convert(h5, out)
    return


if __name__ == '__main__': main()
