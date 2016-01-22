def get_q_e_sqe_sqerr(filename):
    # LOAD MANTID STUFF
    import sys
    sys.path.append('/opt/mantid/bin')
    from mantid.simpleapi import *
    from numpy import *
    
    #filename='/SNS/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/Mo3Sb7_and_Mo3Sb5.5Te1.5/Mo3Sb7_30meV_6K_Feb/Mo3Sb7_30meV_6K_Feb_run_number_56793.nxspe'
    #filename='/SNS/lustre/ARCS/IPTS-11718/shared/Dipanshu/Calculate_DOS/SnSe_and_SnS/SnSe_55meV_300K/SnSe_55meV_300K_run_number_59925.nxspe'
    w=Load(filename)
    print filename
    #Ebin=0.5
    #Qstep=0.1
    md=ConvertToMD(w,QDimensions='|Q|',dEAnalysisMode='Direct')
    qdim=md.getDimension(0)
    qmin=qdim.getMinimum()
    qmax=qdim.getMaximum()
    #qmin=-0.025
    #qmax=10.025
    #nqsteps=322
    emin=w.readX(0)[0]
    emax=w.readX(0)[-1]
    #emin=-54.25
    #emax=54.25
    nesteps=w.blocksize()
    nqsteps = floor((qmax-qmin)/0.04) # 4% 
    ad0='|Q|,'+str(qmin)+','+str(qmax)+','+str(int(nqsteps))
    print ad0
    #ad0='|Q|,-0.025,10.025,201'
    ad1='DeltaE,'+str(emin)+','+str(emax)+','+str(nesteps)
    print ad1
    #ad1='DeltaE,-54.25,54.25,217'
    mdh=BinMD(md,AlignedDim0=ad0,AlignedDim1=ad1)

#BinMD(InputWorkspace='ARCS_70614_autoreduced_detailed_balance_md', AlignedDim0='|Q|,0.316469,16.7911,411', AlignedDim1='DeltaE,-115.5,115.5,231', OutputWorkspace='binned')



    data=mdh.getSignalArray()
    err2=mdh.getErrorSquaredArray()
    npts=mdh.getNumEventsArray()
    sqe=data/npts
    err2=err2/npts
    sqerr=sqrt(err2)
    
    qstep=(qmax-qmin)/nqsteps
    qarray=arange(qmin+qstep*0.5,qmax,qstep)
    estep=w.readX(0)[1]-w.readX(0)[0]
    earray=arange(emin+estep*0.5,emax,estep)
    #print sqe[:,0]
    #print sqe.shape
    return qarray,earray,sqe,sqerr
    
