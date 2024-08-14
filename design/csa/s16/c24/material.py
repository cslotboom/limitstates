"""
The material library contains material models
"""

from limitstates import MaterialElastic

__all__ = ["MaterialSteelCsa19"]


class MaterialSteelCsa19(MaterialElastic):

    """
    An elastic material that has design strengths for glulam. Propreties are
    read from a dictionary
    """
    type:str = "steel"
    code:str = "CSAo86-19"
    species:str = "" # needs to be empty for the repr
    grade:str   = "" # needs to be empty for the repr
    E:float  
    G:float  
    Fy:float 
    rho:float 

    def __init__(self, Fy = 350, E=200000, G = 77000, rho = 8000, 
                 sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        self.Fy = Fy
        self.E = E
        self.G = G
        self.rho = rho
            
    @property
    def name(self):
        myString = f"{self.code} {self.type} {self.Fy}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"
