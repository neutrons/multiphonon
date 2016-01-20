

import wx, wx.lib.hyperlink as wxhl


def MainFrameDocBox( parent, pyreapp, size = (480, 100) ):
    onelinehelp = pyreapp.onelinehelp
    helpurl = pyreapp.helpurl

    sizer = wx.BoxSizer( wx.VERTICAL )
    sizer.Add( wx.StaticText( parent, -1, onelinehelp ) )
    sizer.Add( wxhl.HyperLinkCtrl( parent, -1, label = "help", URL=helpurl ) )
               
    return sizer
