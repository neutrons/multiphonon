#!/SNS/software/bin/python
"""
Module containing functions to calculate incoherent scattering, including
multiphonon and approximated multiple scattering, from a DOS.
  
An instance of expSqe `sqe` is also required, but the actual scattering
data is never used (q, de, M, beta, zeroInd are used, however).

Names for functions are taken from appendix A of Sears, "Phonon density of 
states in vanadium".  Currently found at 
.../multiphonon/doc/Sears--Phonon_density_of_states_in_vanadium.pdf
"""

import numpy
nar = numpy.add.reduce

from constants       import A2m,h_b,J2meV
from doubleDos       import doubleDos

def getSQE(sqe,dos,N,C_ms,g0):
  """ Takes an expSqe, a densityOfStates, a maximum term in the multiphonon 
expansion, and a multiplier taking multiphonon scattering to multiphonon 
plus multiple scattering and returns a list of arrays S_n(Q,E) for 
0 < n <= N """
  SQE = []
  ANE = AthroughN(sqe,dos,N,g0)
  SNQ = SthroughN(sqe,dos,N,g0)
  for i in range(len(ANE)):
    SQE.append( numpy.outer(SNQ[i],ANE[i])*sqe.mask )
  SQE = numpy.array(SQE)
  SQE[1:] *= C_ms
  return SQE/nar(nar(nar(SQE)))

def AthroughN(sqe,dos,N,g0):
  """ Takes an expSqe, a densityOfStates and a maximum term in the 
multiphonon expansion and returns an array of A_n(E) for all 0 < n <= N """
  ANE = []
  ANE.append(getA1E(sqe,dos,g0))
  for i in range(2,N+1):
    ANE.append(getANE(sqe,ANE[0],ANE[-1]))
  return numpy.array(ANE)

def SthroughN(sqe,dos,N,g0):
  """ Takes an expSqe, a densityOfStates and a maximum term in the 
multiphonon expansion and returns an array of S_n(Q) for all 0 < n <= N """
  SNQ = []
  DW2 = debyeWallerExp(sqe,dos,g0)
  for i in range(1,N+1):
    SNQ.append(getSNQ(DW2,i))
  return numpy.array(SNQ)

def getA1E( sqe,dos,g0 ):
  """ Takes an expSqe and a densityOfStates and returns the shape of the 
1-phonon incoherent scattering, A_1(E) """
  g0 =  gamma0(g0)
  dDos = doubleDos( dos )
  res = dDos.gz / g0 / ( dDos.e * ( 1 - numpy.exp(-dDos.e*sqe.beta ) ) )
  z = sqe.zeroInd
  res[z] = 2.0*( res[z+1] + ( res[z+1] - res[z+2] ) )
  return res/nar(res)/dos.de
 
def getANE(sqe, A1E, ANMinus1E):
  """ Takes an expSqe the 1-phonon incoherent scattering as calculated by
getA1E(...) and the N-1-phonon incoherent scattering as calculated by 
this function and  returns the N-phonon incoherent scattering, A_N(E) """
  Y = numpy.zeros( 4*len(ANMinus1E),'d' )
  Y[len(A1E):2*len(A1E)] = ANMinus1E
  y = numpy.zeros( 3*len(A1E),'d' )
  y = y.tolist() + A1E.tolist()
  y.reverse()
  y = numpy.array(y)
  M = convMatrix(y)
  res = numpy.inner(M,Y)
  res /= nar(res)*sqe.de
  return res[len(A1E)/2+1:len(A1E)+len(A1E)/2+1] 

def getSNQ(DW2,N):
  """ Takes the exponent for the Debye Waller factor `DW2` = 2W, and an
integer N indicating a term in the phonon expansion and returns the 
intensity of the N-phonon incoherent scattering S_N(Q) """
  return DW2**N * numpy.exp(-1*DW2) / float(factorial(N))

def debyeWallerExp(sqe,dos,g0):
  """ Takes an expSqe and a densityOfStates and returns 2W, the exponent
of the Debye Waller factor. """
  g0 =  gamma0(g0)
  Er = recoilE(sqe)
  #print "Recoil Er", Er
  return Er*g0

def recoilE(sqe):
  """ Takes an expSqe and returns the recoil energy E_r(Q) """
  return J2meV * ( h_b*sqe.q/A2m )**2.0 / 2.0 /sqe.M

#def gamma0(sqe,dos):
#  """ Takes an expSqe and a densityOfStates and returns thermal factor 
#gamma_0 """
#  res = ( numpy.cosh(sqe.beta*dos.e/2.0)/ \
#          numpy.sinh(sqe.beta*dos.e/2.0)  )*(dos.gz/dos.e)*dos.de
#  res[0] = res[1] + ( res[1] - res[2] )
#  print "gamma0 = ", nar(res)
#  return nar(res)
  
def gamma0(g0):
  """ for incomplete dos, returns the same thermal factor 
gamma_0"""
  res = g0
  print "gamma0 = ", res
  return res 

def convMatrix(y):
  """  Returns matrix M, whose rows are filled with shifted copies of vector 
y"""
  M = numpy.zeros( ( len(y),len(y) ) , 'd' )
  for i in range(len(y)):
    M[i,i:] = y[:len(y)-i]
  return M

def factorial(N):
  """ Returns factorial of integer N """
  res = 1
  n = N
  while n > 0:
    res *= n
    n -= 1
  return res
