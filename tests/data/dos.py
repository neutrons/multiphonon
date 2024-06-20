#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>

import os

datadir = os.path.abspath(os.path.dirname(__file__))


def loadDOS():
    f = os.path.join(datadir, "V-dos.dat")
    from multiphonon.dos import io

    E, Z, error = io.fromascii(f)
    from multiphonon.dos.nice import nice_dos

    E, g = nice_dos(E, Z)
    return E, g
