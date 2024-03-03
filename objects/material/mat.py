"""
Stores information relevant to all materials.
Design dependant material information will be present in 
Material are relevant to design.

"""

from ... units import ConverterStress, ConverterDensity
from functools import partial

class MaterialAbstract:
    
    """
    The common material object. Contains interfaces relevant for all design
    objects.
    """
    E:float
    
    def _initUnits(self, sunit:str='MPa', rhounit='kg/m3'):
        """
        Inititiates the unite of the material.
        """
        self.sUnit      = sunit
        self.sConverter = ConverterStress()
        self.rhoUnit  = rhounit
        self.rhoConverter = ConverterDensity()
    
    def sConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for stress units
        """
        return self.sConverter.getConversionFactor(self.sUnit, outputUnit)
        
    def rhoConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for stress units
        """        
        return self.rhoConverter.getConversionFactor(self.rhoUnit, outputUnit)


class MaterialElastic(MaterialAbstract):

    def __init__(self, E:float, G:float=None, rho=None, 
                 sunit:str='MPa', rhounit='kg/m3'):
        """
        Represents a generic elastic material. This material is code agnostic
        and generally not used in design.
        """
        self._initUnits(sunit,rhounit)
        self.E = E
        self.G = G
        self.rho = rho

        
        