# Jiao Lin <jiao.lin@gmail.com>

"""
make phonon Density of States nicer by fitting starting curve to a parabolic 
"""

import numpy as np


def nice_dos(E, g):
    # .. in crease number of points if necessary
    if len(E) < 500:
        dE = E[-1]/500.
        E1 = np.arange(0, E[-1], dE)
        g1 = np.interp(E1, E, g)
        E, g = E1, g1
    # .. fit parabolic
    try:
        E,g = fitparabolic(E,g)
    except ParabolicFittingError:
        g = smooth(g, window_len=21)
        E,g = fitparabolic(E,g)
    # normalize
    g /= g.sum() * (E[1] - E[0])
    return E,g


class ParabolicFittingError(Exception): pass
def fitparabolic(E, g, N=100, minN = 20):
    """fit the near zero portion of the dos curve to parabolic
    """
    """
    NOTE TO DEVELOPER:
    default minN=90 matches the default requirement for 
    number of "fittable" points in the low-E region
    in c++ implementation of DOS curve. 
    """
    def fit(N):
        E1 = E[:N]; g1 = g[:N]
        return linear_regression(E1*E1, g1)
    badfit = True
    while N > minN:
        c, R2 = fit(N)
        if R2 < 0.9: N-=1
        else: badfit = False; break
        continue
    if badfit:
        # import pylab; pylab.plot(E, g); pylab.show()
        raise ParabolicFittingError("Unable to fit DOS to parabolic")
    print("DOS: fit first %s points to parbolic" % N)
    E1 = E[:N]
    g[:N] = c * E1*E1
    return E,g
    

def linear_regression(x,y):
    """ fit y = cx. return c and R**2
    """
    c = (x*y).sum() / (x*x).sum()
    y_ave = np.average(y)
    SS_tot = ((y - y_ave)**2).sum()
    SS_err = ((y - c*x)**2).sum()
    R2 = 1-SS_err/SS_tot
    return c, R2


# copied from
# http://www.scipy.org/Cookbook/SignalSmooth
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    import numpy
    
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y[(window_len/2-1):-(window_len/2)-1]
    return y


# End of file 
