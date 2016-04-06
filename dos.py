#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                   Jiao Lin
#                      California Institute of Technology
#                      (C) 2007-2013 All Rights Reserved  
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#


def loadDOS():
    f = 'V-dos.dat'
    from mccomponents.sample.phonon.read_dos import doshist_fromascii
    dos = doshist_fromascii(f)
    from mccomponents.sample.phonon.utils import nice_dos
    E,g = nice_dos(dos.energy, dos.I)
    import histogram as H
    dos = H.histogram(
        'dos', 
        [('energy', E, 'meV')],
        g)
    return dos
    

# version
__id__ = "$Id$"

# End of file 
