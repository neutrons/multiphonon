#!/usr/bin/env python
""" the fans resolution function """

# Available Selections
mono_list = ["Cu","Pg"]
coll_list = [10,20,40,60]

def fans_res(mono,coll1=20,coll2=20):
    """
to call: 
    data = fans_res(mono='Cu', coll1=20,coll2=20)
 
mono is either 'Cu' or 'Pg' for the Cu(220) or Pg(002) monochromators
coll1 is the collimation before the monochromator. Must be 10,20,40 or 60
coll2 is the collimation after the monochromator. Must be 10,20,40 or 60
note using FANS the typical choice is coll1,coll2 = 20,20

returns an ndarray of length = 300, where each member is a length = 2
ndarray of energy value and resolution in meV (=8.0655 cm-1).
    """
    import math, numpy
    # compile_opt hidden  #XXX: don't know what this means
    if mono == "Cu":
        d_cu=1.278   # Cu(220) d-spacing A
	dmono=d_cu
	resol=numpy.zeros((350,2))
    elif mono == "Pg":
        d_pg=3.354   # Pg(002) d-spacing A
	dmono=d_pg
	resol=numpy.zeros((45,2))
    else:
        raise TypeError, "Monochromator %s not in %r" % (mono, mono_list)

    if coll1 not in coll_list:
        raise ValueError, "Collimation before monochrometer %s not in %r" % (coll1, coll_list)
    if coll2 not in coll_list:
        raise ValueError, "Collimation after monochrometer %s not in %r" % (coll2, coll_list)

    col1=coll1/60.0/57.269
    col2=coll2/60.0/57.269
    rmos=30./60./57.269
    tmpd=col1**2 + col2**2 + 4.*rmos**2
    tmpn=(col1*col2)**2 + (col1*rmos)**2 + (col2*rmos)**2
    dtheta=math.sqrt(tmpn/tmpd)

    for i in range(len(resol)):
        en=i+1
        wavel=math.sqrt(81.805/en)
        stheta=wavel/(2.*dmono)
        if abs(stheta) < 1.0:
             cot_theta=math.sqrt(1-stheta*stheta)/stheta
        else:
             cot_theta=0.0
        de=2.*en*cot_theta*dtheta

        resol[i][0]=en       #the energy array
        resol[i][1]=math.sqrt(de*de + 1.2*1.2)

    return resol  #XXX: returned ndarray is not length = 300!
