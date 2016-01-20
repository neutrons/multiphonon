
import wx

from pyregui.guitoolkit.wx import TraitLabelFactory as base

class TraitLabelFactory( base ):


    def onTrait(self, trait):
        invDialog = self.parent
        #s = "%s: %s" % (trait.name(), trait.tip(),)
        s = "%s" % (trait.name(),)
        res = wx.StaticText(invDialog, -1, s)
        defsize = res.GetFont().GetPointSize()
        res.SetFont( wx.Font( defsize+1, wx.ROMAN, wx.NORMAL, wx.NORMAL) )
        #res.SetFont( wx.Font( 10, wx.ROMAN, wx.NORMAL, wx.BOLD) )
        #res.SetForegroundColour( wx.BLUE )
        #res.Wrap( 300 )
        return res

    onPropertyWithChoices = onBoolean = onString = onProperty = onFacility = onTrait

    pass
    
