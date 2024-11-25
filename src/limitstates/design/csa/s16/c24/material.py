"""
The material library contains material models
"""

from limitstates import MaterialElastic

__all__ = ["MaterialSteelCsa24"]


class MaterialSteelCsa24(MaterialElastic):
    """
    An material that has design strengths for steel.            

    Parameters
    ----------
    Fy : float, optional
        The reference yield strength for the steel in the the sections units. 
        The default is 350 in MPa.
    E : float, optional
        The reference elastic modulus for the steel in MPa. 
        The default is 200000  in MPa.
    Fu : float, optional
        The reference ultimate strength for the steel. 
        The default is 450  in MPa.
    G : float, optional
        The reference shear modulus for the steel. 
        The default is 77000 in MPa.
    rho : float, optional
        The density for the material. The default is 8000  in kg / m^3.
    sUnit : str, optional
        The units for . The default is 'MPa'.
    rhoUnit : TYPE, optional
        The units for density. The default is 'kg/m3'.
    """
    type:str = "steel"
    code:str = "CSAo86-19"
    species:str = "" # needs to be empty for the repr
    grade:str   = "" # needs to be empty for the repr
    E:float  
    G:float  
    Fy:float 
    rho:float 

    def __init__(self, Fy = 350, E = 200000, Fu = 450, G = 77000, rho = 8000, 
                 sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        self.Fy = Fy
        self.Fu = Fu
        self.E = E
        self.G = G
        self.rho = rho
            
    @property
    def name(self):
        myString = f"{self.code} {self.type} {self.Fy}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"
