#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#                        (C) 2006  All Rights Reserved
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#


import numpy


from pyre.inventory.properties.String import String
class InputFile(String):
    def __init__(self, name, **kwds):
        String.__init__(self, name, **kwds)
        self.type = "inputfile"
        return
    pass

class OutputDir(String):
    def __init__(self, name, **kwds):
        String.__init__(self, name, **kwds)
        self.type = "outputdir"
        return
    pass


def twotuple(candidate):
    if len(candidate) != 2: raise ValueError, "Must be a 2-tuple"
    return candidate


from pyre.applications.Script import Script


class GetdosApp(Script):

    """Use Max Kresch's algorithm to obtain Density of States from
    measured S(Q,E). Multiphonon and multiscattering corrections
    are applied in the transformation.
    """

    onelinehelp = "Extract Density of States from S(Q,E), applying \n"\
                  "multiphonon and multiscattering corrections \n" \
                  "along the way\n"
    helpurl = "http://wiki.cacr.caltech.edu/danse/index.php/How_to_run_GetDOS"


    class Inventory(Script.Inventory):

        import pyre.inventory as inv

        Data = InputFile( "Data", default = "test_cases/ni_0300/sqe.pkl")
        Data.meta['tip'] = "Filename for data set as string"
        Data.meta['importance'] = 1000
        
        MT = InputFile( "MT", default = "test_cases/ni_0300/mqe.pkl" )
        MT.meta['tip'] = "Filename for empty pan data as string"
        MT.meta['importance'] = 999
        
        C_ms = inv.str( "C_ms", default = str( list(numpy.arange(0.0,2.0,0.1)) ) )
        C_ms.meta['tip'] = "a list of possible multilpiers for m-phonon"
        C_ms.meta['importance'] = 500
        
        backgroundFrac = inv.float( "backgroundFrac", default = 0.90 )
        backgroundFrac.meta['tip'] = \
            "Fraction of experimentally determined background to subtract."
        backgroundFrac.meta['importance'] = 400
        
        constantFrac = inv.float( "constantFrac", default = 0.00 )
        constantFrac.meta['tip'] = \
            "Fraction of total scattering to subtract as constant background."
        constantFrac.meta['importance'] = 400
        
        cutoff = inv.float("cutoff", default  = 8.5 )
        cutoff.meta['tip'] = "energy for Elastic cutoff in meV"
        cutoff.meta['importance'] = 300

        elasticCutAvg = inv.int( "elasticCutAvg", default = 3)
        elasticCutAvg.meta['tip'] =\
            "Use this many "\
            "bins after the cutoff to get an average "\
            "value of S(E) near the cutoff."
        elasticCutAvg.meta['importance'] = 300
        
        longE = inv.float( "longE", default = 40.0 )
        longE.meta['tip'] = \
            "Guesstimate of the high energy cutoff in meV. Please overestimate"
        longE.meta['importance'] = 200

        cutRange = inv.array('cutRange', default=[1e-20,1e20], validator=twotuple)
        cutRange.meta['tip'] = 'min and max energy of high energy cutoff in meV'
        cutRange.meta['importance'] = 200
        
        eStop  = inv.float( "eStop", default = 60.0 )
        eStop.meta['tip'] = "Don't use data above this energy"
        eStop.meta['importance'] = 200

        T = inv.float( "T", default = 300.0 )
        T.meta['tip'] = "Temperature in Kelvin"
        T.meta['importance'] = 100
        
        M = inv.float( "M", default = 58.6934 )
        M.meta['tip'] = "Mean molecular weight per atom in AMU"
        M.meta['importance'] = 100
        
        N = inv.int( "N", default = 10 )
        N.meta['tip'] = "Number of terms to include in "\
                        "multiphonon expansion..."
        N.meta['importance'] = 100

        Tol = inv.float( "Tol", default = 1.0e-7 )
        Tol.meta['tip'] = \
            "How small does LSQ penalty between the incoming and"\
            "outgoing DOS have to be before we call them equal"
        Tol.meta['importance'] = 50

        interactive = inv.bool( "interactive", default = False)
        interactive.meta['tip'] = \
            "True if you want to see how things are going."\
            "False if you don't want to be bothered."
        interactive.meta['importance'] = 0
        interactive.meta['opacity'] = 10

        viewDirectory = OutputDir("viewDirectory", default = 'view' )
        viewDirectory.meta['tip'] = \
            "Driectory in which mph.html will be created. When you "\
            "run getDOS.py, images (*.png) will also be saved "\
            "here.  You may then view the progress of your "\
            "calculation in your browser. "
        viewDirectory.meta['importance'] = 800
        
        outputDir = OutputDir("outputDir", default = 'out' )
        outputDir.meta['tip'] = "output directory"
        outputDir.meta['importance'] = 0
        outputDir.meta['opacity'] = 10

        pass # end of Inventory


    parameters =  [
        'Data',
        'MT',
        'C_ms', 
        'backgroundFrac',
        'constantFrac',  
        'cutoff',        
        'elasticCutAvg', 
        'longE',
        'cutRange',
        'eStop',         
        'T',             
        'M',             
        'N',             
        'Tol',           

        'interactive',   
        'viewDirectory', 
        'outputDir',
        ]

    def main(self, *args, **kwds):
        kwds = {}
        for param in self.parameters:
            value = getattr(self, param)
            kwds[param] = value
        from multiphonon.getDOS2 import getDOS
        getDOS( **kwds )
        return


    def __init__(self):
        Script.__init__(self, 'GetDOS')
        return


    def _configure(self):
        Script._configure(self)
        
        for param in self.parameters:
            exec "self.%s = self.inventory.%s" % (param, param)
            continue

        self.C_ms = numpy.array( eval(self.C_ms) )
        #it seems that it works better to make viewDirectory equal to outputDir
        self.outputDir = self.viewDirectory
        return


    pass # end of GetdosApp



def main():
    app = GetdosApp()
    return app.run()


# main
if __name__ == '__main__':
    # invoke the application shell
    main()


# version
__id__ = "$Id$"

# End of file 
