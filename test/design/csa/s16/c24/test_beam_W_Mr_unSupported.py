"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa19(345)
steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')

def _initBeam(beamName, L):
    # L = 6
    section = ls.getByName(steelSections, beamName)
    member = ls.initSimplySupportedMember(L, 'mm')
    props = s16.DesignPropsSteel24(Lx = L, kx = 1)
    beam = s16.BeamColumnSteelCsa24(member, section, props)
    return beam

def test_Mu():
    """
    Rab Nawaz master of engineering report.
    "Equivalent Uniform Moment Factor for
    Lateral Torsional Buckling of Steel Beams", University of Alberta
    See Section "3.4 Validation"
    """
    section = ls.getByName(steelSections, 'W460x89')
    Mcr = s16.checkSectionMu(section, 8000, 1)
    McrSol = 256*1000
    
    assert Mcr == pytest.approx(McrSol, rel = 0.01)

def test_W_Major():
    # pass
    beam = _initBeam('W610x82', 4500)
    Mr = s16.checkBeamMrUnsupportedW(beam) / 1000
    MrSol = 364
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    beam = _initBeam('W610x82', 12000)
    Mr = s16.checkBeamMrUnsupportedW(beam) / 1000
    MrSol = 83.4
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    beam = _initBeam('W360x147', 7000)
    Mr = s16.checkBeamMrUnsupportedW(beam) / 1000
    MrSol = 773
    assert Mr == pytest.approx(MrSol, rel = 0.01)   
       
    Mr = s16.checkBeamMrUnsupportedW(beam, Lu = 16000) / 1000
    MrSol = 467
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    beam = _initBeam('W840x193', 4000)
    # section = ls.getByName(steelSections, )
    Mr = s16.checkBeamMrUnsupportedW(beam) / 1000
    MrSol = 2310
    assert Mr == pytest.approx(MrSol, rel = 0.01)          
    Mr = s16.checkBeamMrUnsupportedW(beam, Lu = 14000) / 1000
    MrSol = 534
    assert Mr == pytest.approx(MrSol, rel = 0.01)

    # section = ls.getByName(steelSections, 'W360x134')
    # Mr = s16.getSectionMrSupported(section, useX=False) / 1000
    # MrSol = 254
    # assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    # section = ls.getByName(steelSections, 'W360x196')
    # Mr = s16.getSectionMrSupported(section, useX=False) / 1000
    # MrSol = 578
    # assert Mr == pytest.approx(MrSol, rel = 0.01)


if __name__ == "__main__":
    test_Mu()
    test_W_Major()
    # test_W_Minor()
