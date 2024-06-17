#!/usr/bin/env python
#
# Jiao Lin <jiao.lin@gmail.com>


# functions to read dos from files
# return values are always e,Z,Error where e is in 'meV'.


def fromascii(datapath, x_unit=None):
    "read dos from an ascii data file"
    import warnings
    import numpy as np

    # read data
    with open(datapath) as stream:
        lines = stream.readlines()
    data = []
    comments = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            comments.append(line[1:])
            continue
        tokens = line.split()
        try:
            numbers = list(map(float, tokens))
        except Exception:
            msg = "Skip line %s" % line
            warnings.warn(msg)
            continue
        data.append(numbers)
        continue
    # treat data
    data = np.array(data).T
    E, I = data[:2]
    if len(data) > 2:
        error = data[2]
    else:
        error = np.zeros(E.size)
    # try to get unit information from comments
    supported_units = ["meV", "TeraHz"]
    if comments:
        found = False
        for c in comments:
            tokens = c.strip().split()
            desc = tokens[0]  # description of x axis
            for u in supported_units:
                if desc.find(u) != -1:
                    x_unit = u
                    found = True
                    break
                continue
            if found:
                break
            continue
    # unit conversion
    if x_unit == "meV":
        pass
    elif x_unit == "TeraHz":
        from ..units.phonon import hertz2mev
        from math import pi

        E *= 2 * pi * 1e12 * hertz2mev
    else:
        raise NotImplementedError("energy unit: %s" % x_unit)
    return E, I, error


def fromidf(datapath):
    "read dos histogram from a idf data file"
    from danse.ins.idf import readDOS

    e, Z = readDOS(datapath)
    return e, Z, np.zeros(e.size)


# End of file
