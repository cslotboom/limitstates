"""
Tests if the read functions proprely return database values.

We will use the a specific function from csa o86-19 to check
"""

"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import _loadSectionDBDict, SectionDBConfig, _parseCLTDataFrame, _loadSectionsCLT
from limitstates.design.csa.o86.c19.material import loadCltMatDB
from limitstates import SectionCLT


db = 'clt_prg320_2019.csv'
config = SectionDBConfig('csa', 'clt', db)
    

def test_mats_load():
    """
    Ensures the materials are loaded correctly.
    """
    # Load the material dictionary
    mats = loadCltMatDB(db)
    
    assert mats[0][0].species == 'SPF'
    assert mats[2][1].E == 6500
    assert mats[2][1].E90 == 6500/30
    assert mats[-1][0].fb == 11
    
def test_section_loadandParse():
    """
    Checks that the parse function is creating sections properly.
    """
    tempDict = _loadSectionDBDict(config)
    tempDict = tempDict.to_dict(orient='index')

    sectionsDict = _parseCLTDataFrame(tempDict)
    assert len(sectionsDict[0]['t']) == 3
    assert len(sectionsDict[2]['t']) == 7
    assert len(sectionsDict[0]['o']) == 3
    assert len(sectionsDict[2]['o']) == 7
    assert len(sectionsDict[20]['o']) == 7
    
    assert sectionsDict[20]['name'] == '245 V5'
    
def test_section_read():
    mats = loadCltMatDB(db)
    sections = _loadSectionsCLT(mats, config)
    
    assert len(sections[0].sLayers) == 3
    assert len(sections[0].wLayers) == 1
    
    assert len(sections[1].sLayers) == 5
    assert len(sections[1].wLayers) == 3    # sectionsDict[]

    
if __name__ == '__main__':
    test_mats_load()
    test_section_loadandParse()
    test_section_read()