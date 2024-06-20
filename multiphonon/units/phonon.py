from pyre.units import SI, energy


def _hertz2meV():
    m = SI.meter
    kg = SI.kilogram
    s = SI.second
    hbar = 1.05457148e-34 * m**2 * kg / s
    hertz = 1 / s
    meV = energy.meV
    return hbar * hertz / meV


hertz2mev = _hertz2meV()
