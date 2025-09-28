"""
Tests if plots are generated properly.
If the plots are run through command line, a non-gui back-end is used
and no figures are shown.
"""

import limitstates as ls
import matplotlib.pyplot as plt
import numpy as np
import pytest

import limitstates.design.csa.a23.c24 as c24

# switch the back-end if running through command line
if __name__ != "__main__":
    plt.switch_backend("Agg")

# sections = o86.loadCltSections()
# member   = ls.initSimplySupportedMember(6, 'm')
# beamColumn = o86.BeamColumnCltCsa19(member, sections[11])
    
  
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
    # barType = '15M'
    # Nbar = 4
    # # rebar = c24.
    # placer = ls.StirrupGroup()
    # placer.place(Nbar, barType, 1)
    # placer.place(2, barType, 2)

def test_section_empty():
    
    ele = _init_element()
    
    ls.plotSection(ele.getSection())
    assert True


def test_section_rebar():
    
    ele = _init_element()
    _add_rebar(ele)
    
    ls.plotSection(ele.getSection())
    assert True



def test_section_rebar_stirrups():
    
    ele = _init_element()
    _add_stirrups(ele)
    _add_rebar(ele)
    
    ls.plotSection(ele.getSection())
    assert True



if __name__ == "__main__":
    
    test_section_empty()
    test_section_rebar()
    # test_plot_rectangle_bottom()
    # test_plot_I_beam()
    # test_plot_I_beam_round()
    # test_plot_I_beam_round_small()
    # test_plot_I_beam_round_canvasConfig()
    # test_plot_I_beam_round_objConfig()
    # test_plot_CLT()
    # test_plot_hss_cisc()

else:
    plt.close('all')