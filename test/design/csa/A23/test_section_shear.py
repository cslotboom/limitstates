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

def test_max_shear_resistance():
    ele = _init_element(500, 300)
    assert c24.getElementVmax(ele) / 1000 == pytest.approx(475, 0.02)

def test_max_stirrup_spacing():
    ele = _init_element(500, 300)
    assert c24.getElementSmax(ele) == pytest.approx(273, 0.02)



if __name__ == '__main__':
    # pass
    test_element_Vrc()
    test_element_Vrs()
    test_max_shear_resistance()
    test_max_stirrup_spacing()
    # test_element_rho()
    # test_element_Mr_top()
    # test_element_Mr_right()
    # test_element_Mr_left()
    # test_element_Mr_over_reinforced()
