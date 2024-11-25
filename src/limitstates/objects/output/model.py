"""
Returns the raw data that can be plotted or rendered.
all classes are unit agnostic.

"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import ceil
from  .. section import LayerGroupClt

import numpy as np

class GeomModel(ABC):
    """
    Represents a geometry and can return a set of verticies
    """
       
    @abstractmethod
    def getVerticies(self):
        pass
    
    

@dataclass
class GeomModelRectangle(GeomModel):
    b:float
    h:float
    dx0:float = 0
    dy0:float = 0
        
    def getVerticies(self):
        
        h = self.h
        b = self.b
        dx0 = self.dx0
        dy0 = self.dy0
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + dx0
        y = np.array([-h/2 , h/2 , h/2,   -h/2,    -h/2])   + dy0
        return list(x), list(y)

   


@dataclass
class GeomModelGlulam(GeomModel):
    """
    Represents a glulam rectangle and can return a fill showing the lamination
    thickness
    """
    b:float
    h:float
    dhTarget:float = 38
    dx0:float = 0
    dy0:float = 0
        
    def getVerticies(self):
        
        h = self.h
        b = self.b
        dx0 = self.dx0 
        dy0 = self.dy0 
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + dx0
        y = np.array([-h/2 , h/2 , h/2,   -h/2,    -h/2])   + dy0 
        return list(x), list(y)
    
    def getFillVerticies(self):
        """
        Returns the verticies for the input fill lines.
        """
        
        h = self.h
        b = self.b
        dx0 = self.dx0
        dy0 = self.dy0 
        dhTarget = self.dhTarget
        
        Nline = ceil(h / dhTarget)
        dh    = h / Nline

        
        x0 = [-b/2  + dx0, b/2 + dx0]
        xlines = []
        ylines = []
        dy = -h/2 + dy0 
        for ii in range(Nline-1):
            y = (ii +1)* dh  + dy
            xlines.append(x0)
            ylines.append([y, y])

        return xlines, ylines




@dataclass
class GeomModelClt(GeomModel):
    """
    Represents a glulam rectangle and can return a fill showing the lamination
    thickness.
    This won't work with imperial units.'
    
    """
    cltLayers:LayerGroupClt
    w:float = 1000

    dx0:float = 0
    dy0:float = 0

    Nboard:int = 8 
    dstart:int = 0.05 
        
    def getVerticies(self):
        
        # directions = self.cltLayers.
        h = self.cltLayers.d
        b = self.w
        dx0 = self.dx0
        dy0 = self.dy0
        
        
        bmin = -b/2  + dx0
        bmax = b/2 + dx0
                
        hmin = -h/2  + dy0
        hmax = h/2 + dy0
        
        x = [bmin, bmin , bmax, bmax, bmin]
        y = [hmin, hmax , hmax, hmin, hmin]
        return x, y
    
        
    def getFillVerticies(self):
        
        h = self.cltLayers.d
        b = self.w
        dx0 = self.dx0
        dy0 = self.dy0
        
        boundaries   = h - np.array(self.cltLayers.lBoundaries)
        orientations = self.cltLayers.getLayerOrientations()
        Nlayers      = len(self.cltLayers)
        # h = [layer.t for layer in self.cltLayers]

        
        bmin = -b/2  + dx0
        bmax = b/2 + dx0
        x0 = [bmin, bmax]
        xlayers = []
        ylayers = []
        
        dstart = b*self.dstart
        Nboard = self.Nboard
        xverticals = np.linspace(dstart, b - dstart, Nboard)
        for ii in range(Nlayers):
            
            ort = orientations[ii]
            ymin = boundaries[ii] -h/2 + dy0  
            ymax = boundaries[ii + 1] -h/2 + dy0
            
            xlayers.append(x0)
            ylayers.append([ymax, ymax])
            
            if not ort:
                for jj in range(Nboard):
                    xlayers.append([xverticals[jj],xverticals[jj]])
                    ylayers.append([ymin, ymax])

        return xlayers, ylayers
    
    
    
    def getFillAreas(self):
        h = self.cltLayers.d
        b = self.w
        dx0 = self.dx0
        dy0 = self.dy0        
        
        boundaries  = h - np.array(self.cltLayers.lBoundaries)
        orientations = self.cltLayers.getLayerOrientations()
        Nlayers     = len(self.cltLayers)
        # h = [layer.t for layer in self.cltLayers]

        
        bmin = -b/2  + dx0
        bmax = b/2 + dx0
        x0 = [bmin, bmax, bmax, bmin, bmin]
        xlayers = []
        ylayers = []
        for ii in range(Nlayers):
            
            ort  = orientations[ii]
            ymin = boundaries[ii] -h/2  + dy0
            ymax = boundaries[ii + 1] -h/2  + dy0
            if not ort:

                xlayers.append(x0)
                ylayers.append([ymax, ymax, ymin, ymin, ymax])

        return xlayers, ylayers
    
    


@dataclass
class GeomModelIbeam(GeomModel):
    d:float
    tw:float
    bf:float
    tf:float

    dx0:float = 0
    dy0:float = 0
    
    def getVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h = self.d 
        w = self.bf 
        tw = self.tw 
        tf = self.tf 
        dx0 = self.dx0
        dy0 = self.dy0
        
        x = np.array([-w/2, w/2, w/2, tw/2, tw/2, w/2,  
                      w/2, -w/2, -w/2, -tw/2, -tw/2, -w/2,
                      -w/2])
        y = np.array([ h/2, h/2, h/2 - tf, h/2 - tf, -h/2 + tf,  
             -h/2 + tf, -h/2,-h/2, -h/2+tf, -h/2+tf, h/2-tf, h/2-tf,
             h/2])
        
        return list(x + dx0), list(y + dy0)    

@dataclass
class GeomModelIbeamRounded(GeomModel):
    d:float
    tw:float
    bf:float
    tf:float
    rf:float
    rw:float

    dx0:float = 0
    dy0:float = 0
    NradiusPoints:int = 6
        
    def _getcornerVerticies(self, x0, y0, r, dx0 = 1, dy0 = 1):
        """
        dx /  dy are direction terms which are either 1 or negative 1
        """
        
        x = np.cos(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dx0*r + x0
        y = np.sin(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dy0*r + y0
        
        return list(x), list(y)
    
    def getVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h   = self.d 
        w   = self.bf 
        tw  = self.tw 
        tf  = self.tf 
        dx0  = self.dx0
        dy0  = self.dy0
        rf:float = self.rf
        rw:float = self.rw

        
        tLeg_x = [-w/2, w/2]
        tLeg_y = [ h/2, h/2]
        
        # Top right flange
        xCorner = w/2 - rf
        yCorner = h/2 - tf + rf
        trfx, trfy = self._getcornerVerticies(xCorner, yCorner, rf, 1, -1)

        # Top right web
        xCorner = tw/2 + rw
        yCorner = h/2 - tf - rw
        trwx, trwy = self._getcornerVerticies(xCorner, yCorner, rw, -1, 1)
        trwx = trwx[::-1]
        trwy = trwy[::-1]

        # Bottom right web
        xCorner = tw/2 + rw
        yCorner = -h/2 + tf + rw
        brwx, brwy = self._getcornerVerticies(xCorner, yCorner, rw, -1, -1)
        
        # Bottom right flange
        xCorner = w/2 - rf
        yCorner = -h/2 + tf - rf
        brfx, brfy = self._getcornerVerticies(xCorner, yCorner, rf, 1, 1)
        brfx = brfx[::-1]
        brfy = brfy[::-1]
        
        # Bottom leg
        bLeg_x = [w/2, -w/2]
        bLeg_y = [-h/2,-h/2]
        
        # Bottom left flange
        xCorner = -w/2 + rf
        yCorner = -h/2 + tf  - rf
        blfx, blfy = self._getcornerVerticies(xCorner, yCorner, rf, -1, 1)

        # Bottom left web
        xCorner = -tw/2 - rw
        yCorner = -h/2 + tf +rw 
        blwx, blwy = self._getcornerVerticies(xCorner, yCorner, rw, 1, -1)
        blwx = blwx[::-1]
        blwy = blwy[::-1]
        
        # top left web
        xCorner = -tw/2 - rw
        yCorner = h/2 - tf - rw
        tlwx, tlwy = self._getcornerVerticies(xCorner, yCorner, rw, 1, 1)

        # top left flange
        xCorner = -w/2 + rf
        yCorner = h/2 - tf + rf
        tlfx, tlfy = self._getcornerVerticies(xCorner, yCorner, rf, -1, -1)                
        tlfx = tlfx[::-1]
        tlfy = tlfy[::-1]        
        
        x = tLeg_x + trfx + trwx + brwx + brfx + bLeg_x + blfx + blwx + tlwx + tlfx + [-w/2]
        y = tLeg_y + trfy + trwy + brwy + brfy + bLeg_y + blfy + blwy + tlwy + tlfy  + [ h/2]       
        
        return list(np.array(x) + dx0), list(np.array(y) + dy0)


@dataclass
class GeomModelHss(GeomModel):
    d:float
    b:float
    t:float
    ro:float
    ri:float

    dx0:float = 0
    dy0:float = 0
    NradiusPoints:int = 6
        
    def _getcornerVerticies(self, x0, y0, r, dx0 = 1, dy0 = 1):
        """
        dx /  dy are direction terms which are either 1 or negative 1
        
        Note, this draws in a different orientation than the W section 
        corner rounding - clockwise, v.s. counterclockwise.
        
        """
        
        x = np.sin(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dx0*r + x0
        y = np.cos(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dy0*r + y0
        
        return list(x), list(y)
    
    
    def _getVerticiesRoundedRectangle(self, h, w, r):
        dx0  = self.dx0
        dy0  = self.dy0
        
        tLeg_x = [-w/2 + r]
        tLeg_y = [ h/2]
        
        # Top right flange
        xCorner = w/2   - r 
        yCorner = h/2 - r 
        tr_x, tr_y = self._getcornerVerticies(xCorner, yCorner, r, 1, 1)

        xCorner =  w/2  - r 
        yCorner = -h/2 +r
        br_x, br_y = self._getcornerVerticies(xCorner, yCorner, r, 1, -1)        
        br_x = br_x[::-1]
        br_y = br_y[::-1]
        
        
        xCorner = -w/2 + r
        yCorner = -h/2  +r
        bl_x, bl_y = self._getcornerVerticies(xCorner, yCorner, r, -1, -1)        
        
        xCorner = -w/2  + r 
        yCorner =  h/2 - r
        tl_x, tl_y = self._getcornerVerticies(xCorner, yCorner, r, -1, 1)            
        tl_x = tl_x[::-1]
        tl_y = tl_y[::-1]
    
    
        x = tLeg_x + tr_x + br_x + bl_x + tl_x 
        y = tLeg_y + tr_y + br_y + bl_y + tl_y 
        
        return list(np.array(x) + dx0), list(np.array(y) + dy0)    

    
    def getVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h   = self.d 
        w   = self.b
        t   = self.t 

        ro:float = self.ro
        ri:float = self.ri

        xyOutter = self._getVerticiesRoundedRectangle(h, w, ro)  
        xyInner  = self._getVerticiesRoundedRectangle(h - 2*t, w- 2*t, ri)  
        xy = np.column_stack((xyOutter, xyInner))
        
        return xy[0,:], xy[1,:]

