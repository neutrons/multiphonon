#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

def loadDOS():
    f = 'V-dos.dat'
    from multiphonon.dos import io
    E, Z, error = io.fromascii(f)
    from multiphonon.dos.nice import nice_dos
    E,g = nice_dos(E, Z)
    return E,g


# End of file
