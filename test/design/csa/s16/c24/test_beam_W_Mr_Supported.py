"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa19(345)
steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')



def _initBeam(beamName):
    L = 6
    section = ls.getByName(steelSections, beamName)
    member = ls.initSimplySupportedMember(L, 'm')
    beam = s16.BeamColumnSteelCSA19(member, section)
    return beam

    

def test_W_Major():
    beam = _initBeam('W310x74')
    Mr = s16.checkBeamMrSupported(beam) / 1000
    MrSol = 366
    assert Mr == pytest.approx(MrSol, rel = 0.01)

    beam = _initBeam('W1100x390')
    Mr = s16.checkBeamMrSupported(beam) / 1000
    MrSol = 6460
    assert Mr == pytest.approx(MrSol, rel = 0.01)
        
    beam = _initBeam('W530x72')
    Mr = s16.checkBeamMrSupported(beam) / 1000
    MrSol = 472
    assert Mr == pytest.approx(MrSol, rel = 0.01)

def test_W_Minor():
    beam = _initBeam('W360x134')
    # section = ls.getByName(steelSections, )
    Mr = s16.checkBeamMrSupported(beam, useX=False) / 1000
    MrSol = 254
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    beam = _initBeam('W360x196')
    Mr = s16.checkBeamMrSupported(beam, useX=False) / 1000
    MrSol = 578
    assert Mr == pytest.approx(MrSol, rel = 0.01)


if __name__ == "__main__":
    
    test_W_Major()
    test_W_Minor()
