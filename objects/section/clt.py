"""
Classes that are used to represent CLT sections.


"""

from .section import SectionAbstract
from ..material import MaterialElastic

from dataclasses import dataclass
import numpy as np

from typing import List, Protocol


class AbstractMaterialTimber(Protocol):
    fb: float
    fv: float
    E: float
    E90: float
    G: float
    G90: float

    def getE(self, isStrong:bool):
        pass

    def getG(self, isStrong:bool):
        pass
    
    
@dataclass
class LayerClt:
    t:float
    mat:AbstractMaterialTimber
    orientation:float = 0    
    # y:float = None
    # w:float = None
    # A:float = None
    lUnit:str = 'mm'
    
    def setI(self):
        self.I = self.t**3 * self.w / 12
        
    def __repr__(self):
        return f"<limitstates CLT layer {self.t}{self.lUnit} {self.mat.name}.>"
        
        # EAy = 0
        # for layer in layers:
        #     EAy += layer.E90 


class LayerGroupClt:
    # y:ndarray[float]
    # w:ndarray[float]
    # A:ndarray[float]
    # mats:list[MaterialElastic]
    layers:list[LayerClt]
    ybar:float
    dnet:float
    
    def __init__(self, layers):
        self.layers:list[LayerClt] = layers
        
        self.d = sum(self.getLayerAttr('t'))
    
    def _setLayerPositions(self):
        lMidpointsAbs = []
        for ii in range(len(self.layers)):
            lMidpointsAbs.append(self.lBoundaries[ii+1] - self.layers[ii].t/2)
        self.lMidpointsAbs = lMidpointsAbs
     
    def _setLayerBoundaries(self):
        y0 = 0
        boundaries = [0]
        for layer in self.layers:
            y0 = y0 + layer.t
            boundaries.append(y0)      
        self.lBoundaries = boundaries
        
    def getLayerAttr(self, attr:str) -> np.ndarray:
        out = []
        for layer in self.layers:
            out.append(getattr(layer, attr))
        return np.array(out)
        
         
    def _setYbar(self) -> float:
        EAy = 0
        EA = 0        
        for ii in range(len(self.layers)):
            layer = self.layers[ii]
            EAtemp = layer.mat.E * layer.t
            EA += EAtemp
            EAy += EAtemp*self.lMidpointsAbs[ii]
            
        self.ybar =  EAy / EA   

class SectionLayered(SectionAbstract):
    """
    Represents a layered section, for example CLT.
    """
    
    def getEA(sunit='sunit', lunit='Pa'):
        pass    
    
    def getEIx(sunit='sunit', lunit='Pa'):
        pass
    
    def getEIy(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAx(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAy(sunit='sunit', lunit='Pa'):
        pass

    




# class SectionAggregate(Section):
#     """
#     """
    
#     def getEA(sunit='sunit', lunit='Pa'):
#         pass    
    
#     def getEIx(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getEIy(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getGAx(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getGAy(sunit='sunit', lunit='Pa'):
#         pass
