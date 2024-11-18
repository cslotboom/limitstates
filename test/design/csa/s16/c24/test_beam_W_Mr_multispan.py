"""
Tests the design of a multi-span steel element
"""

import limitstates.design.csa.s16.c24 as s16
from limitstates.design.csa.s16.c24.beamColumn import _getOmegas
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa24(345)
steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')


import planesections as ps
import numpy as np
L1 = 5
L2 = 8

def _initBeam(beamName):
    
    supportPositions = [0, L1, L2]
    L = supportPositions[-1]
    
    pinSupport      = ls.SupportTypes2D.PINNED.value
    rollerSupport   = ls.SupportTypes2D.ROLLER.value
    n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
    n2 = ls.Node([supportPositions[1], 0.], 'm', support = rollerSupport)
    n3 = ls.Node([L, 0.], 'm', support = pinSupport)
    line1  = ls.getLineFromNodes(n1, n2)
    line2  = ls.getLineFromNodes(n2, n3)
    member = ls.Member([n1, n2, n3], [line1, line2])
    
    
    section = ls.getByName(steelSections, beamName)
    props = s16.DesignPropsSteel24(Lx = L, kx = 1)
    beam = s16.BeamColumnSteelCsa24(member, section, props)
    return beam


def _initBeamManual(beamName, L1eff, L2eff):
    
    
    beam =  _initBeam(beamName)
    designProps = s16.DesignPropsSteel24(Lx=[L1eff, L1eff, L2eff], 
                                         kx=[1.4, 1.4, 1.8], 
                                         lateralSupport=[False, False, False])
    
    beam.designProps = designProps
    return beam




def _initBeam_free(beamName):
    beam = _initBeam(beamName)
    freeSupport = ls.SupportTypes2D.FREE.value
    beam.member.setNodeSupprt(2, freeSupport)
    return beam


def test_cantilever():
    """
    Tests that spans with cantilevers fail.
    """
    myBeam = _initBeam_free('W460x89')    
    with pytest.raises(Exception):
        s16.checkMrBeamMultiSpan(myBeam, lateralSupportType=1)

def test_case1():
    """
    Full lateral support to all flange.
    """
    myBeam = _initBeam('W460x89')
    Mr = s16.checkBeamMrSupported(myBeam)

    Mrmulti, xout, omega = s16.checkMrBeamMultiSpan(myBeam, lateralSupportType=1)

    assert Mrmulti[0] == Mrmulti[1] 
    assert Mr == Mrmulti[1] 


def _getBMD(myBeam):
    beamPs      = ls.convertBeamColumnToPlanesections(myBeam)
    kN = 1000
    q = [0.,-35*kN]
    beamPs.addDistLoad(0, L2, q, label='B') 

    """
    Run the analysis
    """
    analysis = ps.OpenSeesAnalyzer2D(beamPs)
    analysis.runAnalysis(recordOutput=True)

    xyBMD = beamPs.getBMD()
    bmd = ls.DesignDiagram(np.column_stack(xyBMD))
    
    return bmd

def test_case2():
    """
    Full lateral support to all flange.
    """
    beamName = 'W460x89'
    myBeam = _initBeam(beamName)
    section = ls.getByName(steelSections, beamName)
    
    bmd = _getBMD(myBeam)

    Mrmulti, xout, omega = s16.checkMrBeamMultiSpan(myBeam, bmd, 2)    
    
    span1Beam = s16.getBeamColumnSteelCsa24(L1, section, 'm')
    span2Beam = s16.getBeamColumnSteelCsa24(L2-L1, section, 'm')
    Mru1 = s16.checkBeamMrUnsupported(span1Beam, omega[0])
    Mru2 = s16.checkBeamMrUnsupported(span2Beam, omega[1])

    assert Mrmulti[0] == Mru1 
    assert Mrmulti[1] == Mru2 


def test_case3():
    """
    Full lateral support to all flange.
    """
    beamName = 'W460x89'
    myBeam = _initBeam(beamName)
    section = ls.getByName(steelSections, beamName)
    
    bmd = _getBMD(myBeam)


    Mrmulti, xout, omega = s16.checkMrBeamMultiSpan(myBeam, bmd, 3)    
    
    span1Beam = s16.getBeamColumnSteelCsa24(1.4*L1, section, 'm')
    span2Beam = s16.getBeamColumnSteelCsa24(1.4*(L2-L1), section, 'm')
    Mru1 = s16.checkBeamMrUnsupported(span1Beam, omega[0])
    Mru2 = s16.checkBeamMrUnsupported(span2Beam, omega[1])

    assert omega[0] == 1
    assert omega[1] == 1
    assert Mrmulti[0] == Mru1 
    assert Mrmulti[1] == Mru2 

def test_case4():
    """
    Full lateral support to all flange.
    """
    beamName = 'W460x89'
    L1eff = 2.5
    L2eff = 3
    myBeam = _initBeamManual(beamName, L1eff, L2eff)
    section = ls.getByName(steelSections, beamName)
    
    bmd = _getBMD(myBeam)


    Mrmulti, xout, omega = s16.checkMrBeamMultiSpan(myBeam, bmd, 4)    
    
    span1Beam = s16.getBeamColumnSteelCsa24(1.4*L1eff, section, 'm')
    span2Beam = s16.getBeamColumnSteelCsa24(1.8*L2eff, section, 'm')
    Mru1 = s16.checkBeamMrUnsupported(span1Beam, omega[0])
    Mru2 = s16.checkBeamMrUnsupported(span1Beam, omega[1])
    Mru3 = s16.checkBeamMrUnsupported(span2Beam, omega[2])

    # assert omega[0] == 1
    # assert omega[2] == 1
    assert Mrmulti[0] == Mru1 
    assert Mrmulti[1] == Mru2 
    assert Mrmulti[2] == Mru3 

def _getOmega(x,y, L):
    xy = np.column_stack((x, y))
    bmd = ls.DesignDiagram(xy)
        
    Nspan = 1
    omegas = _getOmegas(bmd, Nspan, [L])
    return omegas[0]

def test_bmd_omegas():
    
    """
    Double checks omega is coming out properly for a few common cases
    1. parabolic
    2. linear single curvature
    3. constant
    4. linear double curvature.
    """
    
    L = 8
    t = np.linspace(0,1,101)
    x = t* 8
    y1 = 16-(x-4)**2
    y2 = x
    y3 = np.linspace(1,1,101)*5
    y4 = -4 + x

    omega1 =  _getOmega(x, y1, L)
    omega2 =  _getOmega(x, y2, L)
    omega3 =  _getOmega(x, y3, L)
    omega4 =  _getOmega(x, y4, L)

    
    assert omega1 == pytest.approx(1.13, 0.05  )
    assert omega2 == pytest.approx(1.745743122, 0.05  )
    assert omega3 == pytest.approx(1., 0.05  )
    assert omega4 == pytest.approx(2.309401077, 0.05  )
     

if __name__ == "__main__":
    test_cantilever()
    test_case1()
    test_case2()
    test_case3()
    test_case4()
    test_bmd_omegas()