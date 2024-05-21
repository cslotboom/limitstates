"""
The material library contains material models
"""

from limitstates import MaterialElastic
from limitstates.design.read import _loadMaterialDatabase

__all__ = ["MaterialGlulamCSA_19", "MatCLTLayer_c19", "getGlulamMaterials"]


class MaterialGlulamCSA_19(MaterialElastic):

    """
    Reprsents a glulam material
    """
    type:str = "glulam"
    code:str = "csa086-19"
    E:float
    G:float
    fb:float
    fbneg:float
    fv:float
    fc:float
    fcp:float
    fctn:float
    fctg:float
    fctp:float
    def __init__(self, matDict:dict, sUnit:str='MPa', rhoUnit='kg/m3'):
        self._initUnits(sUnit, rhoUnit)
        self.__dict__.update(matDict)
        self.setG()        

    def _verifyMat(self):
        pass
    
    def setG(self):
        self.G = self.E / 16


class MatCLTLayer_c19(MaterialElastic):
    """
    Material is loaded as file
    """
    type:str='clt'
    code:str = "csa086-19"
    E:float
    G:float
    fb:float
    fbneg:float
    fv:float
    fc:float
    fcp:float
    fctn:float
    fctg:float
    fctp:float    
    def __init__(self, matDict, sUnit = 'MPa', rhoUnit = 'kg/m3'):
        self._initUnits(sUnits, rhoUnits)
        self.__dict__.update(matDict)
        
        self.setE90()
        self.setG0()
        self.setG90()
    
    #TODO: where do these estimates come from?!
    def setE90(self):
        self.E90 = self.E / 30   
        
    def setG0(self):
        self.G = self.E / 16     
        
    def setG90(self):
        self.G90 = self.G / 10     




def getGlulamMaterials(sUnit = 'MPa', rhoUnit = 'kg/m3'):
    """
    Returns all generic CSAo86 materials

    Returns
    -------
    None.

    """
    mats = _loadMaterialDatabase('csa', 'o86', 'c19', "glulam_csa.csv",
                                 MaterialGlulamCSA_19, sUnit, rhoUnit)
    return mats



# def getGlulamMaterialsByName(sUnits = 'MPa', rhoUnits = 'kg/m3'):
#     """
#     Returns all generic CSAo86 materials

#     Returns
#     -------
#     None.

#     """
#     mats = _loadMaterialDatabase('csa', 'o86', 'c19', "glulam_csa.csv",
#                                  MatCLTLayer_c19, sUnits, rhoUnits)
    return mats
    # loadMaterialDatabase()