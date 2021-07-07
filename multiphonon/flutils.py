import histogram as H, histogram.hdf as hh 
import h5py
import numpy as np

def MDH2Histo(filename, Ei=None):
    """
    Load an hdf 5 file containing an MDHistogram workspace and 
    populate a histogram object.
    set an Attribute Ei to the histogram object.  If Ei is None attempt to read if from the file,
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
        if Ei is None:
            try:
                Ei = rh['experiment0/logs/Ei']['value'][:][0]
            except:
                print ('Problem reading Ei from{}'.format(filename))
    
    data = datain['signal'].T/datain['num_events'].T
    err2 = datain['errors_squared'].T/(datain['num_events'].T**2)
    qaxis = H.axis('Q', boundaries=datain['|Q|'], unit='1./angstrom')
    eaxis = H.axis('E', boundaries=datain['DeltaE'], unit='meV')
    hist = H.histogram('IQE', (qaxis, eaxis), data=data, errors=err2)
    hist.setAttribute('Ei',Ei)
    return hist
