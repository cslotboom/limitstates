

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86
import planesections as ps

import pytest

Py = -5000

def _setup_Beam_1():
    MPa = 1
    width = 356 # Section width in mm
    depth = 600 # Section depth in mm
    length = 10  # Beam length in m
    supportPositions = [0,6]
    
    myMat       = o86.loadGlulamMaterial('SPF', '20f-E')
    mySection   = ls.SectionRectangle(myMat, width, depth)
    
    
    # We set up a custom member
    pinSupport = ls.SupportTypes2D.PINNED.value
    n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
    n2 = ls.Node([supportPositions[1], 0.], 'm', support = pinSupport)
    n3 = ls.Node([length, 0.], 'm', support = pinSupport)
    
    line1 = ls.getLineFromNodes(n1, n2)
    line2 = ls.getLineFromNodes(n2, n3)
    
    member = ls.Member([n1,n2,n3], [line1, line2])
    designProps  = o86.DesignPropsGlulam19()
    myElement    = o86.BeamColumnGlulamCsa19(member, mySection, designProps)
    return myElement

def _setup_Beam_2():
    MPa = 1
    b = 38
    h = 235
    E = 9500*MPa

    # length = 10  # Beam length in m
    
    L = 3
    supportPositions = [0, L]
    
    myMat       = o86.loadGlulamMaterial('SPF', '20f-E')
    myMat.E = E
    myMat.G = E/16
    mySection   = ls.SectionRectangle(myMat, b, h)
    
    
    # We set up a custom member
    fixedSupport = ls.SupportTypes2D.FIXED.value
    pinSupport = ls.SupportTypes2D.PINNED.value
    n1 = ls.Node([supportPositions[0], 0.], 'm', support = fixedSupport)
    n2 = ls.Node([supportPositions[1], 0.], 'm', support = pinSupport)
    
    line1 = ls.getLineFromNodes(n1, n2)
    
    member = ls.Member([n1,n2], [line1])
    designProps  = o86.DesignPropsGlulam19()
    myElement    = o86.BeamColumnGlulamCsa19(member, mySection, designProps)
    return myElement


def setupAnalysis():

    beam = _setup_Beam_2()
    psBeam = ls.convertBeamColumnToPlanesections(beam)
    psBeam.addVerticalLoad(2, Py)
    # ps.plotBeamDiagram(psBeam)
    
    
    analysis = ps.PyNiteAnalyzer2D(psBeam)
    analysis.runAnalysis()
    
    return psBeam

def test_Mmax():
    """
    Example 'test_analysis_PointLoads2_PN' from planesections.
    """
    # pass
    psBeam = setupAnalysis()
    R = psBeam.reactions
    L = 3
    tol = 0.0001
    MAsolution = abs(4*L*Py / 27)
    MA = R[0][2]
    MA = abs(MA)
    
    assert(abs(MAsolution - MA) < tol)

def test_maxDisp():
    psBeam = setupAnalysis()
    E = psBeam.section.E
    I = psBeam.section.Iz
    L = 3
    tolPercent = 0.002

    xmaxSol = 8*L / 13
    dispMaxSol = 128*L**3*Py / (13689*E*I)

    disp, x = ps.getVertDisp(psBeam)


    dispMax, xmax = ps.getMaxVertDisp(psBeam)
    
    check1 = abs(dispMax / dispMaxSol) - 1 < tolPercent
    check2 = abs(xmax / xmaxSol) - 1 < tolPercent
    assert (check1 and check2)


# def


if __name__ == '__main__':
    test_Mmax()
    test_maxDisp()
#     test_node_lengths()
#     test_line_fromNodes()
#     test_line_fromlengths()
#     test_support_init()
#     test_support_set()