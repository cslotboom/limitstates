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
    myElement = o86.getBeamColumnGlulamCSA19(L, section, 'm')
    FRR = 60
    o86.setFireSectionGlulamCSA(myElement, FRR)   
        
    knet = o86.kdfi*o86.kfi['glulam']
    
    bfsol = 117
    dfsol = 407
    assert myElement.designProps.fireSection.b == pytest.approx(bfsol, rel = 0.01)
    assert myElement.designProps.fireSection.d == pytest.approx(dfsol, rel = 0.01)

    Mr = o86.checkMrGlulamBeamSimple(myElement, knet, useFire=True) / 1000
    Vr = o86.checkVrGlulamBeamSimple(myElement, knet, useFire=True) / 1000

    kzbg = o86.checkKzbg(section.b, section.d, myElement.member.L*1000)
    Mrsol = 130 * kzbg
    Vrsol = 130 * kzbg

    
    assert Mr == pytest.approx(Mrsol, rel = 0.02)
    # assert Vr == pytest.approx(Vrsol, rel = 0.01)
    
    
def test_table_2():
    """
    Tests results using glulam selecton tables in CSA o86
    D.fir-L 24f-E
    """
    
    myMat = mats[0]
    section = ls.SectionRectangle(myMat, 265, 532)
    L = 6
    myElement = o86.getBeamColumnGlulamCSA19(L, section, 'm')


    FRR = 45
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
    
    # L = 16
    # myElement = o86.getBeamColumnGlulamCSA19(L, section, 'm')
    # o86.setFireSectionGlulamCSA(myElement, FRR)

    # Wr = o86.checkWrGlulamBeamSimple(myElement, knet, useFire=True) / 1000

    # WrSol = 783 * L**-0.18
    
    
    # assert Wr == pytest.approx(WrSol, rel = 0.01)


if __name__ == "__main__":
    test_table_1()
    test_table_2()