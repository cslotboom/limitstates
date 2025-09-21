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
    # stirrups    = ls.StirrupGroup(c24.getStandardRebar('10M'), spacing = 250)
    concreteSection = ls.SectionConcrete(section)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')

    # barType = '25M'
    # Nbar = 4
    # placer = c24.RebarPlacerRowCSA24(concreteSection, designProps)
    # placer.place(Nbar, barType, 1)
    # placer.place(2, barType, 2)


    ele = c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)    
    return ele
   

def test_design_pass():
    """
    6.2 john pao
    """
    ele = _init_element(700, 600)

    Vf = 124000
    designer = c24.StirrupDesigner(Vf, ele)

    Vr, resultCode = designer.design()

    assert resultCode == 2
    assert pytest.approx(Vr,0.05) == 166000

def test_design_failure_force_to_big():
    """
    6.2 john pao
    """
    ele = _init_element(700, 600)

    Vf = 12400000
    designer = c24.StirrupDesigner(Vf, ele)
    Vr, resultCode = designer.design()

    assert resultCode == 3

def test_design_success():
    """
    6.2 john pao
    """
    ele = _init_element(700, 600)

    Vf = 302000
    designer = c24.StirrupDesigner(Vf, ele)
    Vr, resultCode = designer.design()

    assert resultCode == 1
    assert Vr > Vf
    
    section = ele.getSection()
    assert section.stirrups.spacing == 350



if __name__ == '__main__':
    # pass
    test_design_pass()
    test_design_failure_force_to_big()
    test_design_success()

