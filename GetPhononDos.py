from mantid.kernel import *
from mantid.api import *
from mantid.simpleapi import *
import matplotlib.pyplot as plt
#        
from expSqe import expSqe
from correction import *
from sqePlot import *
from constants import *
import numpy

class GetPhononDOS(PythonAlgorithm) :
    def PyInit(self) :

        """ Declare all inputs required for the calculation of the DOS here
        DataFileName            Filename for data set as string
        EmptyFileName              Filename for empty pan data as string
        C_ms            numpy.array of possible multilpiers for m-phonon
        backgroundFrac  Fraction of experimentally determined background to 
                  subtract.
        constantFrac    Fraction of total scattering to subtract as constant 
                  background.
        cutoff          energy for Elastic cutoff in meV
        elasticCutAvg   Use this many bins after the cutoff to get an average 
                  value of S(E) near the cutoff.
        longE           Guesstimate of the debye cutoff in meV. Please 
                  overestimate.
        T               Temperature in Kelvin
        M               Molecular weight for sample in AMU  
        eStop           Use this to limit energy range. Units are meV.
        N               Number of terms to include in multiphonon expansion...
        Tol             How small does LSQ penalty between the incoming and
                  outgoing DOS have to be before we call them equal
                  """
                  
        self.declareProperty(FileProperty("DataFilename","",action=FileAction.Load),"NXSPE format data file for input.")
        self.declareProperty(FileProperty("EmptyFilename","",action=FileAction.Load),"NXSPE format empty file for input.")

        self.declareProperty("C_ms",[1.0],"Array of multipliers for multiphonon.")
        self.declareProperty("backgroundFrac",0.0,FloatBoundedValidator(lower=-1.0, upper = 1.0),"Fraction of experimentally determined background to subtract.")

        self.declareProperty("constantFrac",0.0,FloatBoundedValidator(lower=0.0),"Fraction of total scattering to subtract as constant background.")
        self.declareProperty("cutoff",3.0,FloatBoundedValidator(lower=0.0),"Energy for elastic cutoff in meV.")
        self.declareProperty("elasticCutAvg",3,IntBoundedValidator(lower=0),"Number of bins to include after the cutoff to get an average of S(E) near cutoff.")       

        self.declareProperty("longE",0.0,FloatBoundedValidator(lower=0.0),"Estimate of the DeBye Cutoff in meV; One should overestimate this value.")
        self.declareProperty("T",0.0,FloatBoundedValidator(lower=0.0),"Temperature of system in K.")       
        self.declareProperty("M",0.0,FloatBoundedValidator(lower=0.0),"Mass of system in AMU.")       
        self.declareProperty("eStop",20.0,FloatBoundedValidator(lower=0.0),"Energy to stop calculation.")


        self.declareProperty("N",3,IntBoundedValidator(lower=0),"Number of terms to include in multiphonon expansion.")       
        self.declareProperty("Tol",0.0,FloatBoundedValidator(lower=0.0),"Tolerance for least squares penalty.")              

        self.declareProperty("qbinning",0.04,FloatBoundedValidator(lower=0.0),"Value for qaxis bin size (fraction of whole axis).")          
        self.declareProperty("QCropMin",2.0,FloatBoundedValidator(lower=0.0),"Minimum Value for Q to retain in calculation.")  
        self.declareProperty("QCropMax",5.0,FloatBoundedValidator(lower=0.0001),"Maximum Value for Q to retain in calculation.")  

     
        self.declareProperty(WorkspaceProperty("OutputWorkspace",defaultValue="",direction=Direction.Output),doc="Workspace to store calculated dos file information.")
        self.declareProperty(WorkspaceProperty("Multiphonon",defaultValue="",direction=Direction.Output),doc="Workspace to store calculated dos file information.")
        self.declareProperty(WorkspaceProperty("Calculated",defaultValue="",direction=Direction.Output),doc="Workspace to store calculated dos file information.")
        
        
   
    def PyExec(self):
        _dataws=Load(Filename=self.getPropertyValue("DataFilename"))
        self.log().information("Loaded data from file:" + self.getPropertyValue("DataFileName"))
        _mtws = Load(Filename = self.getPropertyValue("EmptyFilename"))
        self.log().information("Loaded empty can data from file:" + self.getPropertyValue("EmptyFileName"))       
        

        ###############################################
        #Convert data to MD Workspace
        #self.setProperty("OutputWorkspace",_tmpws)
        #convert data file to MDworkspace and extract min/max qvalues
        _md = ConvertToMD(_dataws,QDimensions='|Q|',dEAnalysisMode='Direct')
        qdim = _md.getDimension(0)
        qmin = qdim.getMinimum()
        qmax = qdim.getMaximum()
        #set qbinning at 4%
        qbin = self.getProperty("qbinning").value
        nqsteps = int(numpy.floor((qmax - qmin)/qbin))
        qstep = (qmax-qmin)/nqsteps

        #extract energy min, max, and steps from data histogram
        emin = _dataws.readX(0)[0]
        emax = _dataws.readX(0)[-1]
        nesteps = _dataws.blocksize()
        estep = _dataws.readX(0)[1] - _dataws.readX(0)[0]
        
        #set parameters for BinMD and doIt
        ad0='|Q|,'+str(qmin)+','+str(qmax)+','+str(nqsteps)
        ad1='DeltaE,'+str(emin)+','+str(emax)+','+str(nesteps)
        dataMDH=BinMD(_md,AlignedDim0=ad0,AlignedDim1=ad1)
    
        #creating line plots for elastic line to aid in background determination
        dataElasticLine = BinMD(InputWorkspace=_md, AlignedDim0=ad0, AlignedDim1='DeltaE,-2,2,1')
        ConvertMDHistoToMatrixWorkspace(InputWorkspace=dataElasticLine, OutputWorkspace=dataElasticLine, Normalization='VolumeNormalization')

        #creating inelastic line plots for data near peak in Al PDOS line to aid in background determination
        dataInElasticLine = BinMD(InputWorkspace=_md, AlignedDim0=ad0, AlignedDim1='DeltaE,18.0,22.0,1')
        ConvertMDHistoToMatrixWorkspace(InputWorkspace=dataInElasticLine, OutputWorkspace=dataInElasticLine, Normalization='VolumeNormalization')


        
        sqeEnArray = numpy.arange(emin+estep*0.5,emax,estep)
        sqeQArray = numpy.arange(qmin+qstep*0.5,qmax,qstep)

        
        #Convert empty to MD Workspace; in principle should functionalize this to be consistent with data MDbinning above.
        #self.setProperty("OutputWorkspace",_tmpws)
        #convert data file to MDworkspace and extract min/max qvalues
        _mtmd = ConvertToMD(_mtws,QDimensions='|Q|',dEAnalysisMode='Direct')
        qdim = _md.getDimension(0)
        qmin = qdim.getMinimum()
        qmax = qdim.getMaximum()
        qbin = self.getProperty("qbinning").value
        nqsteps = int(numpy.floor((qmax - qmin)/qbin))
    
        #extract energy min, max, and steps from empty data histogram
        emin = _mtws.readX(0)[0]
        emax = _mtws.readX(0)[-1]
        nesteps = _mtws.blocksize()
        
        #set parameters for BinMD and doIt
        ad0='|Q|,'+str(qmin)+','+str(qmax)+','+str(nqsteps)
        ad1='DeltaE,'+str(emin)+','+str(emax)+','+str(nesteps)
        emptyMDH=BinMD(_mtmd,AlignedDim0=ad0,AlignedDim1=ad1)

        #creating line plots for elastic line to aid in background determination
        emptyElasticLine = BinMD(InputWorkspace=_mtmd, AlignedDim0=ad0, AlignedDim1='DeltaE,-2,2,1')
        ConvertMDHistoToMatrixWorkspace(InputWorkspace=emptyElasticLine, OutputWorkspace=emptyElasticLine, Normalization='VolumeNormalization')

        #creating inelastic line plots for data near peak in Al PDOS line to aid in background determination
        emptyInElasticLine = BinMD(InputWorkspace=_mtmd, AlignedDim0=ad0, AlignedDim1='DeltaE,18.0,22.0,1')
        ConvertMDHistoToMatrixWorkspace(InputWorkspace=emptyInElasticLine, OutputWorkspace=emptyInElasticLine, Normalization='VolumeNormalization')


        emptyEnArray = numpy.arange(emin+estep*0.5,emax,estep)
        emptyQArray = numpy.arange(qmin+qstep*0.5,qmax,qstep)
 
        ############################################
        # Extract SQE from MDH data and empty
        sqeData = dataMDH.getSignalArray()/dataMDH.getNumEventsArray()
        sqeEmpty = emptyMDH.getSignalArray()/emptyMDH.getNumEventsArray()
        
        sqeDataErr = numpy.sqrt(dataMDH.getErrorSquaredArray() / dataMDH.getNumEventsArray())
        sqeEmptyErr = numpy.sqrt(emptyMDH.getErrorSquaredArray() / emptyMDH.getNumEventsArray())
        
        #redefine numpy.add.reduce
        nar = numpy.add.reduce
        
        #series sets all nan's to zeros; all sqe "pixels" that are zeroes are later masked.
        sqeData=numpy.nan_to_num(sqeData)
        sqeEmpty=numpy.nan_to_num(sqeEmpty)
        sqeDataErr=numpy.nan_to_num(sqeDataErr)
        sqeEmptyErr=numpy.nan_to_num(sqeEmptyErr)

         #instantiate the sqe objects for data and empty using _initFromVals method of expSqe.
        #expSqe objects instantiated from values need mass in kg, not amu
        M = self.getProperty("M").value
        T = self.getProperty("T").value
        #expSqe expects sqe data that is in the form of the transpose of that returned from the method get_q_e_sqe_sqerr, so the data are transposed here.
        #print "Q Arrays: ", sqeQArray, len(sqeQArray) 
        #print "Q Arrarys: ", emptyQArray, len(emptyQArray)
        
        #print "Earrays: ", sqeEnArray, len(sqeEnArray)
        #print "Earrays, MT: ", emptyEnArray, len(emptyEnArray)
        
        #transpose of sqe arrays suddenly hosing things?
        
        #sqe = expSqe(sqeQArray,sqeEnArray,sqeData.T,sqeDataErr.T,T,M)
        #mqe = expSqe(emptyQArray,emptyEnArray,sqeEmpty.T,sqeEmptyErr.T,T,M)

        #print "shape sqe: ", numpy.shape(sqeData)
        sqe = expSqe(sqeQArray,sqeEnArray,sqeData,sqeDataErr,T,M)
        mqe = expSqe(emptyQArray,emptyEnArray,sqeEmpty,sqeEmptyErr,T,M)


        #remove background by subtracting empty can, and correcting for user supplied backgroudn and constant frac substractions
        sqe.removeBackground(mqe,self.getProperty("backgroundFrac").value,self.getProperty("constantFrac").value)
        
        #negative infinities are creeping in here... don't understand why.
        # mass values are not instantiating properly for CuInP set vs AgBiSe?
        print "After BG Sub.."

        # crop SQE using elastic cutoff information and qmin/max values
        sqe.cropQEForCalc(self.getProperty("cutoff").value,self.getProperty("QCropMin").value,self.getProperty("QCropMax").value,self.getProperty("eStop").value,self.getProperty("elasticCutAvg").value)

        #normalize
        sqe.norm2one()
        #expand range around SQE for multiphonon information This was a straight transfer from getDos.
        sqe.expand(2.0)
        
        #breaking here - trying to figure out why we are getting all NAN's after the correction.  At this point, the SQE seems reasonable, trying to get it into a workspace to plot.
        #_sqews = CreateWorkspace2D(sqe.e,sqe.sqe,YUnitLabel='SQE (arb)',UnitX='Energy',WorkspaceTitle='SQE Before Correction')
        #set outputs
        #self.setProperty("OutputWorkspace",mdh)
        #DeleteWorkspace(mdh)
        #self.setProperty("OutputWorkspace",_dataws)
        
        #perform calculation to correct the scattering
        res = getCorrectedScatter(sqe,self.getProperty("C_ms").value,self.getProperty("N").value,self.getProperty("Tol").value,interactive=False)
        
        dosCalc = res[0][1]

        
        _dosws = CreateWorkspace(dosCalc.e,dosCalc.g,YUnitLabel='Dos (1/meV)',UnitX='Energy',WorkspaceTitle='DensityOfStates')
        #_doszerows = CreateWorkspace(dosCalc.e,dosCalc.gz,YUnitLabel='Dos (1/meV)',UnitX='Energy',WorkspaceTitle='DensityOfStatesWithNoise')
        
        
        testres=res[-1][0]
        mphon = nar(nar(testres[1:]))
        dos = nar(nar(testres))
        
     
        
        _mphon = CreateWorkspace(sqe.e,mphon,YUnitLabel='arb',UnitX='Energy',WorkspaceTitle='Calculated Multiphonon')
        _cdos = CreateWorkspace(sqe.e,dos,YUnitLabel='arb',UnitX='Energy',WorkspaceTitle='Calculated Dos')

        #WorkspaceFactory.create("Workspace2D",NVectors=2,XLength=len(sqe.e),YLength=len(sqe.e)+1)
        #_output.dataX(0) = sqe.e
        #_output.dataY(0) = mphon
        #_output.dataX(1) = sqe.e
        #_output.dataY(1) = dos
        
        self.setProperty("OutputWorkspace",_dosws)
        #self.setProperty("ZeroedDos",_doszerows)
        self.setProperty("Multiphonon",_mphon)
        self.setProperty("Calculated",_cdos)
        
        """
        #NOTES
         - diffraction comparison cut for empty can subtraction
         - include info for the half dos calculation
         - include output for zeroed with noise calculation
         - include 2D map of cropped SQE
         - include energy slices at finited energy transfer to aid in background subtraction
        """
        #cleanup

        DeleteWorkspace(_mtmd)
        DeleteWorkspace(_md)
        DeleteWorkspace(_dataws)
        DeleteWorkspace(_mtws)
        DeleteWorkspace(_dosws)
        DeleteWorkspace(_mphon)
        DeleteWorkspace(_cdos)
       
        RenameWorkspace(InputWorkspace='emptyMDH', OutputWorkspace='Empty')
        RenameWorkspace(InputWorkspace='dataMDH', OutputWorkspace='Data')
 
      
        
AlgorithmFactory.subscribe(GetPhononDOS)
 