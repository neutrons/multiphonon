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
from multiphonon import getDOS_batch



class TestCase(unittest.TestCase):

    def test(self):
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # obsolete
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        import parametersets
        getDOS_batch.run(parametersets)
        return
    

    def test2(self):
        # creating parameter sets from a common parameterset module
        import parameterset_common
        files = ['sqe.pkl', 'sqe1.pkl']
        parametersets = []
        for f in files:
            # create a parameter set dictionary
            ps = getDOS_batch.PS()
            # most parameters come from the common parameter set module
            ps.fromModule(parameterset_common)
            # input
            ps.Data = f
            # ouptut
            ps.setOutputDir('out-test2')
            # append to the list
            parametersets.append(ps)
            continue
        
        # run all parameter sets
        getDOS_batch.run_all(parametersets)
        return
    

    def test3(self):
        # creating parameter sets from a common parameterset module
        import parameterset_common
        files = ['sqe.pkl', 'sqe1.pkl']
        parametersets = []
        for f in files:
            # create a parameter set dictionary
            ps = getDOS_batch.PS()
            # most parameters come from the common parameter set module
            ps.fromModule(parameterset_common)
            # input
            ps.Data = f
            # ouptut
            ps.setOutputDir('out-test3')
            # append to the list
            parametersets.append(ps)
            continue

        # save parameters into a csv file
        from multiphonon.getDOS_batch import dump
        dump(parametersets, "params-test3.csv")
        return


    def test4(self):
        # read parameter sets from a csv file, and run it
        from multiphonon.getDOS_batch import load, run_all
        psets = load('params-test4.csv')
        for pset in psets:
            print pset
            continue
        run_all(psets)
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
