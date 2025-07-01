"""
The material library contains material models
"""

from limitstates import MaterialElastic
from limitstates.objects.read import _loadMaterialDBDict, _loadMaterialDB, DBConfig, _sortCLTMatDict

__all__ = ["MaterialConcreteCSA24", "MaterialRebarCSA24"]

_glulamConfig = DBConfig('csa', 'glulam', 'csa_o86_2019')

class MaterialConcreteCSA24(MaterialElastic):

    """
    An elastic material that has design strengths for concrete.
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

    def __init__(self, fc:float, amax = 20, ey = 0.0035,
                 sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        # self.__dict__.update(matDict)
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


class MaterialRebarCSA24(MaterialElastic):

    """
    An elastic material that has design strengths for glulam. Propreties are
    read from a dictionary
    """
    type:str = "rebar"
    code:str = "A23-24"
    fy:float
    E:float
    fv:float
    ey:float

    def __init__(self, fy:float = 350, E:float = 200000, ey:float = 0.002, 
                 sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        # self.__dict__.update(matDict)
        
        self.fy = fy
        self.E  = E
        self.ey = ey
        # if 'G' not in self.__dict__:
        #     self.setG()
            
    @property
    def name(self):
        myString = f"{self.code} {self.type} {self.fy}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"

    def _verifyMat(self):
        pass
    
    # def setG(self):
    #     self.G = self.E / 16
