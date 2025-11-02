"""
Initializes some sections and tests the return values
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest
import numpy as np


    
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
    stirrups = c24.getStandardStirrupGroup('10M', spacing = 250)

    concreteSection = ls.SectionConcrete(section, stirrups = stirrups)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')
    return c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)


def test_section():
    """
    Mr from compression tables in blue book
    """
    # barType = '30M'
    # # Nbar = 6
    # yDir = True
    # posDir = True
    # # lUnit = 'mm'
    # Mf = 800
    # deffsol = 1.4*25

    ele = _init_element()
    section = ele.getSection()
    
    c24.placeRebarRowInElement(ele, 4, '25M')
    ls.plotSection(section)

    # Bottom Bars
    deff = section.getdeff()
    assert deff == 900 - 30 - 25/2 - 10
    deff = section.getRebarMaxDepth()
    assert deff == 900 - 30 - 25/2 - 10
    
    # Top bars
    deff = section.getRebarMaxDepth(yDir=True, posDir=False)
    assert deff ==  30 + 25/2 + 10

    # left / right directions
    deff = section.getdeff(yDir=False, posDir=True)
    coords = section.rebar.getxCoords(flatten = True)
    assert deff == np.average(coords[2:4])
    deff = section.getRebarMaxDepth(yDir=False, posDir=True)
    assert deff == 450 - 30 - 25/2 - 10
    
    # # Top Side Bars
    deff = section.getRebarMaxDepth(yDir=False, posDir=False)
    # assert deff ==  30 + 25/2 + 10
    assert deff == 450 - 30 - 25/2 - 10


if __name__ == "__main__":
    test_section()

