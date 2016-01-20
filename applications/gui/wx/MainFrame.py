
import wx
import pyregui.guitoolkit.wx as base

MainFrame = base.MainFrame

class MainPanel(base.MainPanel):


    def createDocBox(self):
        import wx.lib.hyperlink as wxhl

        pyreapp = self.pyreapp
        onelinehelp = pyreapp.onelinehelp
        helpurl = pyreapp.helpurl

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( wx.StaticText( self, -1, onelinehelp ) )
        sizer.Add( wxhl.HyperLinkCtrl( 
            self, -1, label = "Click here for help", URL=helpurl ) )

        return sizer


    def OnRun(self, evt):
        from pyregui.utils import findExecutable
        self._saveConfiguration()
        self._saveLauncherConfiguration()
        launcherApp = self.launcherApp
        try:
            launcherApp.run( self.pyreapp_executable )
            #from pyregui.launchers.spawn import spawn
            #spawn( findExecutable( "PlotSqe.py" ), logfile = "runPlotSqe.log" )
            m = "%s done successfully. Please use histogramGui.py to see the result." % self.pyreapp_executable
        except Exception, msg:
            m = str(msg)
            pass
        
        wx.MessageBox( m, "" )
        return
    
