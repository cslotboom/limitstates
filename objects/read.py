"""
Contains common functions for reading material or section databases.
Material DB functions are not inteded for use by user, instead they should use
material files from the specific design library they are targeting.

Some section files are intended for user by users.

"""


import pandas as pd
import os
from math import isnan

from .material import MaterialAbstract
from .section import SectionAbstract, SectionRectangle, LayerClt, SectionCLT, LayerGroupClt
from dataclasses import dataclass

filepath = os.path.realpath(__file__)
basedir = os.path.dirname(filepath)
matBaseDir = os.path.join(os.path.dirname(basedir), 'design')

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
# Section read files
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
        The type of section to use. 
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



# =============================================================================
# 
# =============================================================================


def _sortCLTMatDict(cltMatDBDict:dict)->list[[dict,dict]]:
    """
    A function used by other internal client functions to sort a material data
    base into other funcitons
    A function that is used to sort through a material database. The material
    database will have information for two materials
    
    Sorts the CLT dictionary so it has a list for each of the two materials
    in the clt section, i.e. the strong and weak layer
    """
    matDicts = {}
    for key in cltMatDBDict.keys():
        subDict = cltMatDBDict[key]
        dictStrong   = {}
        dictWeak  = {}
        for subKey in subDict.keys():
            val = subDict[subKey]
            
            # Set the weak axis
            if 'W' in subKey:
                subKeyMod = subKey.replace('W','')
                dictWeak[subKeyMod] = val
            
            # Set the strong axis
            elif 'S' in subKey:
                subKeyMod = subKey.replace('S','')
                dictStrong[subKeyMod] = val        
            
            # set propreties common to both materials, e.g. rho.
            else:
                dictStrong[subKey] = val
                dictWeak[subKey] = val
            
        matDicts[subDict['grade']] = [dictStrong, dictWeak]
    return matDicts

def _parseCLTDataFrame(matDfDict):
    """
    Modfies the orginal raw dataframe dictionary, converting thickneses and 
    layer orientations into a list for each variable.
    All other attributes will remain the same.
    """
    newMatDict = {}    
    for key in matDfDict.keys():
        tTemp = []
        oTemp = []
        parsedMatDict = {}
        
        matDict = matDfDict[key]
        for matKey in matDict.keys():
            val = matDict[matKey]
            
            if matKey[0] == 't' and not isnan(val):
                tTemp.append(val)
                continue
            
            #collect orientation to lists.
            elif matKey[0] == 'o' and not isnan(val):
                oTemp.append(val)    
                continue
            
            # store standard values without modifying them.
            elif (not matKey[0] == 't') and (not matKey[0] == 'o'):
                parsedMatDict[matKey] = val
            
        parsedMatDict['t'] = tTemp
        parsedMatDict['o'] = oTemp
        
        newMatDict[key] = parsedMatDict
        
    return newMatDict


def _getLayerInd(cltGrade, mats):
    """
    Finds the index of the clt grade to use.
    """
    for ii in range(len(mats)):
        if mats[ii][0].grade == cltGrade:
            return ii
    

def _getCLTSectionLayers(sectionDict:dict, mats:list) -> list[LayerClt]:
    """
    Creates the group of layers for the CLT section.

    Parameters
    ----------
    sectionDict : dict
        The input section dictionary containing geometry information.
    mats : list
        The input material list containing all possible materials.

    Returns
    -------
    layerMats : list[LayerClt]
        A list of the output layers, with the correct materials assigned..

    """
    
    
    layerThicknesses = sectionDict['t']
    layerOrientations = sectionDict['o']
    cltGrade = sectionDict['grade']
    
    Nlayer = len(layerThicknesses)
    
    ind = _getLayerInd(cltGrade, mats)
    strongMat, weakMat = mats[ind]
    
    layerMats = []
    for ii in range(Nlayer):
        o = layerOrientations[ii]       
        if o == 0:
            mat = strongMat
        elif o == 90:
            mat = weakMat
        else:
            raise Exception(f"Recieved layer orientation of {o}, \
                            expected 0 or 90")
        
        layerMats.append(LayerClt(layerThicknesses[ii], mat, o==0))
    return layerMats



def _loadSectionsCLT(mats:list[[MaterialAbstract, MaterialAbstract]], 
                    config:SectionDBConfig, 
                    lUnit = 'mm') -> list[SectionCLT]:
    """
    An internal function that can be used to load a set of CLT sections given
    input materials that correspond to the grades of each section type.
    
    Parameters
    ----------
    mats : list[[MaterialAbstract, MaterialAbstract]]
        DESCRIPTION.
    config : SectionDBConfig
        DESCRIPTION.
    lUnit : TYPE, optional
        DESCRIPTION. The default is 'mm'.

    Returns
    -------
    list[SectionCLT]
        DESCRIPTION.

    """

    tempDict = _loadSectionDBDict(config)
    sectionsDict = _parseCLTDataFrame(tempDict)
   
    sections = []
    for key in sectionsDict.keys():
        sectionDict = sectionsDict[key]
        layerMats = LayerGroupClt(_getCLTSectionLayers(sectionDict, mats))
        sections.append(SectionCLT(layerMats, sectionDict))

    return sections
    
