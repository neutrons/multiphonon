

from  pyregui.guitoolkit.wx import InventoryDialog  as InventoryDialogBase, \
     InventoryDialogLoop as InventoryDialogLoopBase


def InventoryDialogLoop( parent_window, pyre_component, toolkit):

    target = pyre_component.name
    
    if target == "PharosReductionLight":
        
        #special inventory dialog for the pyre application PharosReductionLight
        from AppInventoryDialog import InventoryDialog
        toolkit.InventoryDialog = InventoryDialog
        
    elif target == "eAxis" :
        
        #special inventory dialog for 'eAxis" component
        from EAxisInventoryDialog import InventoryDialog
        toolkit.InventoryDialog = InventoryDialog
        
    else:
        
        toolkit.InventoryDialog = InventoryDialogBase
        
        pass

    return InventoryDialogLoopBase( parent_window, pyre_component, toolkit )
