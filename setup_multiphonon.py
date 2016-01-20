#!/usr/bin/env python

def preparePackage( package, sourceRoot = "." ):
    package.changeRoot( sourceRoot )
    #------------------------------------------------------------
    #dependencies
    #
    #------------------------------------------------------------

    #--------------------------------------------------------
    # now add subdirs
    #
    #multiphonon
    package.addPurePython(
        sourceDir = 'src',
        destModuleName = 'multiphonon' )

    #multiphonon.applications
    package.addPurePython(
        sourceDir = 'applications',
        destModuleName = 'multiphonon.applications' )

    #apps
    package.addScripts(sourceFiles = [
        "applications/GetDOS.py",
        "applications/wxGetDOS.py",
        ] )

    #data
    package.addData(
        sourceDir = "share",
        destDir = "multiphonon"
        )

    return package


if __name__ == "__main__":
    #------------------------------------------------------------
    #init the package
    from distutils_adpt.Package import Package
    package = Package('multiphonon', '0.1.0a')

    preparePackage( package )

    package.setup()

