"""
Returns the raw data that can be plotted or rendered.
All classes are unit agnostic.


"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

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
    x0:float = 0
    y0:float = 0
        
    def getVerticies(self):
        
        h = self.h
        b = self.b
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + x0
        y = np.array([0 ,    h ,   h,   0,    0])  + y0
        return list(x), list(y)

@dataclass
class GeomModelGlulam(GeomModel):
    """
    Represents a glulam rectangle and can return a fill showing the lamination
    thickness
    """
    b:float
    h:float
    x0:float = 0
    y0:float = 0
        
    def getVerticies(self):
        
        h = self.h
        b = self.b
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + x0
        y = np.array([0 ,    h ,   h,   0,    0])  + y0
        return list(x), list(y)
    
        
    def getFillVerticies(self):
        
        h = self.h
        b = self.b
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + x0
        y = np.array([0 ,    h ,   h,   0,    0])  + y0
        return list(x), list(y)    
    

@dataclass
class GeomModelIbeam(GeomModel):
    d:float
    tw:float
    bf:float
    tf:float
    rf:float = None
    rw:float = None

    x0:float = 0
    y0:float = 0
    
    def getVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h = self.d 
        w = self.bf 
        tw = self.tw 
        tf = self.tf 
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-w/2, w/2, w/2, tw/2, tw/2, w/2,  
                      w/2, -w/2, -w/2, -tw/2, -tw/2, -w/2])
        y = np.array([ h/2, h/2, h/2 - tf, h/2 - tf, -h/2 + tf,  
             -h/2 + tf, -h/2,-h/2, -h/2+tf, -h/2+tf, h/2-tf, h/2-tf])
        
        return list(x +x0), list(y + y0)    

@dataclass
class GeomModelIbeamRounded(GeomModel):
    d:float
    tw:float
    bf:float
    tf:float
    rf:float
    rw:float

    x0:float = 0
    y0:float = 0
    NradiusPoints:int = 6
        
    def _getcornerVerticies(self, x0, y0, r, dx = 1, dy = 1):
        """
        dx /  dy are direction terms which are either 1 or negative 1
        """
        
        x = np.cos(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dx*r + x0
        y = np.sin(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dy*r + y0
        
        return list(x), list(y)
    
    def getVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h   = self.d 
        w   = self.bf 
        tw  = self.tw 
        tf  = self.tf 
        x0  = self.x0
        y0  = self.y0
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
        
        x = tLeg_x + trfx + trwx + brwx + brfx + bLeg_x + blfx + blwx + tlwx + tlfx
        y = tLeg_y + trfy + trwy + brwy + brfy + bLeg_y + blfy + blwy + tlwy + tlfy        
        
        return list(np.array(x) + x0), list(np.array(y) + y0)    

