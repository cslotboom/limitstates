"""
Hss sections under Cr
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections


mat = s16.MaterialSteelCsa24(350)
steelSections = getSteelSections(mat, 'csa', 'cisc_12', 'hss')

def _initColumn(beamName, L):
    section = ls.getByName(steelSections, beamName)
    column = s16.getBeamColumnSteelCsa24(L, section, 'mm')
    return column

def test_Cr_HSS():
    """
    Mr from compression tables in blue book
    """
    column = _initColumn('HSS127x127x7.9', 4400)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 542
    assert Cr == pytest.approx(CrSol, rel = 0.02)
    
    column = _initColumn('HSS254x152x9.5', 12000)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 317
    assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    column = _initColumn('HSS254x152x9.5', 6000)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 992
    assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    
    #Unsupported Check
    column = _initColumn('HSS152x152x9.5', 8000)
    Cr      = s16.checkColumnCr(column) / 1000
    CrSol = 421
    assert Cr == pytest.approx(CrSol, rel = 0.01)


if __name__ == "__main__":
    test_Cr_HSS()

