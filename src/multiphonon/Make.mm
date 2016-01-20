# -*- Makefile -*-
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                               Michael A.G. Aivazis
#                        California Institute of Technology
#                        (C) 1998-2004  All Rights Reserved
#
# <LicenseText>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PROJECT = multiphonon


BUILD_DIRS = \
	batch \


RECURSE_DIRS = $(BUILD_DIRS)


#--------------------------------------------------------------------------
#

all:: export
	BLD_ACTION="all" $(MM) recurse

tidy::
	BLD_ACTION="tidy" $(MM) recurse



#--------------------------------------------------------------------------
#
# export

EXPORT_PYTHON_MODULES = \
	__init__.py\
	constants.py\
	correction.py\
	densityOfStates.py\
	doubleDos.py\
	expSqe.py\
	io.py\
	mfit.py\
	multiphonon.py\
	paths.py\
	sqe2dos.py\
	sqePlot.py\
	sqePlot_pylab.py\
	sqePlot_gnuplot.py\
	getDOS.py\
	getDOS_batch.py\
	getDOS2.py\



#include doxygen/default.def

export:: export-package-python-modules #export-docs




# version
# $Id: Make.mm 1206 2006-11-15 21:09:22Z linjiao $

# End of file
