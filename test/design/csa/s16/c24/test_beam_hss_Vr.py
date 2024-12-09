"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

Fy = 350
FyAISC = 345
mat = s16.MaterialSteelCsa24(Fy)
matAISC = s16.MaterialSteelCsa24(345)
steelAISC = getSteelSections(matAISC, 'us', 'aisc_16_si', 'hss')
steelCISC = getSteelSections(mat, 'csa', 'cisc_12', 'hss')



def _initBeamAISC(beamName):
    L = 6
    section = ls.getByName(steelAISC, beamName)
    member = ls.initSimplySupportedMember(L, 'm')
    beam = s16.BeamColumnSteelCsa24(member, section)
    return beam

def _initBeamCISC(beamName):
    L = 6
    section = ls.getByName(steelCISC, beamName)
    member = ls.initSimplySupportedMember(L, 'm')
    beam = s16.BeamColumnSteelCsa24(member, section)
    return beam


def test_hss_Major():
    """
    Checks bending for the major per CSA G420-C sections
    """
    beamAISC = _initBeamCISC('HSS254X152X9.5')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    beamAISC = _initBeamCISC('HSS254X152X6.4')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    
    beamAISC = _initBeamCISC('HSS203X152X4.8')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamCISC('HSS203X152X4.8')
    Vr = s16.checkFsBeam(beamAISC, Cf = 1500e3) / 1000
    section = beamAISC.section
    VrSol = 366
    assert Vr == pytest.approx(VrSol, rel = 0.01)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamCISC('HSS254X152X9.5')
    Vr = s16.checkFsBeam(beamAISC, Cf = 4500e3) / 1000
    section = beamAISC.section
    VrSol = 855
    assert Vr == pytest.approx(VrSol, rel = 0.02)
            
    # beamAISC = _initBeamAISC('HSS203.2X152.4X13')
    # Vr = s16.checkFsBeam(beamAISC, Cf = 1500e3) / 1000
    # section = beamAISC.section
    # VrSol = 366
    # assert Vr == pytest.approx(VrSol, rel = 0.01)
           
 
def test_hss_Major_AISC():
    """
    Checks per beam loading tables for ASTM5000 sections
    """
    beamAISC = _initBeamAISC('HSS254X152.4X9.5')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*FyAISC*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    beamAISC = _initBeamAISC('HSS254X152.4X6.4')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*FyAISC*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    
    beamAISC = _initBeamAISC('HSS203.2X152.4X4.8')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*FyAISC*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamAISC('HSS203.2X152.4X4.8')
    Vr = s16.checkFsBeam(beamAISC, Cf = 1500e3) / 1000
    section = beamAISC.section
    VrSol = 328
    assert Vr == pytest.approx(VrSol, rel = 0.03)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamAISC('HSS254X152.4X9.5')
    Vr = s16.checkFsBeam(beamAISC, Cf = 4500e5) / 1000
    section = beamAISC.section
    VrSol = 773
    assert Vr == pytest.approx(VrSol, rel = 0.03)
            
                         


if __name__ == "__main__":
    test_hss_Major()
    test_hss_Major_AISC()
