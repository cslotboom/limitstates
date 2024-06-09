"""
Contains common functions for reading material or section databases.
Material DB functions are not inteded for use by user, instead they should use
material files from the specific design library they are targeting.

Some section files are intended for user by users.

"""


import pandas as pd
import os
from .material import MaterialAbstract
from .section import SectionAbstract, SectionRectangle
from dataclasses import dataclass

filepath = os.path.realpath(__file__)
basedir = os.path.dirname(filepath)
matBaseDir = os.path.join(os.path.dirname(basedir), 'design')

# class AbstractDatabaseLoader:
#     type:str = None
#     def __init__(self, code:str, matStandard:str, year:str, fileName:str):
#         base = os.path.join(basedir, code, matStandard, year)
#         self.dbPath = os.path.join(base, self.type, 'databases', fileName) 
    
#     def loadDict(self):
#         matdb = pd.read_csv(self.dbPath)
#         matDict = matdb.to_dict(orient='index')    

#     def loadObjects(self):
#         pass

@dataclass
class MaterialDBConfig:
    code:str
    matStandard:str
    year:str
    fileName:str

def _loadMaterialDBDict(config:MaterialDBConfig) -> pd.DataFrame:
    """
    Loads a file and returns the results as a dictionary
    """
    base    = os.path.join(matBaseDir, config.code, config.matStandard, config.year)
    dbPath  = os.path.join(base, 'material', 'db', config.fileName)    
    matdb   = pd.read_csv(dbPath)
    matDict = matdb.to_dict(orient='index')
    return matDict

def _loadMaterialDB(config:MaterialDBConfig,
                    MatClass:MaterialAbstract,
                    sUnit:str = 'MPa', 
                    rhoUnit:str = 'kg/m3'):
    """
    Loads a file and returns the results as a dictionary
    """
    
    matDict = _loadMaterialDBDict(config)   
    
    materials = []
    for key in matDict.keys():
        materials.append(MatClass(matDict[key], sUnit=sUnit, rhoUnit = rhoUnit))
    
    return materials

# =============================================================================
# 
# =============================================================================

@dataclass
class SectionDBConfig:
    code:str
    sectionType:str
    fileName:str

def listSectionDBs(code:str, sectionType:str, fileName:str):
    pass

        
def _loadSectionDBDict(config:SectionDBConfig) -> pd.DataFrame:
    """
    Loads a file and returns the results as a dictionary
    """
    base    = os.path.join(basedir, 'section', 'db')
    dbPath  = os.path.join(base, config.code, config.sectionType, config.fileName)    
    sectiondb   = pd.read_csv(dbPath)
    return sectiondb.to_dict(orient='index')
        
def _loadSectionDB(mat:MaterialAbstract, 
                   config:SectionDBConfig,
                   sectionClass:SectionAbstract,
                   lUnit='mm') -> pd.DataFrame:
    """
    Loads a file and returns the results as a dictionary
    """

    sectionDict = _loadSectionDBDict(config)
    
    sections = []
    for key in sectionDict.keys():
        sections.append(sectionClass(mat, sectionDict[key]), lUnit = lUnit)
    return sections

def _loadSectionRectangular(mat:MaterialAbstract, config:SectionDBConfig, lUnit) -> list[SectionRectangle]:

    sectionDict = _loadSectionDBDict(config)
    
    sections = []
    for key in sectionDict.keys():
        tmpD = sectionDict[key]
        sections.append(SectionRectangle(mat, tmpD['b'], tmpD['d'], lUnit,tmpD))
    return sections
    
    
def getRectangularSections(mat:MaterialAbstract, 
                           code:str, 
                           sectionType:str, 
                           fileName:str):
    """
    Creates a set of rectangular sections from a input database.
    The units the database are in will depend on it's location in

    Parameters
    ----------
    mat : MaterialAbstract
        The material to be applied to the sections.
    code : str
        The code to use, can be one of 'csa' or 'us'.
    sectionType : str
        The type of section to use. Can be one of 'glulam', 'clt', steel.
    fileName : str
        The specific database file to read from.
    lunits : str, optional
        The units the section should be read in. The default is 'mm'.

    Returns
    -------
    None.

    """
    
    if code == 'us':
        lUnit='in'
    else:
        lUnit='mm'
        
    config = SectionDBConfig(code, sectionType, fileName)
    
    return _loadSectionRectangular(mat, config, lUnit)



