
import os, numpy as np, warnings

class DOSStitcherBase:
    
    def __call__(self, original_dos_hist, Emin, Emax, g, gerr):
        # only if the spectrum is nontrivial beyond Emax, we need rescale
        """Update the portion of DOS in between `Emin` and `Emax` with the new 
        DOS values given in array `g`. The stitching happens at the `Emax` point.
        
        Parameters
        ----------
        original_dos_hist:histogram
            original phonon density of states

        Emin:float
            minimum value for energy transfer axis

        Emax:float 
            maximum value for energy transfer axis

        g:float 
            new phonon density of states

        gerr:float 
            error bars for new phonon density of states
        """

        assert original_dos_hist.E[-1] >= Emax
        dE = original_dos_hist.E[1] - original_dos_hist.E[0]
        if Emax + dE > original_dos_hist.E[-1]:
            rescale = False
        else:
            g_beyond_range = original_dos_hist[(Emax + dE, None)].I
            assert np.all(g_beyond_range >= 0)
            rescale = g_beyond_range.sum() > 0
        if rescale:
            scale_factor = self.match(original_dos_hist, Emin, Emax, g)
            g *= scale_factor
            # compute error bar
            gerr *= scale_factor
        # compute new DOS
        newdos = original_dos_hist.copy()
        # by updating only the front portion
        lowEportion = newdos[(Emin, Emax)]
        lowEportion.I[:] = g
        lowEportion.E2[:] = gerr ** 2
        # now renormalize
        return normalize_dos(newdos)


    def match(self, original_dos_hist, Emin, Emax, g):
        # match the new and old DOS at stitching point `Emax` and compute
        # the scale factor to scale the new DOS
        raise NotImplementedError("match()")


def compute_scalefactor_using_area_criteria(original_dos_hist, Emin, Emax, g):
    "update the lower E portion of the dos by keeping the area of the updated portion intact"
    expected_sum = original_dos_hist[(Emin, Emax)].I.sum()
    sum_now = g.sum()
    return expected_sum / sum_now


def compute_scalefactor_using_continuous_criteria(original_dos_hist, Emin, Emax, g):
    "update the lower E portion of the dos by keeping the DOS value at maximum E the same as the original DOS"
    v_at_Emax = original_dos_hist[Emax][0]
    v_now_at_Emax = g[-1]
    return v_at_Emax / v_now_at_Emax


class DOSStitcher(DOSStitcherBase):

    def __init__(self, weights=None):
        self.weights = weights
        return

    def match(self, original_dos_hist, Emin, Emax, g):
        # if need rescale, calculate the factor using some strategies and take weighted average
        scale1 = compute_scalefactor_using_continuous_criteria(original_dos_hist, Emin, Emax, g)
        scale2 = compute_scalefactor_using_area_criteria(original_dos_hist, Emin, Emax, g)
        if not np.isfinite(scale1):
            # this can happen if the original dos has value zero
            warnings.warn(
                "fail to use the continuous criteria to determine the scale factor for combining DOSes"
            )
            scale = scale2
        else:
            if abs(scale1 - scale2) / scale1 > 0.05:
                warnings.warn(
                    "Scaling factor to combine DOSes calculated is not stable: %s (using continuous criteria) vs %s (using area criteria)\n"
                    "You may want to consider adjusting the parameters such as E range (Emax more specifically)" % (
                    scale1, scale2)
                )
            weights = self.weights
            if weights is None:
                weights = [.5, .5]
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
