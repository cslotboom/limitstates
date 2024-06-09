"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic, SectionRectangle
from limitstates.objects.read import getRectangularSections
import pytest


    

def test_load():
    
    myMat = MaterialElastic(9.5*1000)

    sections = getRectangularSections(myMat,'csa', 'glulam', 'csa-19.csv')


    assert sections[2].b == 76
    assert sections[2].d == 184
    assert sections[2].Ix == pytest.approx(39453525,0.001)
    assert sections[2].rx == pytest.approx(53, 0.01)
    assert sections[2].ry == pytest.approx(22, 0.01)
 



if __name__ == '__main__':
    test_load()
