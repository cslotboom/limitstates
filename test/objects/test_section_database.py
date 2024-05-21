"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic, SectionRectangle
import pytest


    

def test_geom():
    
    myMat = MaterialElastic(9.5*1000)
    b = 200
    d = 600
    section = SectionRectangle(myMat, b, d)
    
    assert section.A == b * d
    assert section.Ix == b*d**3 / 12
    assert section.Iy == b**3*d / 12
    assert section.J == pytest.approx(1.26401*1e9,0.001)
 
def test_SectionProps():
    
    b = 200
    d = 600
    E = 9.5
    myMat = MaterialElastic(E, sunit='GPa')
    section = SectionRectangle(myMat, b, d)
    
    assert section.getEIx('Pa','m') == pytest.approx(b*d**3 / 12 * E * 1e-3)


if __name__ == '__main__':
    test_geom()
    test_SectionProps()
