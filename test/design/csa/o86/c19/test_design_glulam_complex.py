"""
Tests the design of glulam elements according to csa o86 where loading 
conditions are complex, i.e. cantilevers, laterally unsupported beams, etc.


"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86
from limitstates.design.csa.o86.c19.glulam import _getElemenKlSegments
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

Lsegs, classSegs = _getElemenKlSegments(myElement)


def test_checkBMDkzbg():
    
    _, kzbg = o86.checkBMDkzbg(interCoords, width, depth)
    
    L1 = interCoords[1]
    L2 = interCoords[2] - interCoords[1]
    
    k1 = o86.checkKzbg(width, depth, L1)
    k2 = o86.checkKzbg(width, depth, L2)

    assert k1 == pytest.approx(kzbg[0])
    assert k2 == pytest.approx(kzbg[1])

def test_SegmentClassification():
    Lsegs, classSegs = _getElemenKlSegments(myElement)
    
 
    assert 5 == pytest.approx(Lsegs[0])
    assert 3 == pytest.approx(Lsegs[1])   
     
    assert 1.92 == pytest.approx(classSegs[0])
    assert 1.92 == pytest.approx(classSegs[1])

def test_kLRegions():
    
    x, kzbg, kL = o86.getMultispanRegions([4.2, 3.8], [0.8, 0.9], [5,3], [0.9, 1])
    
    xSol    = (4.2, 5, 8)
    kzbgSol = (0.8, 0.9, 0.9)
    kLbgSol = (0.9, 0.9, 1)
    
    assert xSol == tuple(x)
    assert sum(kzbgSol) == pytest.approx(sum(kzbg))
    assert kzbgSol[1] == pytest.approx(kzbg[1])
    assert sum(kLbgSol) == pytest.approx(sum(kL))


kzbg = [1.050, 1.056, 1.056]
kL   = [0.921, 0.921, 0.971]

if __name__ == "__main__":
    
    test_checkBMDkzbg()
    test_SegmentClassification()
    test_kLRegions()
