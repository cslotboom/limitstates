"""
Tests if the fire sections instantiat proprely.
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

import numpy as np
import pytest

mats = o86.loadGlulamMaterialDB()
port = o86.GypusmFlatCSA19(['12.7mm'])


def test_table_1():
    """
    Tests results using glulam selecton tables in CSA o86
    """
    
    myMat = mats[2]
    section = ls.SectionRectangle(myMat, 215, 456)
    L = 7
    myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')
    FRR = 60
    FRR = o86.getFRRfromFireConditions(FRR)
    o86.setFireSectionGlulamCSA(myElement, FRR)   
        
    knet = o86.kdfi*o86.kfi['glulam']
    
    bfsol = 117
    dfsol = 407
    assert myElement.designProps.sectionFire.b == pytest.approx(bfsol, rel = 0.01)
    assert myElement.designProps.sectionFire.d == pytest.approx(dfsol, rel = 0.01)

    Mr = o86.checkMrGlulamBeamSimple(myElement, knet, useFire=True) / 1000

    kzbg = o86.checkKzbg(section.b, section.d, myElement.member.L*1000)
    Mrsol = 130 * kzbg

    
    assert Mr == pytest.approx(Mrsol, rel = 0.02)
    
    
def test_table_2():
    """
    Tests results using glulam selecton tables in the Wood Design Manual 2020
    D.fir-L 24f-E
    """
    
    myMat = mats[0]
    section = ls.SectionRectangle(myMat, 265, 532)
    L = 6
    myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')


    FRR = 45
    FRR = o86.getFRRfromFireConditions(FRR)
    o86.setFireSectionGlulamCSA(myElement, FRR)
    
    L = 6
    
    knet = o86.kdfi*o86.kfi['glulam']
    Mr = o86.checkMrGlulamBeamSimple(myElement, knet, useFire=True) / 1000
    Vr = o86.checkVrGlulamBeamSimple(myElement, knet, useFire=True) / 1000
    
    
    kzbg = o86.checkKzbg(section.b, section.d, myElement.member.L*1000)
    Mrsol = 363 * kzbg
    Vrsol = 192
    
    assert Mr == pytest.approx(Mrsol, rel = 0.01)
    assert Vr == pytest.approx(Vrsol, rel = 0.01)

    
def test_compression_example_1():
    """
    Tests results using example 3 on page 827 of the wood design manual.
    """
    
    myMat = mats[-3]
    b = 215
    d = 304
    section = ls.SectionRectangle(myMat, b, d)
    L = 9
    Lx = 4.5
    Ly = 4.5
    port = o86.GypusmFlatCSA19(['12.7mm'])

    column = o86.getBeamColumnGlulamCsa19(L, section, 'm', port,
                                          Lx = Lx, Ly = Ly)
        
    FRR = [60,60,60,60]
    o86.setFireSectionGlulamCSA(column, FRR)
    assert column.designProps.sectionFire.b == pytest.approx(138, rel = 0.01)
    assert column.designProps.sectionFire.d == pytest.approx(227, rel = 0.01)
    
    knet = o86.kdfi*o86.kfi['glulam']

    Pr = o86.checkPrGlulamColumn(column, knet, useFire=True)
    Prsol = 228*1000
    assert Pr == pytest.approx(Prsol, rel = 0.01)
    
def test_compression_example2():
    """
    Tests results using example 4 on page 827 of the wood design manual.
    """
    
    myMat = mats[-3]
    b = 215
    d = 304
    section = ls.SectionRectangle(myMat, b, d)
    L = 7
    Ly = 3.5
    port = o86.GypusmFlatCSA19(['12.7mm'])

    column = o86.getBeamColumnGlulamCsa19(L, section, 'm', port, Ly = Ly)
        
    # o86.FireConditions.
    FRR = [60,60,60,60]
    o86.setFireSectionGlulamCSA(column, FRR)
    
    knet = o86.kdfi*o86.kfi['glulam']

    Pr = o86.checkPrGlulamColumn(column, knet, useFire=True)
    Prsol = 260*1000
    assert Pr == pytest.approx(Prsol, rel = 0.01)

    
def test_compression_table():
    """
    Tests results using glulam selecton tables in the Wood Design Manual 2020
    D.fir-L 24f-E
    """
    
    myMat = mats[-3]
    b = 215
    d = 266
    section = ls.SectionRectangle(myMat, b, d)
    L = 5.5
    column = o86.getBeamColumnGlulamCsa19(L, section, 'm')



    FRR = [60,60,60,60]
    o86.setFireSectionGlulamCSA(column, FRR)
    knet = o86.kdfi*o86.kfi['glulam']

    Pr = o86.checkPrGlulamColumn(column, knet, useFire=True)
    Prsol = 58.1*1000
    
    assert Prsol == pytest.approx(Pr, rel = 0.01)
    # assert Vr == pytest.approx(Vrsol, rel = 0.01)

if __name__ == "__main__":
    test_table_1()
    test_table_2()
    test_compression_example_1()
    test_compression_example2()
    test_compression_table()