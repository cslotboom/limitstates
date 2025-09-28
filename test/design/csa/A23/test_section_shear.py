"""
Author: CS
Date: 202050803
Description:
    Checks if rebar is palced correctly 
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest
    
def _init_element(h = 900, b = 450) -> c24.BeamColumnConcreteCsa24:
    """
    Example 5.2 john Pao
    """

    fc = 25
    c = 40

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    # stirrupBar  = 
    stirrups    = ls.StirrupGroup(c24.getStandardRebar('10M'), spacing = 250)
    concreteSection = ls.SectionConcrete(section, stirrups=stirrups)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')

    barType = '25M'
    Nbar = 4
    placer = c24.RebarPlacerRowCSA24(concreteSection, designProps)
    placer.place(Nbar, barType, 1)
    placer.place(2, barType, 2)


    ele = c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)    
    return ele
   

def test_element_Vrc():

    ele = _init_element(500, 300)    
    assert c24.getElementVrc(ele) / 1000 == pytest.approx(68.4, 0.02)

def test_element_Vrs():
    ele = _init_element(500, 300)
    assert c24.getElementVrs(ele) / 1000 == pytest.approx(151.5, 0.02)

def test_element_Vr():
    ele = _init_element(500, 300)
    assert c24.getElementVr(ele) / 1000 == pytest.approx(151.5 + 68.4, 0.02)

def test_max_shear_resistance():
    """
    6.2 john pao
    """
    ele = _init_element(500, 300)
    assert c24.getElementVmax(ele) / 1000 == pytest.approx(475, 0.02)

def test_max_stirrup_spacing():
    """
    6.2 john pao
    """
    ele = _init_element(500, 300)
    assert c24.getElementSmaxGeom(ele) == pytest.approx(273, 0.02)


def test_min_stirrup_spacing():
    """
    6.2 john pao
    """
    ele = _init_element(500, 300)

    smin = c24.getElementSmaxStirrup(ele, barType='10M')
    sSol = 400 * 200 / (0.06 * 25**0.5 * 300)
    assert smin == pytest.approx(sSol, 0.02)


def test_min_stirrup_spacing_for_Vrs():
    """
    6.4 john pao
    """
    ele = _init_element(700, 600)

    Vrs = 136000
    smin = c24.getElementSminForVrs(ele, Vrs)    
    sSol = 408
    assert smin == pytest.approx(sSol, 0.02)



if __name__ == '__main__':
    # pass
    test_element_Vrc()
    test_element_Vrs()
    test_element_Vr()
    test_max_shear_resistance()
    test_max_stirrup_spacing()
    test_min_stirrup_spacing()
    test_min_stirrup_spacing_for_Vrs()

