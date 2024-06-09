"""
The material library contains material models
"""

from limitstates import MaterialElastic
from limitstates.objects.read import _loadMaterialDB, MaterialDBConfig

__all__ = ["MaterialGlulamCSA19", "MaterialCLTLayerCSA19", 
           "loadGlulamMaterialDB", "loadGlulamMaterial"]

_glulamConfig = MaterialDBConfig('csa', 'o86', 'c19', "glulam_csa.csv")

class MaterialGlulamCSA19(MaterialElastic):

    """
    An elastic material that has design strengths for glulam. Propreties are
    read from a dictionary
    """
    type:str = "glulam"
    code:str = "CSAo86-19"
    species:str = "" # needs to be empty for the repr
    grade:str   = "" # needs to be empty for the repr
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
        if 'G' not in self.__dict__:
            self.setG()
            
    @property
    def name(self):
        myString = f"{self.code} {self.type} {self.species} {self.grade}"
        return ' '.join(myString.split())
    
    def __repr__(self):
        return f"<limitstates {self.name} material.>"

    def _verifyMat(self):
        pass
    
    def setG(self):
        self.G = self.E / 16

class MaterialCLTLayerCSA19(MaterialElastic):
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
        self._initUnits(sUnit, rhoUnit)
        self.__dict__.update(matDict)
        
        if 'E90' not in self.__dict__:
            self.setE90()
        if 'G' not in self.__dict__:
            self.setG0()
        if 'G90' not in self.__dict__:
            self.setG90()
    
    #TODO: where do these estimates come from?!
    def setE90(self):
        self.E90 = self.E / 30   
        
    def setG0(self):
        self.G = self.E / 16     
        
    def setG90(self):
        self.G90 = self.G / 10     

def loadGlulamMaterialDB() -> list[MaterialGlulamCSA19]:
    """
    Returns all CSAo86-19 glulam materials as defined in CSAo86, 
    Strengths are as defined in table 7-2 in the units of MPa. 
    There three grades are considered: 
        DF, SPF, HF. 
        
    Densities are defined in table A.11
    
    Note, for HF, the density of outer laminations are DF in glulam, so a 
    higher density can typically be used for connectors.

    Returns
    -------
    None.

    """
    sUnit = 'MPa'
    rhoUnit = 'kg/m3'
    mats = _loadMaterialDB(_glulamConfig, MaterialGlulamCSA19, sUnit, rhoUnit)
    return mats

def loadGlulamMaterial(species:str, grade:str) -> MaterialGlulamCSA19:

    """
    Returns a specific CSAo86-19 glulam materials as defined in CSAo86.
    
    Strengths are as defined in table 7-2 in the units of MPa. 
    There three grades are considered: 
        DF, SPF, HF. 
        
    Densities are defined in table A.11
    
    Note, for HF, the density of outer laminations are DF in glulam, so a 
    higher density can typically be used for connectors.
    
    Parameters
    ----------
    species : str
        The species of glulam, one of DF, SPF, or HF.
    grade : str
        The grade of glulam, as defined in table 7-2
    
    """
    mats = loadGlulamMaterialDB()
    matOut = None
    for mat in mats:
        if species == mat.species and grade == mat.grade:
            matOut = mat
    if not matOut:
        raise Exception(f"No material with species {species} and grade {grade} found in database.")
    
    return matOut
