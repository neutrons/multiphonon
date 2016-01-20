#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#                        (C) 2007 All Rights Reserved
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

from multiphonon import batch

import unittest, os
class TestCase(unittest.TestCase):

    def test1(self):
        psets = [
            {'a': 2, 'f': 3.5, "user": "Alice"},
            {'a': 1, 'f': 1e-10, "user": "Bob"},
            ]
        filename = "test1.csv"
        names = ['a', 'f', 'user']
        batch.parametersets2csv(psets, filename, names=names)
        return


    def test2(self):
        psets = [
            {'a': 2, 'f': 3.5, "user": "Alice"},
            {'a': 1, 'f': 1e-10, "user": "Bob"},
            ]
        for pset in psets:
            for k, v in pset.iteritems():
                pset[k] = str(v)
                continue
            continue
        
        filename = "test2.csv"
        rows = list(batch.csv2parametersets(filename))
        self.assertEqual(psets, rows)
        return


    pass # end of expSqe_TestCase

    
def main():
    # import journal
##     journal.debug('instrument').activate()
##     journal.debug('instrument.elements').activate()
    unittest.main()
    return


if __name__ == '__main__': main()
    

# version
__id__ = "$Id: expSqey_TestCase.py 834 2006-03-03 14:39:02Z linjiao $"

# End of file 
