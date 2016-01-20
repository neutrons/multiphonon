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


import unittest, os
from multiphonon import getDOS



class expSqe_TestCase(unittest.TestCase):

    def test(self):
        import parameters
        getDOS.run(parameters)
        return
    
    pass # end of expSqe_TestCase

    
def main():
    # import journal
    # journal.debug('instrument').activate()
    # journal.debug('instrument.elements').activate()
    unittest.main()
    return


if __name__ == '__main__': main()
    

# version
__id__ = "$Id: expSqey_TestCase.py 834 2006-03-03 14:39:02Z linjiao $"

# End of file 
