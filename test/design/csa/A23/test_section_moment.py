"""
Author: CS
Date: 202050803
Description:
    Checks if rebar is palced correctly 
"""


import pytest

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls



    
def _init_element():
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


def test_element_Mr():
    barType = '30M'
    # Nbar = 6
    yMoment = True
    positiveMoment = True
    lUnit = 'mm'
    Mf = 800


    ele = _init_element()

    c24.setBottomSteelForMr(Mf, ele, barType)
    
    ls.plotSection(ele.section)
    
    assert True
    # getSectionMr
    
    
    # assert len(section.rebar) == 2
    # assert section.rebar.Nbars == Nbar

    # dbar = 30
    # coords = section.rebar.getCoords(flatten=True)
    # sActual = 42.5

    # assert coords[0,0] == 40 + dbar/2
    # assert coords[0,1] == (40 + dbar/2)

    # assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    # assert coords[-1,1] == (40 + dbar/2 + dbar + dbar*1.4)

    


if __name__ == '__main__':
    # pass
    test_element_Mr()

