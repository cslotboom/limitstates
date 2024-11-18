"""
Tests the design of glulam elements according to csa o86
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

import pytest

import numpy as np
mats = o86.loadGlulamMaterialDB()
myMat = mats[0]
sections = o86.loadGlulamSections(myMat)

mySection = sections[12]
L = 6

myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')

def test_Cb():
    Cbx = o86.checkBeamCb(myElement)
    assert Cbx == pytest.approx((L*mySection.d/(mySection.b**2))**0.5)

def test_kLa():
    """ Tests kL case A. """
    # myElement.L
    E = myElement.mat.E
    Fb = myElement.mat.fb
    
    kL = o86.checkKL(9.9, E, Fb)
    
    assert kL == 1

def test_kLb():
    """ Tests kL case B. """
    # myElement.L
    E = myElement.mat.E
    Fb = myElement.mat.fb
    Cb = 10.1
    kL = o86.checkKL(Cb, E, Fb)
    Ck = (0.97*myMat.E / myMat.fb)**0.5
    
    assert kL == pytest.approx(1 - (1/3)*(Cb / Ck)**4)

def test_kLc():
    """ Tests kL case C. """
    # myElement.L
    E = myElement.mat.E
    Fb = myElement.mat.fb
    Cb = 30
    kL = o86.checkKL(Cb, E, Fb)
    Ck = (0.97*myMat.E / myMat.fb)**0.5
    
    assert kL == pytest.approx(0.65*E / (Cb**2*Fb))

def test_kLc2():
    """ Tests kL case C, with kx applied """
    # myElement.L
    E = myElement.mat.E
    Fb = myElement.mat.fb
    Cb = 30
    kL = o86.checkKL(Cb, E, Fb, kx = 0.6)
    Ck = (0.97*myMat.E / myMat.fb)**0.5
    
    assert kL == pytest.approx(0.65*E / (Cb**2*Fb*0.6))




def test_bending_table_1():
    """
    Tests results using glulam selecton tables in CSA o86
    """
    
    mat = mats[3]
    mySection = ls.SectionRectangle(mat, 365, 836)
    
    L = 6
    myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')
    
    
    kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)
    
    Mr = o86.checkMrGlulamBeamSimple(myElement, 1) / 1000
    Vr = o86.checkVrGlulamBeamSimple(myElement, 1) / 1000
    
    EI = mySection.getEIx('mm', 'MPa')
    
    Mrsol = 980 * kzbg
    Vrsol = 366
    EIsol = 220000*10**9
    
    myElement = o86.getBeamColumnGlulamCsa19(12, mySection, 'm')
    kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)

    Wr = o86.checkWrGlulamBeamSimple(myElement, 1) / 1000

    WrSol = 1200 * 12**-0.18
    
    assert Mr == pytest.approx(Mrsol, rel = 0.01)
    assert Vr == pytest.approx(Vrsol, rel = 0.01)
    assert EI == pytest.approx(EIsol, rel = 0.01)
    assert Wr == pytest.approx(WrSol, rel = 0.01)




def test_compression_Design_Example_Cc():
    """
    Tests results using the design example form column checklists in the 
    wood design manual.
    
    Use 175x228 column.
    
    """
    
    mat = mats[-3]
    mySection = ls.SectionRectangle(mat, 175, 228)
    
    Lx = 7
    Ly = 3.5
    myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm', Lx = Lx, Ly = Ly)
    
    Cx, Cy = o86.checkColumnCc(myElement)
    CxSol = 30.7
    CySol = 20
    
    assert Cx == pytest.approx(CxSol, rel = 0.01)
    assert Cy == pytest.approx(CySol, rel = 0.01)


def test_compression_Design_Example_Pr():
    """
    Tests results using the design example form column checklists in the 
    wood design manual.
    
    Use 175x228 column.
    
    """
    
    mat = mats[-3]
    mySection = ls.SectionRectangle(mat, 175, 228)
    
    Lx = 7
    Ly = 3.5
    myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm', Lx = Lx, Ly = Ly)
    
    Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
        
    Prsol = 217 
    
    assert Pr == pytest.approx(Prsol, rel = 0.01)


def test_compression_Table():
    """
    Tests results using the design example from column checklists in the 
    wood design manual.
    
    Use 265x342 column.
    
    """
    
    mat = mats[5]
    mySection = ls.SectionRectangle(mat, 265, 342)
    
    L = 4.5
    myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')    
    Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
    Prsol = 1290 
    assert Pr == pytest.approx(Prsol, rel = 0.01)

    L = 13
    myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')    
    Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
    Prsol = 200 
    assert Pr == pytest.approx(Prsol, rel = 0.01)
    
def test_Interaction_ecc():
    """
    See CSA wood design manual, 5.3 Ex 3 2020
    """
    
    d = 190
    b = 130
    L = 4
    mat2 = mats[2]

    mySection = ls.SectionRectangle(mat2, b, d)
    
    column = o86.getBeamColumnGlulamCsa19(L, mySection)    
    
    Pr = o86.checkPrGlulamColumn(column)
    Prsol = 175*1000
    
    # assert inTol(pr, prsol)
    assert Pr == pytest.approx(Prsol, rel = 0.01)

    e = (d / 2 + 60)/1000
    knet = 1
    Pf = 72.5*1000
    interSolTop = 0.79
    # interSolMid = 0.54
    inter = o86.checkInterEccPfColumn(column, Pf, e, knet)
    assert inter == pytest.approx(interSolTop, rel = 0.01)


    
def test_Interaction_ecc_table():
    """
    Tests a random example from Table
    """
    
    # d = 228
    d = 152
    b = 80
    L = 4
    mat2 = mats[1]

    mySection = ls.SectionRectangle(mat2, b, d)
    column = o86.getBeamColumnGlulamCsa19(L, mySection)    
    
    e = (d)/2 / 1000
    knet = 1
    # Pf = 35.6*1000
    Pf = 24.3*1000
    interSolTop = 1.0
    inter = o86.checkInterEccPfColumn(column, Pf, e, knet)
    assert inter == pytest.approx(interSolTop, rel = 0.02)

if __name__ == "__main__":
    test_Cb()
    test_kLa()
    test_kLb()
    test_kLc2()
    test_bending_table_1()
    
    test_compression_Design_Example_Cc()
    test_compression_Design_Example_Pr()
    test_compression_Table()
    
    test_Interaction_ecc()
    test_Interaction_ecc_table()
