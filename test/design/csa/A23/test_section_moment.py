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
    # h = 900
    # b = 450
    fc = 25
    c = 30

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    stirrups    = c24.getStandardStirrupGroup('10M')
    concreteSection = ls.SectionConcrete(section, stirrups = stirrups)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')
    
    return c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)


def test_element_Mr():
    barType = '30M'
    Mf = 800
    deffsol = 900 - 30 - 10 - 30/2

    ele = _init_element()

    c24.designBottomSteelForMr(Mf, ele, barType)
    section = ele.getSection()

    assert section.rebar.Nbars == 5
    assert section.getdeff() == deffsol
    # ls.plotSection(ele.section)
    
    assert 800 < c24.getSectionMr(section) / 1000

def test_element_rho():
    
    ele = _init_element()

    rho = c24.getSectionBalancedRho(ele.section)
    
    assert rho == pytest.approx(0.022, 0.02)
    # assert ele.section.getdeff() == deffsol

def test_element_Mr_top():
    barType = '30M'

    posDir = False

    Mf = 800

    deff = 900 - 30 - 10 - 30/2

    ele = _init_element()
    c24.designBottomSteelForMr(Mf, ele, barType, posDir=posDir)
    section = ele.getSection()
    assert section.rebar.Nbars == 5
    assert section.getdeff(posDir=posDir) == deff

    

def test_element_Mr_right():
    barType = '30M'
    Mf = 700
    deffsol = 450 - 30 - 10 - 30/2
    yDir = False
    posDir = True

    ele = _init_element()
    c24.designBottomSteelForMr(Mf, ele, barType, yDir=yDir, posDir=posDir)
    # ls.plotSection(ele.section)
    section = ele.getSection()
    assert section.rebar.Nbars == 11
    assert section.getdeff(yDir) == deffsol

def test_element_Mr_left():
    barType = '30M'
    yDir = False
    posDir = False
    Mf = 700
    # deff = 900 - 30 - 10 - 30/2

    ele = _init_element()
    OR = c24.designBottomSteelForMr(Mf, ele, barType, yDir=yDir, posDir=posDir)
    ls.plotSection(ele.section)
    section = ele.getSection()
    assert section.rebar.Nbars == 11

    
def test_element_Mr_over_reinforced():
    barType = '30M'
    Mf = 800
    deffsol = 900 - 30 - 10 - 30/2

    ele = _init_element(650, 400)

    c24.designBottomSteelForMr(Mf, ele, barType)
    ls.plotSection(ele.section)
    section = ele.getSection()

    assert ele.section.rebar.Nbars == 10
    assert Mf < c24.getSectionMr(ele.section) / 1000

    # assert section.getdeff() == deffsol



if __name__ == '__main__':
    # pass
    test_element_Mr()
    test_element_rho()
    test_element_Mr_top()
    test_element_Mr_right()
    test_element_Mr_left()
    test_element_Mr_over_reinforced()
