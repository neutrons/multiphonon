from math import sqrt

PI = 3.14159265
neutron_mass = 1.6749286e-27;
mN = neutron_mass;

electron_charge = 1.60217733e-19;
e = electron_charge;

boltzman_constant = 1.3806504e-23;
kB = boltzman_constant;

hbar = 1.054571628e-34;

K2V = hbar/mN*1e10
V2K = 1./K2V
#V2K = 1.58801E-3 # Convert v[m/s] to k[1/AA]
SE2V = sqrt(2e-3*e/mN)
# SE2V = 437.3949	   #/* Convert sqrt(E)[meV] to v[m/s] */
VS2E = mN/(2e-3*e)
#VS2E = 5.227e-6	   #/* Convert (v[m/s])**2 to E[meV] */
RV2W = 2*PI*K2V            # Converts reverse v[m/s] to wavelength[AA]; w = RV2W*1/v
#RV2W = 3.95664E+3
SE2K = SE2V * V2K

def v2k(vel):
    return V2K * vel
def e2v(energy):
    from numpy import sqrt
    return sqrt(energy)*SE2V
def e2k(energy):
    return v2k( e2v( energy) )
def k2v(k):
    return K2V * k
def v2e(v):
    return v*v*VS2E
def k2e(k):
    return v2e( k2v( k) )

