

import wx
import wxmpl

class PlotDialog( wx.Dialog ):

    def __init__(self, parent, id, title, **kwds):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, id, title, **kwds)
        self.PostCreate(pre)
        
        sizer = self._create_action_window()

        # add ok and cancel buttons to sizer
        ok = wx.Button(self, wx.ID_OK, "OK")
        cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")

        sizer.Add(ok, pos=(0,0))
        sizer.Add(cancel, pos=(0,1))

        # now paint the screen
        border = wx.BoxSizer()
        border.Add(sizer, 1, wx.GROW|wx.ALL, 25)
        border.Fit(self)
        self.SetSizer(border)
        self.Layout()

        #print "%s.__init__ done" % self.__class__.__name__
        return


    def get_figure(self): return self.plotPanel.get_figure()


    def _create_action_window(self):
        sizer = wx.GridBagSizer(vgap = 5, hgap = 5)

        self.plotPanel = wxmpl.PlotPanel( self, -1 )
        sizer.Add( self.plotPanel, pos = (1,0) )
        return sizer

        
