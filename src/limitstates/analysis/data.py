"""
Contains classes that represent beam bendign diagrams, such as the shear force
diagram (SFD), bending moment diagram (BMD), or 

"""


import hysteresis as hys
import numpy as np
from limitstates import ConverterLength
# ConverterLength


class DesignDiagram:
    
    def __init__(self, xyIn, lUnit= 'm'):
        
        self.xy = np.array(xyIn)
       
        # self.curve.
        self.segments = None
        
        self._initUnits(lUnit)
        self._setCurve(xyIn)
    
    def _setCurve(self, xyIn):
        self.curve = hys.SimpleCurve(xyIn)
        self.curve.setIntersectionInds()
        self.xInflections = self.curve.getXIntersections()[:,0]
        
        
    def getIntersectionCoords(self):
        return self.xInflections
    
    
    
    
    def _initUnits(self, lUnit:str='m'):
        """
        Inititiates the unit of the section.
        """
        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        """
        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
    def convertDiagramTo(self, outputUnit:str):
        lfactor = self.lConvert(outputUnit)
        self.xyIn[:,0] = self.xyIn[:,0]*lfactor
        self._setCurve(self.xyIn)
        