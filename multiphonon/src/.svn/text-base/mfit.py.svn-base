#!/usr/bin/python
#---docstring------------------------------------------------------------------
"""
Here, we are solving a least squares problem using the QR Factorization:
this can also be thought of as a column-wise Gram-Schmidt.
There is information on the row-wise version of this algorithm in:
  _Matrix_Computation_ by Golub and Van Loan, on page 241
"""
#---end-docstring--------------------------------------------------------------

import numpy as n
def poly(x,y,N,throughZero='no'):
  """ 
Takes a function y(x), a number of terms in the polynomial fit, N,
and returns the terms in the polynomial fit: 
result = [ a_n, a_n-q, ..., a_2, a_1, a_0 ]

if throughZero = 'y','Y','yes', or 'Yes' then the solution is found 
such that a_0 = 0.
"""
  M = n.zeros( (len(x), N+1),'d' )
  for i in range(len(M[0])):
    M[:,i] = x**(N-i)

  if throughZero == 'y' or throughZero == 'yes' \
  or throughZero == 'Y' or throughZero == 'Yes' :
    M = M[:,:-1]

  m,w = M.shape
  R = n.zeros((w,w),'d')
  Q = n.zeros((m,w),'d')

  v = M[:,0]
  R[0,0] = n.sqrt(n.add.reduce(v*v))
  Q[:,0] = v / R[0,0]

  for i in range(1,w):
    v = M[:,i]
    for j in range(0,i):
      p = Q[:,j]
      R[j,i] = n.add.reduce(v*p)
      v = v - R[j,i]*p
    R[i,i] = n.sqrt(n.add.reduce(v*v))
    Q[:,i] = v / R[i,i]

  w = len(R[0]);

  Q = n.inner( n.transpose(Q),y ) 
  result = n.zeros((w),'d');

  for i in range(w-1,-1,-1):
    for j in range(w-1,i-1,-1):
      Q[i] = Q[i] - R[i,j]*result[j]
    result[i] = Q[i]/R[i,i]

  return result

def poly_of_x(x,c,throughZero='no'):
  """ 
Takes an x array, and coefficients c from poly(...) and returns 
result = y(x) as calculated using the coefficients.

if throughZero was 'y','Y','yes', or 'Yes' when the coefficients
were determined, then it needs to be 'y', 'Y', 'yes', or 'Yes' here.
"""
  N = len(c)-1
  result = n.zeros(len(x),'d')
  for i in range(len(c)):
    j = i
    if throughZero == 'y' or throughZero == 'yes' \
    or throughZero == 'Y' or throughZero == 'Yes' :
      j += 1
    result += c[N-i]*x**j
  return result
