"""
The material library contains material models
"""

from limitstates import MaterialElastic
from limitstates.units import ConverterLength

__all__ = ["MaterialConcreteCSA24", "MaterialRebarCSA24"]

class MaterialConcreteCSA24(MaterialElastic):
    """
    An elastic material that has design strengths for concrete.
    The elastic modulus is set using the provided fc input value.

    Parameters
    ----------
    fc : float
        The compressive strength of the concrete.
    amax : float, optional
        The maximum aggregate size in units lUnit.
    ey : float, optional
        The yield strain of the concrete.
    sUnit : str, optional
        The stress units to use for the material. The default is 'MPa'.
    rhoUnit : str, optional
        The density units to use for the material. The default is 'kg/m3'.
    lUnit : str, optional
        An optional name for the material. By default is 'Elastic Material'.
    """
    
    type:str = "concrete"
    code:str = "A23-24"
    fc:float
    E:float
    G:float
    fv:float
    ft:float
    alpha:float = 0.8
    beta:float = 0.9

    def __init__(self, fc: float, amax: float = 20, ey: float = 0.0035,
                 sUnit: str = 'MPa', rhoUnit: str = 'kg/m3', 
                 lUnit: str = 'mm'):
        self._initUnits(sUnit, rhoUnit)
        self._initLUnit(lUnit)
        self.ey = ey
        
        self.fc = fc
        self.amax = amax
        
        if 'E' not in self.__dict__:
            self.setE()
            
        self._setAplha()
        self._setBeta()
        
    def _setAplha(self):
        self.alpha = 0.85 - 0.0015*self.fc
        
    def _setBeta(self):
        self.beta = 0.97 - 0.0025*self.fc
    
    
    @property
    def name(self):
        myString = f"{self.code} {self.type} {int(self.fc)}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"

    def setE(self):
        self.E = 1
    
    def _initLUnit(self, lUnit:str):
        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
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
        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)

class MaterialRebarCSA24(MaterialElastic):
    """
    An CSA A23.3-24 elastic material that has design strengths for steel.

    Parameters
    ----------
    fy : float, optional
        The yield stress of the steel in Sunit. The default is 400.
    E : float, optional
        The elastic modulus for the steel in Sunit. The default is 200000.
    E : float, optional
        The shear modulus for the steel in Sunit. The default is 80000.
    ey : float, optional
        The yeild strain for the steel. The default is 0.0002.
    sUnit : str, optional
        The stress units used. The default is 'MPa'.
    rhoUnit : TYPE, optional
        The density units used. The default is 'kg/m3'.

    Returns
    -------
    None.

    """
    type:str = "rebar"
    code:str = "A23-24"
    fy:float
    E:float
    fv:float
    ey:float

    def __init__(self, fy:float = 400, E:float = 200000, G:float = 80000, 
                 ey:float = 0.002, 
                 sUnit:str='MPa', rhoUnit='kg/m3'):

        self._initUnits(sUnit, rhoUnit)
        self.fy = fy
        self.E  = E
        self.G  = G
        self.ey = ey

            
    @property
    def name(self):
        myString = f"{self.code} {self.type} {self.fy}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"

    def _verifyMat(self):
        pass

        