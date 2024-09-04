"""
Contains common functions for reading material or section databases.
Material DB functions are not inteded for use by user, instead they should use
material files from the specific design library they are targeting.

Some section files are intended for user by users.

"""

import os
from dataclasses import dataclass
from functools import wraps

import pandas as pd
from math import isnan

from .material import MaterialAbstract
from .section import SectionAbstract, SectionRectangle, LayerClt, SectionCLT, LayerGroupClt, SectionSteel, SectionSteelHSS


__all__ = ["getSteelSections", "getRectangularSections"]


filepath = os.path.realpath(__file__)
basedir = os.path.dirname(filepath)
matBaseDir = os.path.join(os.path.dirname(basedir), 'design')

@dataclass
class DBConfig:
    """
    A configuration file, used to load a file from a database.
    Databases are stored in path code/dbTyp/dbname.csv, for example clt 
    csa/clt/prg320_2019   
    
    Parameters
    ----------
    code : str
        The building code to use.
    dbType : str
        The type of object to use for the database, i.e. glulam/clt/steel.
    dbName : str
        The name of the database to use. Typically this is in the form 
        supplier_year_qualifier, e.g. prg320_2019, or supplier_year_qualifier,
        e.g. 
    """
    code:str
    dbType:str
    dbName:str



def _setupLoader(objType):
    
    # @wraps()
    def _loadDBDict(config:DBConfig) -> pd.DataFrame:
        """
        Loads a database using the input configuration file and returns a 
        pd dataframe.
        
        Note that converting a pd dataframe to a dictionary is expensive, 
        so any fitlering should be done before that operation.

        Parameters
        ----------
        config : DBConfig
            The database configuration object.

        Returns
        -------
        pd.DataFrame
            A padas dataframe with the database information in it.

        """
        
        base    = os.path.join(basedir, objType, 'db')
        dbPath  = os.path.join(base, config.code, config.dbType)    
        fileID =  config.dbName + '.csv'
        dbPath  = os.path.join(dbPath, fileID)    
        return pd.read_csv(dbPath)
    
    return _loadDBDict


# @setupLoader
_loadMaterialDBDict = _setupLoader('material')
_loadSectionDBDict  = _setupLoader('section')


# def _loadMaterialDBDict(config:DBConfig) -> pd.DataFrame:
#     """
#     Loads a file and returns the results as a dictionary
#     """
    
#     base    = os.path.join(basedir, 'material', 'db')
#     dbPath  = os.path.join(base, config.code, config.dbType)    
#     fileID =  config.dbName + '.csv'
#     dbPath  = os.path.join(dbPath, fileID)    
#     return pd.read_csv(dbPath)

def _loadMaterialDB(config:DBConfig,
                    MatClass:MaterialAbstract,
                    sUnit:str = 'MPa', 
                    rhoUnit:str = 'kg/m3'):
    """
    Loads a file and returns the results as a dictionary
    """
    
    matdb = _loadMaterialDBDict(config)   
    matDict = matdb.to_dict(orient='index')

    materials = []
    for key in matDict.keys():
        materials.append(MatClass(matDict[key], sUnit=sUnit, rhoUnit = rhoUnit))
    
    return materials

# =============================================================================
# Section read files
# =============================================================================
        
# def _loadSectionDBDict(config:DBConfig) -> pd.DataFrame:
#     """
#     Loads a file and returns the results as a dictionary.
#     Note that converting to a dictionary is expensive, and we want to do 
#     any fitlering before that operation.
#     """
#     base    = os.path.join(basedir, 'section', 'db')
#     dbPath  = os.path.join(base, config.code, config.dbType)    
#     fileID =  config.dbName + '.csv'
#     dbPath  = os.path.join(dbPath, fileID)
#     return pd.read_csv(dbPath)
    
 
def _loadSectionDB(mat:MaterialAbstract, 
                   config:DBConfig,
                   sectionClass:SectionAbstract,
                   lUnit='mm') -> pd.DataFrame:
    """
    Loads a file and returns the results as a dictionary
    """

    sectiondb   = _loadSectionDBDict(config)
    sectionDict = sectiondb.to_dict(orient='index')
    
    sections = []
    for key in sectionDict.keys():
        sections.append(sectionClass(mat, sectionDict[key]), lUnit = lUnit)
    return sections

def _loadSectionRectangular(mat:MaterialAbstract, config:DBConfig, lUnit) -> list[SectionRectangle]:


    sectiondb = _loadSectionDBDict(config)
    sectionDict = sectiondb.to_dict(orient='index')
    
    sections = []
    for key in sectionDict.keys():
        tmpD = sectionDict[key]
        sections.append(SectionRectangle(mat, tmpD['b'], tmpD['d'], lUnit))
    return sections
    

def _getCodeUnits(code):
    
    if code == 'us':
        return 'in'
    else:
        return 'mm'

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

    lUnit = _getCodeUnits(code)
        
    config = DBConfig(code, sectionType, fileName)
    
    return _loadSectionRectangular(mat, config, lUnit)


        
def getSectionTypes(sectionRawDict, section_type: str) -> pd.DataFrame:
    """
    Removes all empty entry from the dataframe.
    """
    return sectionRawDict.loc[sectionRawDict.type == section_type.upper()]



#TODO Evaluate if we can make this a generic steel section class.
sectionDict = {'w':SectionSteel, 'hss':SectionSteelHSS}


def getSteelSections(mat:MaterialAbstract, 
                     code:str, 
                     dbName:str,
                     steelShapeType:str) -> SectionSteel:
    
    steelShapeType = steelShapeType.lower()
    # !!! This is a bandaid
    if '_si' in dbName:
        lUnit =  'mm'
    else:
        lUnit  = _getCodeUnits(code)
    
    # !!! do we actually need a different section for
    if steelShapeType in list(sectionDict.keys()):
        dbName += '_' + steelShapeType.lower()
    else:
        raise Exception(f'Shape {steelShapeType} is not currently supported.')
    
    config      = DBConfig(code, 'steel', dbName)
    rawDbData   = _loadSectionDBDict(config)

    filteredDbData = getSectionTypes(rawDbData, steelShapeType)
    
    filteredDict = filteredDbData.to_dict(orient='index')
    SectionClass = sectionDict[steelShapeType]
    
    # !!! Consider making this a funciton with more logic.
    tmpNameList = dbName.replace('.csv', '').strip(steelShapeType).split('_')
    dbName = ''.join(tmpNameList[0:2])
    
    

    
    sections = [None]*len(filteredDict.keys())
    for ii, key in enumerate(filteredDict.keys()):
        tmpD = filteredDict[key]
        sections[ii] = SectionClass(mat, tmpD, lUnit)
        sections[ii].sectionDB = dbName
    
    return sections




# =============================================================================
# CLT loading functions
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
    

def _getCLTSectionLayers(sectionDict:dict, mats:list, 
                         lUnit:str) -> list[LayerClt]:
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
        
        layerMats.append(LayerClt(layerThicknesses[ii], mat, o==0, lUnit))
    return layerMats



def _loadSectionsCLT(mats:list[[MaterialAbstract, MaterialAbstract]], 
                    config:DBConfig, 
                    lUnit = 'mm', **sectionkwargs) -> list[SectionCLT]:
    """
    An internal function that can be used to load a set of CLT sections given
    input materials that correspond to the grades of each section type.
    
    Parameters
    ----------
    mats : list[[MaterialAbstract, MaterialAbstract]]
        The materials to assign to the strong and weak axis respectively.
    config : DBConfig
        A config object that contains the database file to read from.
    lUnit : string, optional
        The units to use in the section. The default is 'mm'.
    kwargs : dict
        The units to use in the section. The default is 'mm'.

    Returns
    -------
    list[SectionCLT]
        A list of loaded sections.

    """

    tempDict = _loadSectionDBDict(config)
    tempDict = tempDict.to_dict(orient='index')

    sectionsDict = _parseCLTDataFrame(tempDict)
   
    sections = []
    for key in sectionsDict.keys():
        sectionDict = sectionsDict[key]
        layers = LayerGroupClt(_getCLTSectionLayers(sectionDict, mats, lUnit))
        sections.append(SectionCLT(layers, **sectionkwargs))

    return sections
    
# =============================================================================
# Steel Loading functions
# =============================================================================



