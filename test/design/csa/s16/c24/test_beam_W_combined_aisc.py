"""
Tests the design of glulam elements according to csa o86
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
import pytest
from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa19(345)
steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'w')


    
kN = 1000
m = 1


def _initBeam(beamName, L):
    # L = 6
    section = ls.getByName(steelSections, beamName)
    # member = ls.initSimplySupportedMember(L, 'mm')
    # props = s16.DesignPropsSteel24(Lx = L, kx = 1, Ly = L, ky = 1)
    # beam = s16.BeamColumnSteelCSA19(member, section, props)
    beam = s16.getBeamColumnSteelCSA19(L, section)
    return beam


def test_combined_blueBook():
    
    beam = _initBeam('W310X117', 3.7)
    
    Cf = 2000*kN
    Mfx = 300*kN

    omega1x = 0.4
    isBracedFrame = True
    n = 1.34
    u = s16.checkBeamColumnCombined(beam, Cf, Mfx, 0, n, omega1x, isBracedFrame)
    util_solA = 0.85
    util_solB = 0.625
    util_solC = 0.94
    assert u[0] == pytest.approx(util_solA, rel = 0.01)
    assert u[1] == pytest.approx(util_solB, rel = 0.01)
    assert u[2] == pytest.approx(util_solC, rel = 0.01)
    
def test_combined_LSDSS_EX8_4():
    
    """
    Example 8.4 - limit states design in structural steel. GLK
    """
    
    beam = _initBeam('W250X73', 2.9)

    Cf = 900*kN
    Mfx = 180*kN

    Mmax = 180*kN*m
    Mmin = -75*kN*m 
    
    omega1x = s16.getOmega1(1, Mmax, Mmin)
    assert 0.767 == pytest.approx(omega1x, rel = 0.01)
   
    n = 1.34
    u = s16.checkCombinedCaseA(beam, Cf, Mfx, 0, n, omega1x)
    util_solA = 0.80
    assert u == pytest.approx(util_solA, rel = 0.02)

    
def test_combined_LSDSS_EX8_5():
    
    """
    Example 8.5 - limit states design in structural steel. GLK
    """
    beam = _initBeam('W250X73', 3.6)

    Cf = 900*kN
    Mmax = 180*kN*m
    
    omega1x = s16.getOmega1(2)
    assert 1 == pytest.approx(omega1x, rel = 0.01)
   
    n = 1.34
    u = s16.checkCombinedCaseB(beam, Cf, Mmax, 0, n, omega1x, True)
    util_solA = 0.85
    assert u == pytest.approx(util_solA, rel = 0.02)


    
def test_combined_LSDSS_EX8_6():
    
    """
    Example 8.6 - limit states design in structural steel. GLK
    """
    beam = _initBeam('W250X73', 3.6)

    Cf = 900*kN
    Mmax = 180*kN*m
    Mmin = 0*kN*m
    
    omega1x = s16.getOmega1(1, Mmax, Mmin)
   
    n = 1.34
    u = s16.checkCombinedCaseB(beam, Cf, Mmax, 0, n, omega1x, True)
    util_solA = 0.64
    assert u == pytest.approx(util_solA, rel = 0.02)
    
def test_combined_LSDSS_EX8_7():
    
    """
    Example 8.7 - limit states design in structural steel. GLK
    Example for LTB
    """
    beam = _initBeam('W250X73', 3.6)

    Cf = 900*kN
    Mmax = 180*kN*m
    
    omega1x = s16.getOmega1(2, Mmax)
   
    n = 1.34
    u = s16.checkCombinedCaseC(beam, Cf, Mmax, 0, n, omega1x, True)
    util_solC = 0.93
    assert u == pytest.approx(util_solC, rel = 0.02)

    
def test_combined_LSDSS_EX8_8():
    
    """
    Example 8.7 - limit states design in structural steel. GLK
    Example for LTB
    """
    beam = _initBeam('W250X73', 3.6)

    Cf = 900*kN
    Mmax = 180*kN*m
    
    Mmax = 180*kN*m
    Mmin = 0*kN*m
    
    omega1x = s16.getOmega1(1, Mmax, Mmin)   
    n = 1.34
    u = s16.checkCombinedCaseC(beam, Cf, Mmax, 0, n, omega1x, True)
    util_solC = 0.90
    assert u == pytest.approx(util_solC, rel = 0.02)

    
# def test_combined_LSDSS_EX8_9():
    
#     """
#     Example 8.7 - limit states design in structural steel. GLK
#     Example for LTB
#     """
#     beam = _initBeam('W250X73', 12)

#     Cf = 900*kN
#     Mmax = 180*kN*m
    
#     Mmax = 180*kN*m
#     Mmin = 0*kN*m
    
#     omega1x = s16.getOmega1(1, Mmax, Mmin)   
#     n = 1.34
#     u = s16.checkCombinedCaseC(beam, Cf, Mmax, 0, n, omega1x, True)
#     util_solC = 0.90
#     assert u == pytest.approx(util_solC, rel = 0.02)








if __name__ == "__main__":
    # test_Mu()
    test_combined_blueBook()
    
    test_combined_LSDSS_EX8_4()
    test_combined_LSDSS_EX8_5()
    test_combined_LSDSS_EX8_6()
    test_combined_LSDSS_EX8_7()
    test_combined_LSDSS_EX8_8()
