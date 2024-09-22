"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic
from limitstates.objects.read import getRectangularSections, _loadSectionDBDict, DBConfig, getSteelSections
import pytest


import time

def test_load_gl():
    
    myMat = MaterialElastic(9.5*1000)

    sections = getRectangularSections(myMat,'csa', 'glulam', 'csa_o86_2019')


    assert sections[2].b == 76
    assert sections[2].d == 184
    assert sections[2].Ix == pytest.approx(39453525,0.001)
    assert sections[2].rx == pytest.approx(53, 0.01)
    assert sections[2].ry == pytest.approx(22, 0.01)
 

def test_load_steel():  
    
    myMat = MaterialElastic(200*1000)

    sections = getSteelSections(myMat, 'us', 'aisc_16_si', 'W')

    assert sections[5].d == 1090
    assert sections[5].Ix == pytest.approx(8660*1e6,0.01)
    assert sections[38].kdet == pytest.approx(87.3,0.01)



if __name__ == '__main__':
    test_load_gl()
    test_load_steel()
