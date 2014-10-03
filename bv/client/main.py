import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties,GraphicsPipe
from direct.gui.DirectGui import *
import zlib
from bv.common.chunk.decode import Chunk2GeomDecoder

class ClientApp(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)

        wp=base.win.getProperties()
        self.vpW=wp.getXSize()
        self.vpH=wp.getYSize()
        
        self.cfgFullscreen=True
        self.cfgFullscreen=False
        
        gp=base.win.getPipe()
        wp=WindowProperties()
        
        self.deskSize=(gp.getDisplayWidth(),gp.getDisplayHeight())

        self.isFullscreen=False
        if self.deskW>0 and self.deskH>0 and self.cfgFullscreen:
            wp.setFullscreen(True)
            wp.setSize(self.deskW(),self.deskH())
            self.vpW=self.deskW()
            self.vpH=self.deskH()
            base.win.requestProperties(wp)
            self.isFullscreen=True
        
        self.vpR=float(self.vpW)/float(self.vpH)
        
        btnQuit=DirectButton(
            text="Exit",
            pos=(0.93*self.vpR,0,.9),
            scale=0.05*self.vpR,
            command=sys.exit)
        
        decoder=Chunk2GeomDecoder()
        
        rawChunk=chr(0)*4
        sliver=(chr(1)*64)+(chr(0)*192)
        rawChunk+=sliver*16*16
        compressedChunk=zlib.compress(rawChunk)
        decoder.Chunk2Geom(compressedChunk,( 0, 0,0))

    def deskW(self):
        return self.deskSize[0]
    def deskH(self):
        return self.deskSize[1]

def run():
    app=ClientApp()
    app.run()

if __name__ == '__main__':
    run()
