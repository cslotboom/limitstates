"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic
from limitstates.objects.read import getRectangularSections, _loadSectionDBDict, SectionDBConfig, getSteelSections
import pytest

from FEdesign.structobj import loadSISectionsW

import time

def test_load_gl():
    
    myMat = MaterialElastic(9.5*1000)

    sections = getRectangularSections(myMat,'csa', 'glulam', 'csa-19.csv')


    assert sections[2].b == 76
    assert sections[2].d == 184
    assert sections[2].Ix == pytest.approx(39453525,0.001)
    assert sections[2].rx == pytest.approx(53, 0.01)
    assert sections[2].ry == pytest.approx(22, 0.01)
 

def test_load_steel():
    
    myMat = MaterialElastic(200*1000)
    config = SectionDBConfig('us', 'steel', 'aisc_16_si.csv')
    
    t1 = time.time()
    myDict = _loadSectionDBDict(config)
    
    sections = myDict.loc[myDict.Type == 'W']
    tempDict = sections.to_dict(orient='index')

    # sections = getRectangularSections(myMat, )
    t2 = time.time()
    
    
    sections = loadSISectionsW(myMat)
    t3 = time.time()
    print(t2-t1)
    print(t3-t2)


    sections = getSteelSections(myMat, 'us', 'aisc_16_si.csv', 'W')

    assert sections[2].b == 76
    # assert sections[2].d == 184
    # assert sections[2].Ix == pytest.approx(39453525,0.001)
    # assert sections[2].rx == pytest.approx(53, 0.01)
    # assert sections[2].ry == pytest.approx(22, 0.01)
 


if __name__ == '__main__':
    test_load_gl()
    test_load_steel()
