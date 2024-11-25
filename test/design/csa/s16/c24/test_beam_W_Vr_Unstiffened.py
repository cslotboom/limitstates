"""
Tests Steel Beamcolumn elements in shear.
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa24(345)
steelAISC = getSteelSections(mat, 'us', 'aisc_16_si', 'W')
steelCISC = getSteelSections(mat, 'csa', 'cisc_12', 'W')



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

    
    
# beamAISC = _initBeamAISC('W310x74')
# beamCISC = _initBeamCISC('W310x74')
# Mr = s16.checkBeamMrSupported(beamAISC) / 1000
# MrSol = 366


# beamCISC.section.ho

def test_shear_attributes():
    """
    Makes sure the db files has the correct shear attributes
    """
    beamCISC = _initBeamCISC('W310x74')

    section = beamCISC.section
    d  = section.d
    tf = section.tf
    
    assert (d - 2*tf) == pytest.approx(section.ho)


def test_W_Major():
    beamAISC = _initBeamAISC('W310x74')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    VrSol = 597
    assert Vr == pytest.approx(VrSol, rel = 0.01)

    beamCISC = _initBeamCISC('W310x74')
    Vr = s16.checkFsBeam(beamCISC) / 1000
    VrSol = 597
    assert Vr == pytest.approx(VrSol, rel = 0.01)


    beamAISC = _initBeamAISC('W1100x390')
    Vr = s16.checkFsBeam(beamAISC) / 1000
    VrSol = 4510
    assert Vr == pytest.approx(VrSol, rel = 0.01)
        
    beamCISC = _initBeamCISC('W1100x390')
    Vr = s16.checkFsBeam(beamCISC) / 1000
    VrSol = 4510
    assert Vr == pytest.approx(VrSol, rel = 0.01)
        
    # beam = _initBeam('W530x72')
    # Mr = s16.checkBeamMrSupported(beam) / 1000
    # MrSol = 472
    # assert Mr == pytest.approx(MrSol, rel = 0.01)

# def test_W_Minor():
#     beam = _initBeam('W360x134')
#     # section = ls.getByName(steelSections, )
#     Mr = s16.checkBeamMrSupported(beam, useX=False) / 1000
#     MrSol = 254
#     assert Mr == pytest.approx(MrSol, rel = 0.01)
    
#     beam = _initBeam('W360x196')
#     Mr = s16.checkBeamMrSupported(beam, useX=False) / 1000
#     MrSol = 578
#     assert Mr == pytest.approx(MrSol, rel = 0.01)


if __name__ == "__main__":
    test_shear_attributes()
    test_W_Major()
    # test_W_Minor()
