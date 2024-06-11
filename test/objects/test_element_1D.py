"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic, SectionRectangle, getBeamColumn
import pytest


def test_getBeam():
    
    myMat = MaterialElastic(9.5*1000)
    b = 200
    d = 600
    L = 4
    section = SectionRectangle(myMat, b, d)
    myBeam = getBeamColumn(L,section,'m')
    
    assert myBeam.getLength() == L
    
    
    


if __name__ == '__main__':
    test_getBeam()