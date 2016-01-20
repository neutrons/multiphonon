
from pyregui.guitoolkit.wx.SetButtonFactory import SetButtonFactory as Base

import wx

class SetButtonFactory(Base):


    def __init__(self, *args, **kwds):
        Base.__init__(self, *args, **kwds)
        return


    def onInputfile(self, prop):
        b = wx.Button(self.parent, label="Choose")
        self.parent.Bind(wx.EVT_BUTTON, self.ChooseFile( prop ),  b)
        b.SetToolTipString( "choose file for %s from browser" % prop.tip())
        return b


    def onOutputDir(self, prop):
        b = wx.Button(self.parent, label="Choose")
        self.parent.Bind(wx.EVT_BUTTON, self.ChooseDir( prop ),  b)
        b.SetToolTipString( "choose directory for %s from browser" % prop.tip())
        return b
        

    def ChooseFile(self, prop):
        import os
        def _(event):
            v = self.parent.getUserInput( prop )
            default = os.path.split( v )[0]
            if len(default) == 0: default = '.'
            d = wx.FileDialog( self.parent, "Select input file for %s: %s" % (
                prop.name(), prop.tip() ), defaultDir = default )
            if d.ShowModal() != wx.ID_OK: d.Destroy(); return
            res = str(d.GetPath())
            d.Destroy()
            self.parent.setUserInput( prop, res )

        return _


    def ChooseDir(self, prop):
        
        def _(event):
            default = self.parent.getUserInput( prop )
            if len(default ) == 0: default = '.'
            res = wx.DirSelector(
                "Select output directory", 
                defaultPath = default )
            if res is None or res == '': res = '.'
            self.parent.setUserInput( prop, res )

        return _


    def onPhiMin(self, trait):
        mainframe = self.parent.parent.parent.parent
        pyreapp = mainframe.pyreapp
        di = pyreapp.inventory.dataFiles.inventory
        calibfilename = di.calib
        instrumentFilename = di.instrumentFilename
        eiGuess = pyreapp.inventory.e_iGuess
        dataformat = pyreapp.getDataformat()

        parentWindow = self.parent
        b = wx.Button(parentWindow, label="Plot I(phi)")
        parentWindow.Bind(
            wx.EVT_BUTTON,
            self.PlotI_phi(calibfilename, instrumentFilename, eiGuess, dataformat),
            b)
        b.SetToolTipString( "pick 'dark angle region' from plot" )
        return b


    def onTbgMin(self, trait):
        mainframe = self.parent.parent.parent
        pyreapp = mainframe.pyreapp
        di = pyreapp.inventory.dataFiles.inventory
        mainfilename = di.main
        instrumentFilename = di.instrumentFilename
        dataformat = pyreapp.getDataformat()

        parentWindow = self.parent
        b = wx.Button(parentWindow, label="Plot I(tof)")
        parentWindow.Bind(
            wx.EVT_BUTTON,
            self.PlotI_tof(mainfilename, instrumentFilename, dataformat),
            b)
        b.SetToolTipString( "pick 'time-independent background region' from plot" )
        return b


    def onDatafiles(self, fac):
        b = wx.Button(self.parent, label="Set")
        self.parent.Bind(wx.EVT_BUTTON, self.SetDatafiles(fac),  b)
        return b


    def SetDatafiles(self, fac):
        def _( evt ):
            appinvDialog = self.parent
            inventory = appinvDialog.inventory
            pyre_component = inventory.getComponent( fac.name() )
            toolkit = appinvDialog.toolkit

            while 1:
                result = toolkit.InventoryDialogLoop( appinvDialog, pyre_component, toolkit )
                if result == wx.ID_CANCEL: break
                
                pyreapp = appinvDialog.parent.pyreapp
                succeed = True
                try: pyreapp.determineDataformat()
                except Exception, msg:
                    wx.MessageBox( str(msg) )
                    succeed = False
                    pass
                if succeed: break
                
            appinvDialog.update()
            return 
        return _


    def PlotI_phi(self, calibfilename, instrumentFilename, eiGuess, dataformat):
        def _(evt):
            phiMin, phiMax = launch_vanplotIphi(
                calibfilename, instrumentFilename, eiGuess, dataformat)
            parentWin = self.parent
            parentWin.setUserInput( "phiMin", str(phiMin) )
            parentWin.setUserInput( "phiMax", str(phiMax) )
            return
        return _
    

    def PlotI_tof(self, mainfilename, instrumentFilename, dataformat):
        def _(evt):
            tbgMin, tbgMax = launch_plotItof(
                mainfilename, instrumentFilename, dataformat)
            parentWin = self.parent
            parentWin.setUserInput( "tbgMin", str(tbgMin) )
            parentWin.setUserInput( "tbgMax", str(tbgMax) )
            return
        return _
    

    def createGuiElement(self, trait):
        from pyregui.inventory.proxies.FacilityProxy import FacilityProxy
        from pyregui.inventory.proxies.PropertyProxy import PropertyProxy
        from reduction.applications.Pharos.DataFiles import DataFiles, InputFile
        if isinstance( trait, PropertyProxy ):
            if trait.type() == "inputfile" : return self.onInputfile( trait )
            if trait.type() == "outputdir" : return self.onOutputDir( trait )
            if trait.name() == "phiMin": return self.onPhiMin( trait )
            if trait.name() == "tbgMin": return self.onTbgMin( trait )
            pass
        else:
            if trait.name() == "dataFiles" : return self.onDatafiles( trait )
            pass
        return Base.createGuiElement(self, trait)
        
    pass # end of SetButtonFactory
        



from pyregui.utils import findExecutable
                
vanplotIphi = findExecutable( "PharosVanPlotI_phi.py" )

def launch_vanplotIphi( calibfilename, instrumentFilename, eiGuess,
                        dataformat = "old" ):
    import popen2
    
    if dataformat == "old":
        fmtstr = "%s --Measurement.calib=\"%s\" --Measurement.instrumentFilename=\"%s\" --Measurement=PharosMeasurement --eiGuess=%s"
    else:
        fmtstr = "%s --Measurement.calib=\"%s\" --Measurement.instrumentFilename=\"%s\" --Measurement=PharosMeasurement11202005 --eiGuess=%s"
        pass # end of 'if dataformat == "old"'
    
    cmd = fmtstr % (vanplotIphi, calibfilename, instrumentFilename, eiGuess)

    print "execute %s" % cmd
        
    res = popen2.popen4( cmd )[0].readlines()[-1].strip()

    return eval(res)


plotItof = findExecutable( "PharosPlotI_tof.py" )

def launch_plotItof( mainfilename, instrumentFilename, 
                     dataformat = "old" ):
    import popen2
    
    if dataformat == "old":
        fmtstr = "%s --Measurement.main=\"%s\" --Measurement.instrumentFilename=\"%s\" --Measurement=PharosMeasurement"
    else:
        fmtstr = "%s --Measurement.main=\"%s\" --Measurement.instrumentFilename=\"%s\" --Measurement=PharosMeasurement11202005"
        pass # end of 'if dataformat == "old"'
    
    cmd = fmtstr % (plotItof, mainfilename, instrumentFilename)

    print "execute %s" % cmd

    res = popen2.popen4( cmd )[0].readlines()[-1].strip()

    return eval(res)
