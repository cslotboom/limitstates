"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

Fy = 350
mat = s16.MaterialSteelCsa24(Fy)
steelAISC = getSteelSections(mat, 'us', 'aisc_16_si', 'hss')
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
    beamAISC = _initBeamAISC('HSS254X152.4X9.5')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    VrSol = 855
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    beamAISC = _initBeamAISC('HSS254X152.4X6.4')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    
    beamAISC = _initBeamAISC('HSS203.2X152.4X4.8')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    section = beamAISC.section
    VrSol = 0.66*0.9*Fy*section.A*section.d/(section.b + section.d) / 1000
    assert Vr == pytest.approx(VrSol, rel = 0.01)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamAISC('HSS203.2X152.4X4.8')
    Vr = s16.checkFsBeam(beamAISC, Cf = 1500e3) / 1000
    section = beamAISC.section
    VrSol = 366
    assert Vr == pytest.approx(VrSol, rel = 0.01)
           
    # Force the section to be class 4 for testing purposes
    beamAISC = _initBeamAISC('HSS254X152.4X9.5')
    Vr = s16.checkFsBeam(beamAISC, Cf = 4500e3) / 1000
    section = beamAISC.section
    VrSol = 855
    assert Vr == pytest.approx(VrSol, rel = 0.02)
            
    # beamAISC = _initBeamAISC('HSS203.2X152.4X13')
    # Vr = s16.checkFsBeam(beamAISC, Cf = 1500e3) / 1000
    # section = beamAISC.section
    # VrSol = 366
    # assert Vr == pytest.approx(VrSol, rel = 0.01)
           
               


if __name__ == "__main__":
    test_hss_Major()
