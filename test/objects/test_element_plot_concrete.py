"""
Author: CS
Data: 20250927
Description: Tests if concrete elements are being plotted correctly.
"""

import limitstates as ls
import matplotlib.pyplot as plt
import numpy as np
import pytest

import limitstates.design.csa.a23.c24 as c24

# switch the back-end if running through command line
if __name__ != "__main__":
    plt.switch_backend("Agg")
  
def _init_element(h = 900, b = 450) -> c24.BeamColumnConcreteCsa24:
    """
    Example 5.2 john Pao
    """

    fc = 25
    c = 40

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    # stirrupBar  = 
    concreteSection = ls.SectionConcrete(section)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(5, 'm')

    ele = c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)    
    return ele
   
def _add_rebar(ele: c24.BeamColumnConcreteCsa24):
    section = ele.getSection()
    designProps = ele.designProps

    barType = '25M'
    Nbar = 4
    placer = c24.RebarPlacerRowCSA24(section, designProps)
    placer.place(Nbar, barType, 1)
    placer.place(2, barType, 2)
   
def _add_stirrups(ele: c24.BeamColumnConcreteCsa24):
    section = ele.getSection()
    # designProps = ele.designProps
    stirrups    = ls.StirrupGroup(c24.getStandardRebar('10M'), spacing = 250)
    section.setStirrups(stirrups)
    
    # placer = c24.RebarPlacerRowCSA24(section, designProps)

    # barType = '15M'
    # Nbar = 4
    # # rebar = c24.
    # placer = ls.StirrupGroup()
    # placer.place(Nbar, barType, 1)
    # placer.place(2, barType, 2)

# def test_section_empty():
    
#     ele = _init_element()
    
#     ls.plotSection(ele.getSection())
#     assert True


def test_section_rebar():
    
    ele = _init_element()
    _add_rebar(ele)
    
    ls.plotElementSection(ele)
    assert True





if __name__ == "__main__":
    test_section_rebar()
    # test_section_rebar()


else:
    plt.close('all')