
from pyregui.guitoolkit.wx.InputBoxFactory import InputBoxFactory as Base

import wx

class InputBoxFactory(Base):


    def onFacility(self, facility):
        guielement = Base.onFacility(self, facility)
        #guielement.Enable( False )
        return guielement


    def onDataformatPostCreation( self, dataformat, guielement ):
        Base.postCreation( self, dataformat, guielement )
        invDialog = self.parent
        invDialog.Bind(wx.EVT_COMBOBOX, self.OnDataformatChange, guielement)
        guielement.SetToolTipString( dataformat.tip() )
        return


    def onDiagonalPostCreation(self, trait, guielement ):
        Base.postCreation( self, trait, guielement )
        guielement.SetToolTipString( "[ width, height, thickness ] of vanadium sample" )
        return
    

    def OnDataformatChange(self, evt):
        invDialog = self.parent
        appInvDialog = invDialog.parent
        dataformat = invDialog.getUserInput( "dataformat" )
        appInvDialog.updateDataformat( dataformat )
        return


    def postCreation(self, trait, guielement):
        if trait.name() == "dataformat": self.onDataformatPostCreation( trait, guielement )
        if trait.name() == "diagonal":  self.onDiagonalPostCreation( trait, guielement )
        else: Base.postCreation( self, trait, guielement )
        return


    pass # end of InputBoxFactory
        
