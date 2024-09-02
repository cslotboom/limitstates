"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa19(345)
steelWSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')

def test_Cr_W():
    """
    Checks results agains values from tables in CISC steel design handbook 
    section 4.
    """
    
    section = ls.getByName(steelWSections, 'W360x463')
    column  = s16.getBeamColumnSteelCSA19(8, section)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 11000    

    assert Cr == pytest.approx(CrSol, rel = 0.01)
    column  = s16.getBeamColumnSteelCSA19(16, section)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 4190    
    assert Cr == pytest.approx(CrSol, rel = 0.01)

    
    section = ls.getByName(steelWSections, 'W310x107')
    column  = s16.getBeamColumnSteelCSA19(6, section)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 2450
    assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    section = ls.getByName(steelWSections, 'W310x107')
    column  = s16.getBeamColumnSteelCSA19(10, section)
    Cr      = s16.checkColumnCr(column) / 1000
    # Mcr = s16.checkSectionMu(section, , 1)
    CrSol = 1230    
    assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    section = ls.getByName(steelWSections, 'W200x46')
    column  = s16.getBeamColumnSteelCSA19(10, section)
    Cr      = s16.checkColumnCr(column) / 1000
    # Mcr = s16.checkSectionMu(section, , 1)
    CrSol = 258    
    assert Cr == pytest.approx(CrSol, rel = 0.01)



if __name__ == "__main__":
    test_Cr_W()
    # test_W_Major()
    # test_W_Minor()
