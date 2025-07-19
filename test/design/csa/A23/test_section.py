"""
Hss sections under Cr
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest



# fc = 30
# fy = 400
# mat      = c24.MaterialConcreteCSA24(fc)
# matRebar = c24.MaterialRebarCSA24(fy)

# b = 500
# d = 300
# section = ls.SectionRectangle(mat, b, d)
# config = DBConfig('csa', 'rebar', 'rebar')

# rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
# placer = ls.RebarPlacer(rebarFactory)


# layer1 = placer.getRebarLayer(5, '25M', 375, 300, 50)
# layer2 = placer.getRebarLayer(5, '25M', 425, 300, 50)

# Lbars = ls.RebarCollection([layer1, layer2])

# concreteSection = ls.SectionConcrete(section, Lbars)

# steelSections = getSteelSections(mat, 'csa', 'cisc_12', 'hss')

# def _initColumn(beamName, L):
#     section = ls.getByName(steelSections, beamName)
#     column = s16.getBeamColumnSteelCsa24(L, section, 'mm')
#     return column

def test_Mr():
    """
    Mr from compression tables in blue book
    """
    fc = 30
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    assert mat.fc == 30
    assert matRebar.fy == 400
    # Cr      = s16.checkColumnCr(column) / 1000
    # CrSol = 542
    # assert Cr == pytest.approx(CrSol, rel = 0.02)
    
    # column = _initColumn('HSS254x152x9.5', 12000)
    # Cr      = s16.checkColumnCr(column) / 1000
    # CrSol = 317
    # assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    # column = _initColumn('HSS254x152x9.5', 6000)
    # Cr      = s16.checkColumnCr(column) / 1000
    # CrSol = 992
    # assert Cr == pytest.approx(CrSol, rel = 0.01)
    
    
    # #Unsupported Check
    # column = _initColumn('HSS152x152x9.5', 8000)
    # Cr      = s16.checkColumnCr(column) / 1000
    # CrSol = 421
    # assert Cr == pytest.approx(CrSol, rel = 0.01)


# if __name__ == "__main__":
#     test_fc()

