#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#                      (C) 2007-2011  All Rights Reserved
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#


import csv


def parametersets2csv(paramsets, file, names):
    """save a list of parameter sets to a csv file

    * paramsets: an iterable of parameter sets.
      each set is a dictionary
    * names: a list of names of parameters
    * file: filename or file object
    """
    if isinstance(file, str):
        file = open(file, 'w')
        pass

    writer = csv.DictWriter(file, fieldnames=names, dialect="excel-tab")
    
    # writer.writeheader() # good on 2.7
    headerrow = {}
    for n in names: headerrow[n] = n
    writer.writerow(headerrow)
    
    writer.writerows(paramsets)
    return


def csv2parametersets(file):
    """
    """
    if isinstance(file, str):
        file = open(file, 'r')
        pass

    reader = csv.DictReader(file, dialect="excel-tab")
    return reader
    



# version
__id__ = "$Id$"

# End of file 
