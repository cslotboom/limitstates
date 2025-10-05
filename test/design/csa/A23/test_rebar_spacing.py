"""
Author: CS
Date: 20251005
Description: Tests if rebar spacing rules are being respected.
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest

  
def _init_Section(h = 900, b = 450) -> ls.SectionConcrete:
    """
    Example 5.2 john Pao
    """

    fc = 25

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    return ls.SectionConcrete(section)

def _init_rebar(rType = '15M'):
    fy = 400
    matRebar = c24.MaterialRebarCSA24(fy)
    factory  = c24.loadRebarFactory(matRebar)
    rebar15M = factory.getRebar(rType)
    return rebar15M

  
def _init_element(h = 900, b = 450) -> c24.BeamColumnConcreteCsa24:
    """
    Example 5.2 john Pao
    """

    c = 40
    concreteSection = _init_Section(h, b)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')

    return c24.BeamColumnConcreteCsa24(member, concreteSection, designProps) 
   



def test_rebar_spacing_config():
    """
    Mr from compression tables in blue book
    """
    rebar15M = _init_rebar()
    section = _init_Section()
    rebarConfig = c24.getSectionSpacingRules(rebar15M, section, 40, True)
    
    assert rebarConfig.clearSpacing == 30
    assert rebarConfig.cover ==  40

def test_rebar_spacing_config_25M():
    """
    Mr from compression tables in blue book
    """
    rebar15M = _init_rebar('25M')
    section = _init_Section()
    rebarConfig = c24.getSectionSpacingRules(rebar15M, section, 40, True)
    
    assert rebarConfig.clearSpacing == 25*1.4
    assert rebarConfig.cover ==  40

def test_rebar_spacing_config_stirrups():
    """
    Mr from compression tables in blue book
    """

    rebar15M = _init_rebar()
    section  = _init_Section()
    stirrups = c24.getStandardStirrupGroup('10M')
    section.setStirrups(stirrups)
    
    rebarConfig = c24.getSectionSpacingRules(rebar15M, section, 40, True)
    
    assert rebarConfig.clearSpacing == 30
    assert rebarConfig.cover ==  40
    assert rebarConfig.stirrupCurveRadius
   
def test_rebar_spacing_config_ele():
    """
    Mr from compression tables in blue book
    """
    rebar15M = _init_rebar()
    ele = _init_element()
    
    rebarConfig = c24.getElementSpacingRules(rebar15M, ele)

    assert rebarConfig.clearSpacing == 30
    assert rebarConfig.cover ==  40

if __name__ == "__main__":
    test_rebar_spacing_config()
    test_rebar_spacing_config_25M()
    test_rebar_spacing_config_stirrups()
    test_rebar_spacing_config_ele()

