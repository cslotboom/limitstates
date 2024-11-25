"""
Contains classes that represent beam bendign diagrams, such as the shear force
diagram (SFD), bending moment diagram (BMD), or 

"""


import hysteresis as hys
import numpy as np
from limitstates import ConverterLength
# ConverterLength


class DesignDiagram:
    """
    Represents a bending moment or shear force diagram.

    Parameters
    ----------
    xyIn : np.ndarray
        The xy points in.
    lUnit : TYPE, optional
        The input units used for length. The default is 'm'.

    Returns
    -------
    None.

    """
    
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
        """
        Returns the x points where y intersections occur in the bmd

        Returns
        -------
        np.ndarray
            The output array/list of points.

        """
        return self.xInflections
    
        
    def getForceAtx(self, x:float|list):
        """
        A function that can be used to calcualte the y values at a set of input
        x points. Linear interpolation is used to determine y where a x point 
        does conencide exactly with a x value in the array.

        Parameters
        ----------
        x : float|list
            The points to calcualte y values at.

        Returns
        -------
        x : np.ndarray
            The y values for each input x.

        """
        
        return np.interp(x, self.xy[:,0], self.xy[:,1])
    
        
    def getMaxForceInRange(self, x1, x2):
        """
        Determines the absolute maximum y value within a range x1 -> x2

        Parameters
        ----------
        x1 : float
            The start of the range.
        x2 : float
            The end of the range. Must be greater than x1.

        Returns
        -------
        float
            The maximum value within the range.

        """
        x = self.xy[:,0]
        y = self.xy[:,1]
        ind1 = np.where(x1 <= x)[0][0]
        ind2 = np.where(x2 <= x)[0][0]
        return max(abs(y[ind1:ind2]))
    
    
    def _initUnits(self, lUnit:str='m'):
        """
        Inititiates the unit of the section.
        """
        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units.    

        Parameters
        ----------
        outputUnit : str
            The unit to convert the current units to.

        Returns
        -------
        float
            The output unit.

        """

        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
    def convertDiagramTo(self, outputUnit:str):
        """
        Converst the diagram to use the input unit for it's x values.

        Parameters
        ----------
        outputUnit : str
            The unit to change the x value of the diagram to.

        Returns
        -------
        None.

        """
        lfactor = self.lConvert(outputUnit)
        self.xyIn[:,0] = self.xyIn[:,0]*lfactor
        self._setCurve(self.xyIn)
        