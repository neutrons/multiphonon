
import os, numpy as np, warnings


class DOSStitcherBase:
    
    def __call__(self, original_dos_hist, new_dos_hist, Emin, Emax):
        """Update the portion of DOS in between `Emin` and `Emax` with the new 
        DOS curve. The stitching happens at the `Emax` point.

        Parameters
        ----------
        original_dos_hist:histogram
            original phonon density of states

        new_dos_hist:histogram
            new phonon density of states

        Emin:float
            minimum value for energy transfer axis

        Emax:float 
            maximum value for energy transfer axis
        """
        # make sure E axis is compatible
        intersection_emin = max(original_dos_hist.E[0], new_dos_hist.E[0])
        intersection_emax = min(original_dos_hist.E[-1], new_dos_hist.E[-1])
        assert np.allclose(
            original_dos_hist[(intersection_emin, intersection_emax)].E, 
            new_dos_hist[(intersection_emin, intersection_emax)].E,
            )
        # only if the spectrum is nontrivial beyond Emax, we need rescale
        assert original_dos_hist.E[-1] >= Emax
        dE = original_dos_hist.E[1] - original_dos_hist.E[0]
        if Emax + dE > original_dos_hist.E[-1]:
            rescale = False
        else:
            g_beyond_range = original_dos_hist[(Emax + dE, None)].I
            assert np.all(g_beyond_range >= 0)
            rescale = g_beyond_range.sum() > 0
        if rescale:
            scale_factor = self.match(original_dos_hist, new_dos_hist, Emin, Emax)
        else:
            scale_factor = 1.
        # compute new DOS
        outdos = original_dos_hist.copy()
        # by updating only the front portion
        lowEportion = outdos[(Emin, Emax)]
        subset = new_dos_hist[(Emin, Emax)]
        lowEportion.I[:] = subset.I*scale_factor
        lowEportion.E2[:] = subset.E2*(scale_factor*scale_factor)
        # now renormalize
        return normalize_dos(outdos)


    def match(self, original_dos_hist, new_dos_hist, Emin, Emax):
        # match the new and old DOS at stitching point `Emax` and compute
        # the scale factor to scale the new DOS
        raise NotImplementedError("match()")


def compute_scalefactor_using_area_criteria(original_dos_hist, new_dos_hist, Emin, Emax):
    "update the lower E portion of the dos by keeping the area of the updated portion intact"
    expected_sum = original_dos_hist[(Emin, Emax)].I.sum()
    sum_now = new_dos_hist[(Emin, Emax)].I.sum()
    return expected_sum / sum_now


def compute_scalefactor_using_continuous_criteria(original_dos_hist, new_dos_hist, Emin, Emax, Npoints=3):
    """update the lower E portion of the dos by keeping the DOS value at maximum E the same as the original DOS
    the values are taken as averages of `Npoints` points with the middle point at Emax
    """
    dE = original_dos_hist.E[1] - original_dos_hist.E[0]
    hN = Npoints//2
    bracket = Emax - dE*hN, Emax + dE*hN
    if bracket[1] > new_dos_hist.E[-1]:
        raise RuntimeError("Stitching point %s too large and close to the max energy transfer for new DOS %s" % (
            Emax, new_dos_hist.E[-1]))
    expected = original_dos_hist[bracket].I.mean()
    now = new_dos_hist[bracket].I.mean()
    return expected/now


class DOSStitcher(DOSStitcherBase):

    def __init__(self, weights=None):
        self.weights = weights
        return

    def match(self, original_dos_hist, new_dos_hist, Emin, Emax):
        # if need rescale, calculate the factor using some strategies and take weighted average
        scale1 = compute_scalefactor_using_continuous_criteria(original_dos_hist, new_dos_hist, Emin, Emax, Npoints=3)
        scale2 = compute_scalefactor_using_area_criteria(original_dos_hist, new_dos_hist, Emin, Emax)
        if not np.isfinite(scale1):
            # this can happen if the original dos has value zero
            warnings.warn(
                "fail to use the continuous criteria to determine the scale factor for combining DOSes"
            )
            scale = scale2
        else:
            if abs(scale1 - scale2) / scale1 > 0.05:
                warnings.warn(
                    "Scaling factor to combine DOSes calculated is not stable: {} (using continuous criteria) vs {} (using area criteria)\n"
                    "You may want to consider adjusting the parameters such as the E range (Emin ={} Emax={}) (Emax more specifically)".format(
                    scale1, scale2, Emin, Emax)
                )
            weights = self.weights
            if weights is None:
                weights = [1., 0.]
            scale = np.dot([scale1, scale2], weights)
        assert np.isfinite(scale), "scale is a bad number: %s" % scale
        return scale


def normalize_dos(dos_hist):
    """ Parameters
        ----------
        dos_hist:histogram
            phonon density of states

    """
    dE = dos_hist.E[1] - dos_hist.E[0]
    norm = dos_hist.I.sum() * dE
    dos_hist.I /= norm
    dos_hist.E2 /= norm * norm
    return dos_hist
