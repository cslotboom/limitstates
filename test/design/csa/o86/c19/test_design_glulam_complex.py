"""
Tests the design of glulam elements according to csa o86 where loading 
conditions are complex, i.e. cantilevers, laterally unsupported beams, etc.


"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86
import planesections as ps

import pytest
import numpy as np

width = 175 # Section width in mm
depth = 608 # Section depth in mm
length = 8  # Beam length in m
supportPositions = [0, 5]

myMat       = o86.loadGlulamMaterial('SPF', '20f-E')
mySection   = ls.SectionRectangle(myMat, width, depth)

# We set up a custom member
pinSupport      = ls.SupportTypes2D.PINNED.value
rollerSupport   = ls.SupportTypes2D.ROLLER.value
freeSupport     = ls.SupportTypes2D.FREE.value
n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
n2 = ls.Node([supportPositions[1], 0.], 'm', support = rollerSupport)
n3 = ls.Node([length, 0.], 'm', support = freeSupport)
line1  = ls.getLineFromNodes(n1, n2)
line2  = ls.getLineFromNodes(n2, n3)
member = ls.Member([n1, n2, n3], [line1, line2])


designProps = o86.DesignPropsGlulam19()
myElement   = o86.BeamColumnGlulamCsa19(member, mySection, designProps)
beamPs      = ls.convertBeamColumnToPlanesections(myElement)


"""
Define the beam nodes loads
"""
kN = 1000*1.5
q = [0.,-10*kN]
beamPs.addVerticalLoad(3, -50*kN)
beamPs.addDistLoad(0, length, q) 
analysis = ps.OpenSeesAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)


bmd = ls.DesignDiagram(np.column_stack(beamPs.getBMD()))

interCoords = bmd.getIntersectionCoords() * 1000
Linflect, kzbg = o86.checkBMDkzbg(interCoords, width, depth)

Lsegs, classSegs = o86.getElemenklSegments(myElement)


def test_checkBMDkzbg():
    
    _, kzbg = o86.checkBMDkzbg(interCoords, width, depth)
    
    L1 = interCoords[1]
    L2 = interCoords[2] - interCoords[1]
    
    k1 = o86.checkKzbg(width, depth, L1)
    k2 = o86.checkKzbg(width, depth, L2)

    assert k1 == pytest.approx(kzbg[0])
    assert k2 == pytest.approx(kzbg[1])

def test_SegmentClassification():
    Lsegs, classSegs = o86.getElemenklSegments(myElement)
    
 
    assert 5 == pytest.approx(Lsegs[0])
    assert 3 == pytest.approx(Lsegs[1])   
     
    assert 1.92 == pytest.approx(classSegs[0])
    assert 1.92 == pytest.approx(classSegs[1])

    
    # assert Cbx == pytest.approx((L*mySection.d/(mySection.b**2))**0.5)

# def test_kLa():
#     """ Tests kL case A. """
#     # myElement.L
#     E = myElement.mat.E
#     Fb = myElement.mat.fb
    
#     kL = o86.checkKL(9.9, E, Fb)
    
#     assert kL == 1

# def test_kLb():
#     """ Tests kL case B. """
#     # myElement.L
#     E = myElement.mat.E
#     Fb = myElement.mat.fb
#     Cb = 10.1
#     kL = o86.checkKL(Cb, E, Fb)
#     Ck = (0.97*myMat.E / myMat.fb)**0.5
    
#     assert kL == pytest.approx(1 - (1/3)*(Cb / Ck)**4)

# def test_kLc():
#     """ Tests kL case C. """
#     # myElement.L
#     E = myElement.mat.E
#     Fb = myElement.mat.fb
#     Cb = 30
#     kL = o86.checkKL(Cb, E, Fb)
#     Ck = (0.97*myMat.E / myMat.fb)**0.5
    
#     assert kL == pytest.approx(0.65*E / (Cb**2*Fb))

# def test_kLc2():
#     """ Tests kL case C, with kx applied """
#     # myElement.L
#     E = myElement.mat.E
#     Fb = myElement.mat.fb
#     Cb = 30
#     kL = o86.checkKL(Cb, E, Fb, kx = 0.6)
#     Ck = (0.97*myMat.E / myMat.fb)**0.5
    
#     assert kL == pytest.approx(0.65*E / (Cb**2*Fb*0.6))




# def test_bending_table_1():
#     """
#     Tests results using glulam selecton tables in CSA o86
#     """
    
#     mat = mats[3]
#     mySection = ls.SectionRectangle(mat, 365, 836)
    
#     L = 6
#     myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')
    
    
#     kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)
    
#     Mr = o86.checkMrGlulamBeamSimple(myElement, 1) / 1000
#     Vr = o86.checkVrGlulamBeamSimple(myElement, 1) / 1000
    
#     EI = mySection.getEIx('mm', 'MPa')
    
#     Mrsol = 980 * kzbg
#     Vrsol = 366
#     EIsol = 220000*10**9
    
#     myElement = o86.getBeamColumnGlulamCsa19(12, mySection, 'm')
#     kzbg = o86.checkKzbg(mySection.b, mySection.d, myElement.member.L*1000)

#     Wr = o86.checkWrGlulamBeamSimple(myElement, 1) / 1000

#     WrSol = 1200 * 12**-0.18
    
#     assert Mr == pytest.approx(Mrsol, rel = 0.01)
#     assert Vr == pytest.approx(Vrsol, rel = 0.01)
#     assert EI == pytest.approx(EIsol, rel = 0.01)
#     assert Wr == pytest.approx(WrSol, rel = 0.01)




# def test_compression_Design_Example_Cc():
#     """
#     Tests results using the design example form column checklists in the 
#     wood design manual.
    
#     Use 175x228 column.
    
#     """
    
#     mat = mats[-3]
#     mySection = ls.SectionRectangle(mat, 175, 228)
    
#     Lex = 7
#     Ley = 3.5
#     myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm', Lex = Lex, Ley = Ley)
    
#     Cx, Cy = o86.checkColumnCc(myElement)
#     CxSol = 30.7
#     CySol = 20
    
#     assert Cx == pytest.approx(CxSol, rel = 0.01)
#     assert Cy == pytest.approx(CySol, rel = 0.01)


# def test_compression_Design_Example_Pr():
#     """
#     Tests results using the design example form column checklists in the 
#     wood design manual.
    
#     Use 175x228 column.
    
#     """
    
#     mat = mats[-3]
#     mySection = ls.SectionRectangle(mat, 175, 228)
    
#     Lex = 7
#     Ley = 3.5
#     myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm', Lex = Lex, Ley = Ley)
    
#     Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
        
#     Prsol = 217 
    
#     assert Pr == pytest.approx(Prsol, rel = 0.01)


# def test_compression_Table():
#     """
#     Tests results using the design example from column checklists in the 
#     wood design manual.
    
#     Use 265x342 column.
    
#     """
    
#     mat = mats[5]
#     mySection = ls.SectionRectangle(mat, 265, 342)
    
#     L = 4.5
#     myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')    
#     Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
#     Prsol = 1290 
#     assert Pr == pytest.approx(Prsol, rel = 0.01)

#     L = 13
#     myElement = o86.getBeamColumnGlulamCsa19(L, mySection, 'm')    
#     Pr = o86.checkPrGlulamColumn(myElement, 1) / 1000
#     Prsol = 200 
#     assert Pr == pytest.approx(Prsol, rel = 0.01)
    
# def test_Interaction_ecc():
#     """
#     See CSA wood design manual, 5.3 Ex 3 2020
#     """
    
#     d = 190
#     b = 130
#     L = 4
#     mat2 = mats[2]

#     mySection = ls.SectionRectangle(mat2, b, d)
    
#     column = o86.getBeamColumnGlulamCsa19(L, mySection)    
    
#     Pr = o86.checkPrGlulamColumn(column)
#     Prsol = 175*1000
    
#     # assert inTol(pr, prsol)
#     assert Pr == pytest.approx(Prsol, rel = 0.01)

#     e = (d / 2 + 60)/1000
#     knet = 1
#     Pf = 72.5*1000
#     interSolTop = 0.79
#     # interSolMid = 0.54
#     inter = o86.checkInterEccPfGlulam(column, Pf, e, knet)
#     assert inter == pytest.approx(interSolTop, rel = 0.01)


    
# def test_Interaction_ecc_table():
#     """
#     Tests a random example from Table
#     """
    
#     # d = 228
#     d = 152
#     b = 80
#     L = 4
#     mat2 = mats[1]

#     mySection = ls.SectionRectangle(mat2, b, d)
#     column = o86.getBeamColumnGlulamCsa19(L, mySection)    
    
#     e = (d)/2 / 1000
#     knet = 1
#     # Pf = 35.6*1000
#     Pf = 24.3*1000
#     interSolTop = 1.0
#     inter = o86.checkInterEccPfGlulam(column, Pf, e, knet)
#     assert inter == pytest.approx(interSolTop, rel = 0.02)

if __name__ == "__main__":
    
    test_checkBMDkzbg()
    test_SegmentClassification()
    # test_kLa()
    # test_kLb()
    # test_kLc2()
    # test_bending_table_1()
    
    # test_compression_Design_Example_Cc()
    # test_compression_Design_Example_Pr()
    # test_compression_Table()
    
    # test_Interaction_ecc()
    # test_Interaction_ecc_table()
