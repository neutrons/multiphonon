# -*- Makefile -*-
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                               Michael A.G. Aivazis
#                        California Institute of Technology
#                        (C) 1998-2004  All Rights Reserved
#
# <LicenseText>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

PROJECT = multiphonon

# directory structure

#--------------------------------------------------------------------------
all: export
#

CP_RF = cp -rf

EXPORT_SHARE_ROOT = $(EXPORT_ROOT)/share

EXPORT_SHARE_DIR =  $(EXPORT_SHARE_ROOT)/$(PROJECT)

export:: export-package-data


$(EXPORT_SHARE_DIR):
	$(MKDIR) $(MKPARENTS) $(EXPORT_SHARE_DIR)

export-package-data:: $(EXPORT_SHARE_DIR)
	for x in *; do { \
	    $(CP_RF) $$x $(EXPORT_SHARE_DIR); \
        } done


# version
# $Id: Make.mm 788 2006-02-22 05:33:34Z linjiao $

# End of file
