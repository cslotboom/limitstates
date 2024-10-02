"""
The material library contains material models
"""

from ... units import ConverterStress, ConverterDensity

__all__ = ["MaterialAbstract", "MaterialElastic"]

class MaterialAbstract:
    """
    A base class common to all material objects. It Contains interfaces 
    relevant for all design, including unit initiation and converters.
    objects.
    """
    E:float
    
    def _initUnits(self, sUnit:str='MPa', rhoUnit='kg/m3'):
        """
        Inititiates the units of the material.
        Parameters
        ----------
        sUnit : str, optional
            The stress units to use for the material. The default is 'MPa'.
        rhoUnit : str, optional
            The density units to use for the material. The default is 'kg/m3'.

        """

        self.sUnit      = sUnit
        self.sConverter = ConverterStress()
        self.rhoUnit  = rhoUnit
        self.rhoConverter = ConverterDensity()
    
    def sConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        in stress units.
        
        Parameters
        ----------
        outputUnit : str
            The desired output unit for stress.

        Returns
        -------
        float
            The conversion factor between the base unit and the output unit.

        """
        return self.sConverter.getConversionFactor(self.sUnit, outputUnit)
        
    def rhoConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for density.
        
        Parameters
        ----------
        outputUnit : str
            The desired output unit for stress.

        Returns
        -------
        float
            The conversion factor between the base unit and the output unit.

        """        
        return self.rhoConverter.getConversionFactor(self.rhoUnit, outputUnit)

class MaterialElastic(MaterialAbstract):
    """
    The elastic material represents a generic Isotropic elastic material. 
    This material is code agnostic and contains no strenght information.

    Parameters
    ----------
    E : float
        The elastic modulus for the sections, in units of sUnit.
    G : float, optional
        The shear modulus for the sections, in units of sUnit.
    rho : float, optional
        The density of the material in units of mass per unit of volume. 
        The default is None.
    sUnit : str, optional
        The stress units to use for the material. The default is 'MPa'.
    rhoUnit : str, optional
        The density units to use for the material. The default is 'kg/m3'.

    """

    def __init__(self, E:float, G:float=None, rho=None, 
                 sUnit:str='MPa', rhoUnit='kg/m3', name=None):

        self._initUnits(sUnit, rhoUnit)
        self.E = E
        self.G = G
        self.rho = rho
        
        if name == None:
            name = 'Elastic Material'
        
        self.name = name
