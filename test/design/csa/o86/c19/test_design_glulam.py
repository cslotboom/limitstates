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

myElement = o86.getBeamColumnGlulamCSA19(L, mySection, 'm')

def test_Cb():
    Cbx = o86.getBeamCb(myElement)
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

def test_kzbg():
    
    kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L)
    


def test_table_1():
    """
    Tests results using glulam selecton tables in CSA o86
    """
    
    mat = mats[3]
    mySection = ls.SectionRectangle(mat, 365, 836)
    
    L = 6
    myElement = o86.getBeamColumnGlulamCSA19(L, mySection, 'm')
    
    
    kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)
    
    Mr = o86.checkMrGlulamSimple(myElement, 1) / 1000
    Vr = o86.checkVrGlulamSimple(myElement, 1) / 1000
    
    EI = mySection.getEIx('mm', 'MPa')
    
    Mrsol = 980 * kzbg
    Vrsol = 366
    EIsol = 220000*10**9
    
    myElement = o86.getBeamColumnGlulamCSA19(12, mySection, 'm')
    kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)

    Wr = o86.checkWrGlulamSimple(myElement, 1) / 1000

    WrSol = 1200 * 12**-0.18
    
    assert Mr == pytest.approx(Mrsol, rel = 0.01)
    assert Vr == pytest.approx(Vrsol, rel = 0.01)
    assert EI == pytest.approx(EIsol, rel = 0.01)
    assert Wr == pytest.approx(WrSol, rel = 0.01)


if __name__ == "__main__":
    test_Cb()
    test_kLa()
    test_kLb()
    test_kLc2()
    test_table_1()
    
    
