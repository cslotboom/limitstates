"""
Initializes some sections and tests the return values
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest



    
def _init_element() -> c24.BeamColumnConcreteCsa24:
    """
    Example 5.2 john Pao
    """
    h = 900
    b = 450
    fc = 25
    c = 30

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    stirrupBar  = c24.getStandardRebar('10M')
    concreteSection = ls.SectionConcrete(section, stirrups = ls.StirrupGroup(stirrupBar))
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')
    
    return c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)


def test_section():
    """
    Mr from compression tables in blue book
    """
    barType = '30M'
    # Nbar = 6
    yMoment = True
    posMoment = True
    # lUnit = 'mm'
    Mf = 800
    deffsol = 1.4*25

    ele = _init_element()
    
    c24.placeRebarRowInElement(ele, 4, '25M')
    
    deff = ele.section.getdeff()
    assert deff == 900 - 30 - 25/2 - 10
    
    deff = ele.section.getdeff(yMoment=True, posMoment=False)
    assert deff ==  30 + 25/2 + 10

    deff = ele.section.getdeff(yMoment=False, posMoment=True)
    assert deff == 450 - 30 - 25/2 - 10
    
    deff = ele.section.getdeff(yMoment=False, posMoment=False)
    assert deff ==  30 + 25/2 + 10


if __name__ == "__main__":
    test_section()

