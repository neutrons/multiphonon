# -*- Makefile -*-
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                               Michael A.G. Aivazis
#                        California Institute of Technology
#                        (C) 1998-2005 All Rights Reserved
#
# <LicenseText>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PROJECT = multiphonon
PACKAGE = applications/gui/wx

PROJ_TIDY += *.log
PROJ_CLEAN =

#--------------------------------------------------------------------------
#

all: export

#--------------------------------------------------------------------------
#

EXPORT_PYTHON_MODULES = \
	AppInventoryDialog.py \
	EAxisInventoryDialog.py \
	InventoryDialog.py \
	InputBoxFactory.py \
	MainFrame.py \
	MainFrameDocBox.py \
	MainPanel.py \
	MainWindowApp.py \
	PlotDialog.py \
	SetButtonFactory.py \
	TraitLabelFactory.py \
	wxmpl.py \
	__init__.py \


export:: export-package-python-modules


# version
# $Id: Make.mm 1052 2006-08-02 04:45:45Z linjiao $

# End of file
