# -*- python -*-
#
import ipywe.wizard as wiz
import ipywidgets as ipyw, ipywe
from ipywe import fileselector
import os, numpy as np, yaml, inspect

class Context(wiz.Context):

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
        d = self._to_dict()
        yaml.dump(d, open(path, 'wt'))
        return
    def from_yaml(self, path):
        d = yaml.load(open(path))
        for k, v in d.items():
            setattr(self, k,v)
            continue
        return
    
    def __str__(self):
        d = self._to_dict()
        l = ['%s=%s' % (k,v) for k,v in d.items()]
        return '\n'.join(l)
    
    def _to_dict(self):
        d = dict()
        for k in dir(self):
            if k.startswith('_'): continue
            v = getattr(self, k)
            if inspect.ismethod(v): continue
            d[k] = v
            continue
        return d
        
    

# ------------------------------------------------------------
# Wizard: Get Nexus files
#
# Step 1:
class GetSampleNxs(wiz.Step):
    
    def createPanel(self):
        explanation = ipyw.HTML("Please choose the sample nxs or nxspe file:")
        self.warning = ipyw.HTML()
        self.createFS()
        # the last one must be fileselector. see "validate" below
        widgets= [explanation, self.warning, self.fs.panel]
        return ipyw.VBox(children=widgets)
    
    def createFS(self):
        context = self.context
        if context.sample_nxs:
            start_dir = os.path.dirname(context.sample_nxs)
        else:
            start_dir = '/SNS/ARCS'
        self.fs = fileselector.FileSelectorPanel("Select a file", start_dir=start_dir, type='file')
        def next(s):
            self.sample_nxs = self.fs.selected
            self.handle_next_button_click(s)
            return
        self.fs.next = next
        return
    
    def validate(self):
        ext = os.path.splitext(self.sample_nxs)[-1]
        if ext not in ['.nxs', '.nxspe']:
            self.warning.value = "Please select a NXS or NXSPE file"
            self.createFS()
            self.panel.children = self.panel.children[:-1] + (self.fs.panel,)
            return
        return True
        
    def nextStep(self):
        self.context.sample_nxs = self.sample_nxs
        step2 = GetMTNxs(self.context)
        step2.show()
        return
        
NxsWizardStart=GetSampleNxs

# Step 2: 
class GetMTNxs(wiz.Step):
    
    def createPanel(self):
        explanation = ipyw.HTML("Please choose the empty can (MT) nxs or nxspe file:")
        self.warning = ipyw.HTML()
        self.skip_button = ipyw.Button(description='Skip', tooltip='Skip empty can')
        self.skip_button.on_click(self.skip)
        self.createFS()
        # the last one must be fileselector. see "validate" below
        widgets= [explanation, self.skip_button, self.warning, self.fs.panel]
        return ipyw.VBox(children=widgets)
    
    def createFS(self):
        start_dir = os.path.dirname(self.context.mt_nxs or self.context.sample_nxs)
        self.fs = fileselector.FileSelectorPanel(
            "Select a file", start_dir=start_dir, type='file')
        def next(s):
            self.mt_nxs = self.fs.selected
            self.handle_next_button_click(s)
            return
        self.fs.next = next
        return
    
    def skip(self, s):
        self.mt_nxs = None
        self.remove()
        self.nextStep()
        return

    def validate(self):
        ext = os.path.splitext(self.mt_nxs)[-1]
        if ext not in ['.nxs', '.nxspe']:
            self.warning.value = "Please select a NXS or NXSPE file"
            self.createFS()
            self.panel.children = self.panel.children[:-1] + (self.fs.panel,)
            return
        return True
        
    def nextStep(self):
        self.context.mt_nxs = self.mt_nxs
        GetEiT(self.context).show()
        return
    

# Step 3:
class GetEiT(wiz.Step):
    "Exp conditions: Ei, T"
    
    def createPanel(self):
        context = self.context
        self.text_Ei = ipyw.BoundedFloatText(
            description="Ei (meV)", value=context.Ei, min=0., max=10000)
        self.text_T = ipyw.BoundedFloatText(
            description="Temperature (Kelvin)", value=context.T, min=0., max=10000)
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [self.text_Ei, self.text_T, OK]
        return ipyw.VBox(children=widgets)
    
    def validate(self):
        self.context.Ei = self.text_Ei.value
        self.context.T = self.text_T.value
        return True
    
    def nextStep(self):
        print "Done."

def round2(a, digits = 1):
    d = 10**(np.floor(np.log10(a)) - digits+1)
    return np.round(a/d)*d


# ------------------------------------------------------------
# Wizard: Get Q and E axis
#
# Step 1:
class GetEAxis(wiz.Step):
    "E axis"
    
    def createPanel(self):
        context = self.context
        Ei = context.Ei
        self.text_Emin = ipyw.BoundedFloatText(
            description='Emin', value=(-Ei*.95 if context.Emin is None else context.Emin), min=-Ei*5, max=0)
        self.text_Emax = ipyw.BoundedFloatText(
            description='Emax', value=(Ei*.95 if context.Emax is None else context.Emax), min=0., max=Ei)
        self.text_dE = ipyw.BoundedFloatText(
            description='dE', value=(round2(Ei/100.) if context.dE is None else context.dE), min=0., max=Ei/5)
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [self.text_Emin, self.text_Emax, self.text_dE, OK]
        return ipyw.VBox(children=widgets)
    
    def validate(self):
        self.context.Emin = self.text_Emin.value
        self.context.Emax = self.text_Emax.value
        self.context.dE = self.text_dE.value
        return True
    
    def nextStep(self):
        GetQAxis(self.context).show()

QEGridWizardStart = GetEAxis


# Step 2:
class GetQAxis(wiz.Step):
    "Q axis"
    
    def createPanel(self):
        context = self.context
        Ei = context.Ei
        Qmin = 0
        from multiphonon.units.neutron import e2k
        Qmax = round2(e2k(Ei)*2*1.5, digits=2)        
        self.text_Qmin = ipyw.BoundedFloatText(
            description='Qmin', value=(Qmin if context.Qmin is None else context.Qmin), min=Qmin, max=Qmax)
        self.text_Qmax = ipyw.BoundedFloatText(
            description='Qmax', value=(Qmax if context.Qmax is None else context.Qmax), min=Qmin, max=Qmax)
        self.text_dQ = ipyw.BoundedFloatText(
            description='dQ', value=(round2(Qmax/100.) if context.dQ is None else context.dQ), min=0., max=Qmax/5)
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [self.text_Qmin, self.text_Qmax, self.text_dQ, OK]
        return ipyw.VBox(children=widgets)
    
    def validate(self):
        self.context.Qmin = self.text_Qmin.value
        self.context.Qmax = self.text_Qmax.value
        self.context.dQ = self.text_dQ.value
        return True
    
    def nextStep(self):
        import warnings
        warnings.simplefilter(action = "ignore", category = FutureWarning)
        from multiphonon.getdos import reduce2iqe
        context = self.context
        r2i = reduce2iqe(
            context.sample_nxs,
            context.Emin, context.Emax, context.dE,
            context.Qmin, context.Qmax, context.dQ,
            mt_nxs=context.mt_nxs,
            workdir=context.workdir,
        )
        for msg in r2i:print msg
        context.iqe_h5, context.mtiqe_h5, context.Qaxis, context.Eaxis = msg
        print "Done."


# Wizard: GetDOS 
#
# Step 1:
class GetInitDOS(wiz.Step):
    
    def createPanel(self):
        explanation = ipyw.HTML(
            "If you are combining data from different incident energies, it is desirable to provide an DOS computed from higher Ei. "
            "Please choose the DOS histogram for initial input (you can also skip this step) :"
        )
        self.warning = ipyw.HTML()
        self.skip_button = ipyw.Button(description='Skip', tooltip='Skip initial DOS')
        self.skip_button.on_click(self.skip)
        self.createFS()
        # the last one must be fileselector. see "validate" below
        widgets= [explanation, self.skip_button, self.warning, self.fs.panel]
        return ipyw.VBox(children=widgets)
    
    def createFS(self):
        context = self.context
        start_dir = '/SNS/ARCS' if context.initdos is None else os.path.dirname(context.initdos)
        self.fs = fileselector.FileSelectorPanel("Select a file", start_dir=start_dir, type='file')
        def next(s):
            self.initdos = self.fs.selected
            self.handle_next_button_click(s)
            return
        self.fs.next = next
        return

    def skip(self, s):
        self.initdos = None
        self.remove()
        self.nextStep()
        return
    
    def validate(self):
        ext = os.path.splitext(self.initdos)[-1]
        if ext not in ['.h5']:
            self.warning.value = "Please select a hdf5 file"
            self.createFS()
            self.panel.children = self.panel.children[:-1] + (self.fs.panel,)
            return
        return True
        
    def nextStep(self):
        self.context.initdos = self.initdos
        GetParameters(self.context).show()
        return
        
GetDOSWizStart=GetInitDOS


# Step 2:
class GetParameters(wiz.Step):
    
    def createPanel(self):
        context = self.context
        w_inputs, w_Run = createParameterInputWidgets(context)
        self.w_inputs = w_inputs
        w_Run.on_click(self.handle_next_button_click)
        # get the input widget list
        _ = w_inputs.values(); l=[]
        for t in _:
            if isinstance(t, tuple): l += list(t)
            else: l.append(t)
            continue
        widgets= l + [w_Run, ]
        return ipyw.VBox(children=widgets)
    
    def validate(self):
        return True
    
    def nextStep(self):
        context = self.context
        # suppress warning from h5py
        import warnings
        warnings.simplefilter(action = "ignore", category = FutureWarning)
        # some parameters from context
        Emin, Emax, dE = context.Eaxis; Qmin, Qmax, dQ = context.Qaxis;
        w_inputs = self.w_inputs
        # special: update_strategy_weights
        w_update_weight_continuity, w_update_weight_area = w_inputs['update_weights']
        context.update_strategy_weights = w_update_weight_continuity.value, w_update_weight_area.value
        from .getdos0 import _get_dos_update_weights
        dos_update_weights = _get_dos_update_weights(*context.update_strategy_weights)
        # special: elastic_E_cutoff
        w_ElasticPeakMin, w_ElasticPeakMax = w_inputs['ElasticPeakRange']
        elastic_E_cutoff = context.ElasticPeakMin, context.ElasticPeakMax = w_ElasticPeakMin.value, w_ElasticPeakMax.value
        # other parameters
        maxiter = 10
        # build args to be passed to getDOS method
        kargs = dict(
            mt_fraction = w_inputs['mt_fraction'].value,
            const_bg_fraction = w_inputs['const_bg_fraction'].value,
            Emin=Emin, Emax=Emax, dE=dE,
            Qmin=Qmin, Qmax=Qmax, dQ=dQ,
            T=context.T, Ecutoff=w_inputs['Ecutoff'].value, 
            elastic_E_cutoff=elastic_E_cutoff,
            M=w_inputs['M'].value,
            C_ms=w_inputs['C_ms'].value, Ei=context.Ei,
            initdos=context.initdos,
            workdir=context.workdir,
            update_strategy_weights = dos_update_weights,
            sample_nxs=context.sample_nxs,
            mt_nxs=context.mt_nxs,
            maxiter=maxiter,
            )
        # update context
        for k in ['mt_fraction', 'const_bg_fraction', 'Ecutoff', 'M', 'C_ms']:
            setattr(context, k, kargs[k])
        # run getdos
        import pprint, os, yaml
        workdir = context.workdir
        if not os.path.exists(workdir): os.makedirs(workdir)
        # save kargs sent to getDOS
        yaml.dump(kargs, open(os.path.join(workdir, 'getdos-kargs.yaml'), 'wt'))
        from ..getdos import getDOS
        from .getdos0 import log_progress
        log_progress(getDOS(**kargs), every=1, size=maxiter+2)
        return


def createParameterInputWidgets(context):
    from collections import OrderedDict
    import ipywidgets as widgets
    w_mt_fraction = widgets.BoundedFloatText(description="mt_fraction", min=0., max=100., value=context.mt_fraction)
    w_const_bg_fraction = widgets.BoundedFloatText(description="const_bg_fraction", min=0., max=1., value=context.const_bg_fraction)
    w_Ecutoff = widgets.BoundedFloatText(description="Max energy of phonons", min=0, max=1000., value=context.Ecutoff)
    w_ElasticPeakMin = widgets.BoundedFloatText(description="Emin of elastic peak", min=-300., max=0., value=context.ElasticPeakMin)
    w_ElasticPeakMax = widgets.BoundedFloatText(description="Emax of elastic peak", min=0., max=300., value=context.ElasticPeakMax)
    w_M = widgets.BoundedFloatText(description="Average atom mass", min=1., max=1000., value=context.M)
    w_C_ms = widgets.BoundedFloatText(description="C_ms", min=0., max=10., value=context.C_ms)

    update_strategy_weights = context.update_strategy_weights
    w_update_weight_continuity = widgets.BoundedFloatText(
        description='"enforce continuity" weight for DOS update strategy',
        min=0., max=1., value=update_strategy_weights[0])
    w_update_weight_area = widgets.BoundedFloatText(
        description='"area conservation" weight for DOS update strategy',
        min=0., max=1., value=update_strategy_weights[1])

    w_inputs = OrderedDict(
        mt_fraction = w_mt_fraction, const_bg_fraction = w_const_bg_fraction,
        Ecutoff = w_Ecutoff,
        ElasticPeakRange = (w_ElasticPeakMin, w_ElasticPeakMax),
        M = w_M, C_ms = w_C_ms,
        update_weights = (w_update_weight_continuity, w_update_weight_area),
    )
    w_Run = widgets.Button(description="Run")
    return w_inputs, w_Run

# End of file        
