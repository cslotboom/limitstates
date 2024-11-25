"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa24(350)
# steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'hss')
steelSections = getSteelSections(mat, 'csa', 'cisc_12', 'hss')

def _initBeam(beamName, L):
    # L = 6
    section = ls.getByName(steelSections, beamName)
    member = ls.initSimplySupportedMember(L, 'mm')
    props = s16.DesignPropsSteel24(Lx = L, kx = 1)
    beam = s16.BeamColumnSteelCsa24(member, section, props)
    return beam


def test_hss_unsupported():
    """
    Mr from compression tables in blue book
    """
    # pass
    beam = _initBeam('HSS127x127x7.9', 4500)
    Mr = s16.checkBeamMrSupported(beam) / 1000
    # Mr = s16.checkBeamMrUnsupportedW(beam) / 1000
    MrSol = 50.1
    assert Mr == pytest.approx(MrSol, rel = 0.02)
    
    beam = _initBeam('HSS254x152x9.5', 12000)
    Mr = s16.checkBeamMrSupported(beam) / 1000
    MrSol = 186
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    beam = _initBeam('HSS254x152x9.5', 12000)
    Mr = s16.checkBeamMrSupported(beam, useX=False) / 1000
    MrSol = 130
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    
    
    #Unsupported Check
    beam = _initBeam('HSS254x152x9.5', 12000)
    Mr = s16.checkBeamMrUnsupported(beam) / 1000
    MrSol = 186
    assert Mr == pytest.approx(MrSol, rel = 0.01)
    


if __name__ == "__main__":
    test_hss_unsupported()
