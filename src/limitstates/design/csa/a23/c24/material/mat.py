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

    def __init__(self, fc:float, sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        # self.__dict__.update(matDict)
        
        self.fc = fc
        
        if 'E' not in self.__dict__:
            self.setE()
            
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

    def __init__(self, fy:dict, sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        # self.__dict__.update(matDict)
        
        self.fy = fy
        ey = 0.002
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
