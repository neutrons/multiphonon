

import pyregui.guitoolkit.wx as base

class InventoryDialog(base.InventoryDialog):

    def get_action_window(self):
        sizer = base.InventoryDialog.get_action_window(self)
        self.update()
        return sizer
    

    def update(self):
        pyreapp = self.parent.pyreapp
        calibfilename = pyreapp.inventory.dataFiles.inventory.calib
        hascalib =  calibfilename != "" and calibfilename != None
        self.getGuiElement( "setButton", "vanadium").Enable( hascalib )
        
        mainfilename = pyreapp.inventory.dataFiles.inventory.main
        hasmain =  mainfilename != "" and mainfilename != None
        self.getGuiElement( "setButton", "TimeBG").Enable( hasmain )

        return


    pass
