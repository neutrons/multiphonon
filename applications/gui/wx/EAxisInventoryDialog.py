

import pyregui.guitoolkit.wx as base

class InventoryDialog(base.InventoryDialog):

    def get_action_window(self):
        self._init()
        sizer = base.InventoryDialog.get_action_window(self)
        return sizer
    

    def _init(self):
        appInv = self.parent.parent.inventory
        eAxisInv = self.inventory
        eiGuess = float(appInv.getValueAsString( "EiGuess" ) )

        bound = 0.99 * eiGuess
        default = 0.9 * eiGuess
        min = float (eAxisInv.getValueAsString('min'))
        max = float (eAxisInv.getValueAsString('max'))
        if min < - bound : eAxisInv.setProperty( 'min', -default )
        if max > bound : eAxisInv.setProperty( 'max', default )
        return

    pass
