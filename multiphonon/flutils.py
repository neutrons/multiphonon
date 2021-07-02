import histogram as H, histogram.hdf as hh 
import h5py
import numpy as np

def MDH2Histo(filename):
    """
    Load an hdf 5 file containing an MDHistogram workspace and 
    populate a histogram object.
    """
    datain = {}
    with h5py.File(filename) as fh:
        try:
            rh = fh['MDHistoWorkspace']
        except KeyError:
            print('This is not an MDHistoWorkspace')
        kys = list(rh['data'].keys())
        for ky in kys:
            datain[ky] = rh['data'][ky][:]
    
    data = datain['signal'].T/datain['num_events'].T
    err2 = datain['errors_squared'].T/(datain['num_events'].T**2)
    qaxis = H.axis('Q', boundaries=datain['|Q|'], unit='1./angstrom')
    eaxis = H.axis('E', boundaries=datain['DeltaE'], unit='meV')
    hist = H.histogram('IQE', (qaxis, eaxis), data=data, errors=err2)
    return hist
