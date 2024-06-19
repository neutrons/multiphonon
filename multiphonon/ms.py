#!/usr/bin/env python
#
# Jiao Lin


"""compute multiple scattering"""


def sqe(mpsqe, Ei):
    """Given multiphonon SQE, compute multiple scattering sqe"""
    # multiple scattering (MS) is uniform along Q
    # so we want to compute the average S from multi-phonon
    # scattering and assign the value to MS result
    # first compute the mask
    import numpy as np

    from .sqe import dynamical_range_mask

    mask = dynamical_range_mask(mpsqe, Ei)
    # set outside to zero
    mpsqe.I[mask] = 0
    # average
    aveS = mpsqe.I.sum(0) / np.logical_not(mask).sum(0)
    # res
    mssqe = mpsqe.copy()
    mssqe.I[:] = aveS[np.newaxis, :]
    mssqe.I[mask] = np.nan
    return mssqe


# End of file
