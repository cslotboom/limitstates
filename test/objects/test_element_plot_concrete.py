"""
Author: CS
Data: 20250927
Description: Tests if concrete elements are being plotted correctly.
"""

import limitstates as ls
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
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
    ele.eleDisplayProps.setPlotOrigin(3)
    return ele
   
def _add_rebar(ele: c24.BeamColumnConcreteCsa24):
    section = ele.getSection()
    designProps = ele.designProps

    barType = '25M'
    Nbar = 6
    includeRadius = False
    placer = c24.RebarPlacerRowCSA24(section, designProps)
    placer.place(Nbar, barType, 1, includeRadius=includeRadius)
    placer.place(2, barType, 2, includeRadius=includeRadius)
   
def _add_stirrups(ele: c24.BeamColumnConcreteCsa24):
    # c24.placeStirrupRowInElement(ele, 2, '10M', dshift = 25)
    c24.placeStirrupRowInElement(ele, 1, '15M', dshift = 25)


def test_section_rebar():
    
    ele = _init_element()
    _add_rebar(ele)
    
    ls.plotElementSection(ele)
    assert True


def test_section_stirrups():
    
    ele = _init_element()
    _add_stirrups(ele)
    _add_rebar(ele)

    # position = ele.getSection().stirrups[0].position
    fig, ax = ls.plotElementSection(ele)
    # ax.set(xlim=(0, 500), ylim=(0, 100))
    # ax.grid(visible=True, color='r', linestyle='--')
    # ax.grid(visible=True, which='minor', linestyle='--')
   
    
    # ax.xaxis.set(minor_locator=MultipleLocator(20))
    # ax.yaxis.set(minor_locator=MultipleLocator(20))
    
    
    ax.minorticks_on()
    assert True





if __name__ == "__main__":
    # test_section_rebar()
    test_section_stirrups()



else:
    plt.close('all')