"""
The material library contains material models
"""

from ... units import ConverterStress, ConverterDensity
from functools import partial

__all__ = ["MaterialAbstract", "MaterialElastic"]

class MaterialAbstract:
    
    """
    The common material object. Contains interfaces relevant for all design
    objects.
    """
    E:float
    
    def _initUnits(self, sUnit:str='MPa', rhoUnit='kg/m3'):
        """
        Inititiates the unite of the material.
        """
        self.sUnit      = sUnit
        self.sConverter = ConverterStress()
        self.rhoUnit  = rhoUnit
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

    """
    Represents a generic Isotropic elastic material. This material is code 
    agnostic.
    """
    def __init__(self, E:float, G:float=None, rho=None, 
                 sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        self.E = E
        self.G = G
        self.rho = rho

class MaterialElasticIso(MaterialElastic):
    """
    Represents a generic Isotropic elastic material. This material is code 
    agnostic.
    """
    pass

class MaterialElastic(MaterialAbstract):

    """
    Represents a generic Isotropic elastic material. This material is code 
    agnostic.
    """
    def __init__(self, E:float, G:float=None, rho=None, 
                 sunit:str='MPa', rhounit='kg/m3'):
        self._initUnits(sunit, rhounit)
        self.E = E
        self.G = G
        self.rho = rho     