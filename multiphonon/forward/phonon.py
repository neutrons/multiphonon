#!/usr/bin/env python
#
# Jiao Lin


"""
compute one-phonon and multi-phonon S(Q,E) from phonon DOS

We follow the formulas in section
"Calculation of Multiphonon Scattering"
of the book 
"Experimental Inelastic Neutron Scattering".

Some of the implementation here were taken from
Max Kresch's original multiphonon code.
"""

import warnings


def sqehist(E, g, **kwds):
    "a simple wrapper of method sqe to return a histogram"
    Q,E,S = sqe(E,g, **kwds)
    import histogram as H
    Qaxis = H.axis('Q', Q, '1./angstrom')
    Eaxis = H.axis('E', E, 'meV')
    return H.histogram("SP SQE", [Qaxis, Eaxis], S)


def sqe(
    E, g, Qmax=None, Qmin=0, dQ=None,
    T=300, M=50, N=5, starting_order=2, Emax=None,
    ):
    """compute sum of multiphonon SQE from dos
    S = \sum_{i=2,N} S_i(Q,E)
    
    Note: single phonon scattering is not included. only 2-phonons and up
    
    E,g: input DOS data
    energy axis is inferred from input DOS data
    Q axis is defined by Qmax, Qmin, and dQ
    T: temperature (Kelvin)
    M: atomic mass 
    N: maximum number of order for multi-phonon scattering
    starting_order: 2: start with 2 phonon scattering
    """
    dos_sample = len(E)
    e0 = E[0]
    de = E[1] - E[0]
    emax = E[-1]
    # expand E
    Emax = Emax or e0+de*3*dos_sample
    E = np.arange(e0, Emax, de)
    g = np.concatenate((g, np.zeros(len(E)-len(g))))
    # normalize
    int_g = np.sum(g) * de
    g/=int_g
    # Q axis
    if Qmax is None:
        from ..units import neutron as nunits
        Qmax = nunits.e2k(emax) * 3
    if dQ is None:
        dQ = (Qmax-Qmin)/200
    Q = np.arange(Qmin, Qmax, dQ)
    
    # beta
    beta = 1./(T*kelvin2mev)
    
    # compute S
    S = None
    for i, (Q,E,S1) in enumerate(iterSQESet(N, Q, dQ, E, de, M, g, beta)):
        if i < starting_order - 1: continue
        if S is None: S = S1; continue
        S += S1
        continue
    
    # sum over 2..N
    # S = S_set[starting_order-1:].sum(axis=0)
    return Q, E, S


def iterSQESet(N, Q,dQ, E,dE, M, g, beta):
    """iterate over the set of S(Q,E) for n in [1,N]
    Q, dQ: Q axis
    E, dE: E axis
    M: mass
    g: phonon DOS for the given E
    beta: 1/(kBT)
    """

    E2, AnE_set = computeAnESet(N, E,g, beta, dE)
    
    DW2 = DWExp(Q, M, E,g, beta, dE)
    SnQ_set = computeSnQSet(N, DW2)
    
    sqe = []
    for S, A in zip(SnQ_set, AnE_set):
        yield Q, E2, np.outer(S, A)
        continue
    return


def computeSQESet(N, Q,dQ, E,dE, M, g, beta):
    """compute the set of S(Q,E) for n in [1,N]
    Q, dQ: Q axis
    E, dE: E axis
    M: mass
    g: phonon DOS for the given E
    beta: 1/(kBT)
    """
    
    E2, AnE_set = computeAnESet(N, E,g, beta, dE)
    
    DW2 = DWExp(Q, M, E,g, beta, dE)
    SnQ_set = computeSnQSet(N, DW2)
    
    sqe = []
    for S, A in zip(SnQ_set, AnE_set):
        sqe.append(np.outer(S, A))
        continue
    sqe = np.array(sqe)
    return Q, E2, sqe


def computeSnQSet(N, DW2):
    """ compute the set of Sn(Q) for n in [1,N]
    """
    SNQ = []
    for i in range(1,N+1):
        SNQ.append(computeSNQ(DW2,i))
    return np.array(SNQ)


def computeSNQ(DW2,N):
    """ Takes the exponent for the Debye Waller factor `DW2` = 2W, and an
    integer N indicating a term in the phonon expansion and returns the 
    intensity of the N-phonon incoherent scattering S_N(Q)
    """
    return DW2**N * np.exp(-DW2) / float(math.factorial(N))


def computeAnESet(N, E,g, beta, dE):
    """compute the set of An(E) for n in [1,N]
    """
    E, A1E = computeA1E(E,g, beta, dE)
    ANE = np.zeros((N,) + A1E.shape, dtype=A1E.dtype)
    ANE[0] = A1E
    
    for i in range(2,N+1): 
        ANE[i-1] = AnE_from_n_1(ANE[0], ANE[i-2], dE)
        continue
    return E, ANE


def AnE_from_n_1(A1E, Anm1E, dE):
    """compute A_n(E) from A_{n-1}(E)

    A_n(E) = A1 (convolve) A_{n-1}
    """
    Y = np.zeros( 4*len(Anm1E),'d' )
    Y[len(A1E):2*len(A1E)] = Anm1E
    y = np.zeros( 3*len(A1E),'d' )
    y = np.concatenate((y, A1E), axis=0)
    y = y[::-1]
    M = convMatrix(y) # XXX: this could be big
    res = np.inner(M,Y)
    del M
    res *= dE
    start = len(A1E)/2+1
    t = res[start:start + len(A1E)]
    # XXX: normalize?
    t/= t.sum() * dE
    return t


def convMatrix(y):
    """ Returns matrix M, whose rows are filled with shifted copies of vector y"""
    M = np.zeros( ( len(y),len(y) ) , 'd' )
    for i in range(len(y)):
        M[i,i:] = y[:len(y)-i]
    return M


def computeA1E(E,g, beta, dE):
    """compute A_1(E)
    
    A_1(E) = g(E)/(E*gamma_0) / (exp(E/kBT) - 1)

    E,g: numpy arrays of energies and density of states
         it must be normalized

    output: npy array of A1E 
    **note**: if the input energy array for DOS has N elements
              the output has 2N-1 elements, since the input 
              energies are in [0, Emax], while the output energies 
              are in [-Emax, Emax]
    """
    zero_ind = len(E) - 1
    g0 = gamma0(E,g, beta, dE)
    E, g = reflected(E,g)
    # t = 1./(np.exp(E*beta) - 1) # XXX
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with np.errstate(divide='ignore'):
            t = 1./(1-np.exp(-E*beta)) # XXX
    with np.errstate(invalid='ignore'):
        t = g/(E*g0)*t
    z = zero_ind
    # remove NaN
    t[z] = max(0, t[z+1] + ( t[z+1] - t[z+2] ))
    # XXX: normalize?
    # t /= t.sum()
    return E, t


def reflected(x,y):
    """compute reflected function
    
    the input x array must starts with 0
    the result is xr, yr tuple

    The reflected function has the property
    y(-x) = y(x)
    """
    def reflect(a, multiplier):
        t = (multiplier*a).tolist()
        t.reverse()
        return np.concatenate( (t, a[1:]), 0 )
    return reflect(x, -1), reflect(y, 1)

    
def coth(x):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with np.errstate(divide='ignore'):
            tentative = np.cosh(x)/np.sinh(x)
    tentative[x>10] = 1.
    tentative[x<-10] = -1
    return tentative


def gamma0(E, g, beta, dE):
    """Compute gamma0
    gamma0 = \int coth(E/2kBT) g(E)/E dE

    E,g: numpy arrays of energies and density of states
         it must be normalized
    beta: 1/kBT
    dE:  delta E in E array
    """
    assert abs(E[0]) < 1e-7 # E[0] must be 0
    dos_integrated = np.sum(g)*dE
    if not abs(dos_integrated - 1) < 1e-3:
        # import pickle as pkl
        # pkl.dump((E,g,beta,dE), open('mp.forward.phonon.gamma0-debug.pkl', 'w'))
        raise RuntimeError("integrated dos should be 1, got %s instead" % (dos_integrated,))
    # compute function to integrate
    with np.errstate(invalid='ignore'):
        f = coth(beta * E/2.) * g/E
    # f[0] would be nan, replace that with "extrapolation"
    f[0] = f[1] - (f[2] - f[1])
    return np.sum(f) * dE 


# this is an implementation that tries to deal with
# low E part differently. 
# later we decided that it is better to just replace
# the lowe E part with a parabolic. 
# see implementation in mcvine-debye-waller-core-from-phonon-dos
def gamma0a(E, g, beta, dE):
    """Compute gamma0
    gamma0 = \int coth(E/2kBT) g(E)/E dE

    E,g: numpy arrays of energies and density of states
         it must be normalized
    beta: 1/kBT
    dE:  delta E in E array
    """
    dos_integrated = np.sum(g)*dE
    assert abs(dos_integrated - 1) < 1e-3
    # when E is small, we need special treatment
    # .. find a reasonable threshold
    E_threshold = 0.1/beta
    E_threshold = max(E_threshold, dE*0.5)
    E_threshold = min(E_threshold, E[-1]*0.25)
    # .. for E > threshold, we can just integrate
    bigE = E>E_threshold
    E1 = E[bigE]; g1 = g[bigE]
    f = coth(beta * E1/2.) * g1/E1
    
    # for E < threshold, we fit the g(E) as a parabolic
    # and compute 
    smallE = E<=E_threshold
    # .. we need enough points to make a good fit
    # .. 10 is kind of random
    if smallE.sum() < 10:
        E2 = E[1:11]; g2 = g[1:11]
    else:
        E2 = E[smallE]; g2 = g[smallE]
    # .. not fit
    d2gdE2 = fitparabolic(E2, g2)
    # .. compute contribution at E=0
    atzero = 2 * d2gdE2 / beta
    # import pylab
    # pylab.plot(np.concatenate(([atzero], f)))
    # pylab.show()
    # the final result is a sum of two terms
    return atzero * (E1[0] - dE/2) + np.sum(f) * dE 


def fitparabolic(x,y):
    x2 = x*x
    return (x2*y).sum()/(x2*x2).sum()


def DWExp(Q, M, E,g, beta, dE):
    """compute 2W, the exponent of the Debye Waller factor. 
    """
    g0 =  gamma0(E,g, beta, dE)
    Er = recoilE(Q, M)
    return Er*g0


def recoilE(Q, M):
    """compute recoil energy E_r(Q)
    """
    return J2meV * ( h_b*Q/A2m )**2.0 / 2.0 / (M*amu)


""" 
Some physical constants in mks units, and some conversions to units 
convenient for neutron scattering.

A2m   = multiply by this to take Angstroms to meters
J2meV = multiply by this to convert Joules to meV 
amu   = mass of `atomic mass unit`
h     = Planck's constant
h_b   = Planck's constant / 2 pi
k_b   = Boltzmann's constant 
m_n   = Neutron mass
"""
A2m   =   1.0e-10         # multiplication by takes Angstroms to meters
J2meV =   6.2415097e+21   # multiplication by takes Joules to meV
amu   =   1.66053873e-27  # kg
h     =   6.6260688e-34   # kg m^2 / s
h_b   =   1.0545716e-34   # kg m^2 / s
k_b   =   1.3806503e-23   # kg m^2 / K s^2
m_n   =   1.6749272e-27   # kg


kelvin2mev = 0.0862


import numpy as np, math

# End of file 
