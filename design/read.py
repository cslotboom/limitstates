"""
Contains common functions for reading material or section databases.
These are not inteded for use by user.
"""


import pandas as pd
import os
from limitstates import MaterialAbstract

filepath = os.path.realpath(__file__)
basedir = os.path.dirname(filepath)


class AbstractDatabaseLoader:
    type:str = None
    def __init__(self, code:str, matStandard:str, year:str, fileName:str):
        base = os.path.join(basedir, code, matStandard, year)
        self.dbPath = os.path.join(base, self.type, 'databases', fileName) 
    
    def loadDict(self):
        matdb = pd.read_csv(self.dbPath)
        matDict = matdb.to_dict(orient='index')    

    def loadObjects(self):
        pass
        
def _loadMaterialDatabaseDict(code:str,
                             matStandard:str,
                             year:str,                         
                             fileName:str) -> pd.DataFrame:
    """
    Loads a file and returns the results as a dictionary
    """
    base    = os.path.join(basedir, code, matStandard, year)
    dbPath  = os.path.join(base, 'material', 'databases', fileName)    
    matdb   = pd.read_csv(dbPath)
    matDict = matdb.to_dict(orient='index')
    return matDict

def _loadMaterialDatabase(code:str,
                         materialStandard:str,
                         year:str,                         
                         fileName:str,
                         MatClass:MaterialAbstract,
                         sUnit:str = 'MPa', 
                         rhoUnit:str = 'kg/m3'):
    """
    Loads a file and returns the results as a dictionary
    """
    
    matDict = _loadMaterialDatabaseDict(code, materialStandard, year, fileName)   
    
    materials = []
    for key in matDict.keys():
        materials.append(MatClass(matDict[key], sUnit=sUnit, rhoUnit = rhoUnit))
    
    return materials
