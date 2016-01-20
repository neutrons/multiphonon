# -*- python -*-



def dump(parameter_sets, csvfile):
    pset0 = parameter_sets[0]
    if isinstance(pset0, PS):
        parameter_sets = [ps.asDict() for ps in parameter_sets]
    names = parameter_sets[0].keys()
    from .batch import parametersets2csv
    return parametersets2csv(parameter_sets, csvfile, names)


def load(csvfile):
    from .batch import csv2parametersets
    dicts = csv2parametersets(csvfile)
    psets = []
    for d in dicts:
        ps = PS()
        ps.fromDict(d)
        psets.append(ps)
        continue
    return psets


def run1(pset):
    if isinstance(pset, dict):
        ps = PS()
        for k, v in pset.iteritems():
            setattr(ps, k, v)
            continue
        pset = ps
    from . import getDOS
    getDOS.run(pset)
    return


def run_all(parameterset_list):
    for ps in parameterset_list:
        run1(ps)
        continue
    return


class Descriptor:

    converter = None

    def __init__(self, **kwds):
        for k,v in kwds.iteritems():
            setattr(self, k, v)
            continue
        return


def tonpyarr(s):
    s = s.strip()
    if s.startswith('['): s = s[1:]
    if s.endswith(']'): s = s[:-1]
    s = s.strip()
    l = [eval(i) for i in s.split()]
    import numpy
    return numpy.array(l)


class PS: 
    
    default_converter = eval
    Data = Descriptor(converter=str)
    viewDirectory = Descriptor(converter=str)
    outputDir = Descriptor(converter=str)
    C_ms = Descriptor(converter=tonpyarr)
    

    def __repr__(self):
        s = []
        for k, v in self.__dict__.iteritems():
            if not k.startswith('_'):
                s.append("%s=%s" % (k,v))
            continue
        return 'PS(' + ', '.join(s) + ')'


    def cast(self):
        kls = self.__class__
        for k, v in self.__dict__.iteritems():
            # if v is empty string, treats it as None
            if not v:
                setattr(self, k, None)
                continue
            # otherwise, make appropriate conversion if necessary
            if k not in kls.__dict__:
                converter = self.default_converter
            else:
                descriptor = kls.__dict__[k]
                converter = descriptor.converter
                pass
            v = converter(v)
            setattr(self, k, v)
            continue
        return self


    def fromDict(self, d, casting=True):
        for k, v in d.iteritems():
            setattr(self, k, v)
            continue
        if casting:
            self.cast()
        return self


    def fromModule(self, mod):
        for k, v in mod.__dict__.iteritems():
            if k.startswith('_'):
                continue
            setattr(self, k, v)
            continue
        return self

    
    def asDict(self):
        d = {}
        for k, v in self.__dict__.iteritems():
            d[k] = v
            continue
        return d
        

    def setOutputDir(self, outdir):
        import os
        self.outputDir = os.path.join(outdir, self.Data, 'data')
        self.viewDirectory = os.path.join(outdir, self.Data, 'view')
        return outdir



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# obsolete
def run(parameterset):
    import warnings
    warnings.warn("This is obsolete. Use run_all directly")
    pset = parameterset
    # if it contains just one data, run the non-batch version
    if isinstance(pset.Data, str):
        from . import getDOS
        return getDOS.run(pset)

    # this assumes that 
    # pset.Data is an iterator of data files
    # and other parameters are either a list of parameters each
    # corresponding to one data file, or one parameter
    # that works for all files.

    pslist = []

    for i, datafile in enumerate(pset.Data):
        ps = PS()
        ps.Data = datafile
        
        # all parameters that are not list
        for key in nonlist_parameters:
            value = getattr(pset, key)
            if isinstance(value, list):
                value = value[i]
            setattr(ps, key, value)
            continue

        # all parameters that are lists already
        for key in list_parameters:
            value = getattr(pset, key)
            if isinstance(value[0], list):
                value = value[i]
            setattr(ps, key, value)
            continue
        
        #
        import os
        ps.outputDir = os.path.join(pset.outputDir, datafile, 'data')
        ps.viewDirectory = os.path.join(pset.outputDir, datafile, 'view')

        pslist.append(ps)
        continue

    # print pslist
    run_all(pslist)
    return

nonlist_parameters = [
    'MT',
    'backgroundFrac',
    'constantFrac',
    'cutoff',
    'elasticCutAvg',
    'longE',
    'QHi',
    'QLow',
    'eStop',
    'T',
    'M',
    'N',
    'Tol',
    'maxIter',

    'interactive',
    ]
list_parameters = [
    'C_ms',
    'cutRange',
    ]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


