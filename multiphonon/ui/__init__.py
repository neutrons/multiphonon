# -*- python -*-
#

import yaml

class Context:

    # defaults
    Ei = 100.
    sample_nxs = None
    mt_nxs = None
    Emin = Emax = dE = None
    Qmin = Qmax = dQ = None
    mt_fraction = 0.9
    const_bg_fraction = 0.
    T = 300.
    Ecutoff = 50.
    ElasticPeakMin = -20
    ElasticPeakMax = 7.
    M = 50.94
    C_ms = 0.1
    workdir = 'work'
    initdos = None
    update_strategy_weights = (0.5, 0.5)

    # yaml IO. requirement: all properties are simple as strs, ints, floats
    def to_yaml(self, path):
        d = self.to_dict()
        with open(path, 'wt') as stream:
            yaml.dump(d, stream)
        return
    def from_yaml(self, path):
        with open(path) as stream:
            d = yaml.load(stream,Loader=yaml.FullLoader)
        for k, v in d.items():
            setattr(self, k,v)
            continue
        return
    
    def __str__(self):
        d = self.to_dict()
        l = ['%s=%s' % (k,v) for k,v in d.items()]
        return '\n'.join(l)
    
    def to_dict(self):
        import inspect
        d = dict()
        for k in dir(self):
            if k.startswith('_'): continue
            v = getattr(self, k)
            if inspect.ismethod(v): continue
            d[k] = v
            continue
        return d
        
    
def context2kargs(context):
    d = context.to_dict()
    d['Emin'], d['Emax'], d['dE'] = context.Eaxis
    d['Qmin'], d['Qmax'], d['dQ'] = context.Qaxis
    from .getdos0 import _get_dos_update_weights
    d['update_strategy_weights'] = _get_dos_update_weights(*context.update_strategy_weights)
    d['elastic_E_cutoff'] = context.ElasticPeakMin, context.ElasticPeakMax
    del d['ElasticPeakMax'], d['ElasticPeakMin'], d['Eaxis'], d['Qaxis'], d['mtiqe_h5']
    return d


# End of file 
