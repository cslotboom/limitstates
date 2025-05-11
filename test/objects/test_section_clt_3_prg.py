"""
Checks if PRG sections properly return section propreties, such as EI, GA,
Seff, etc.

"""

from limitstates import MaterialElastic, LayerClt, LayerGroupClt, SectionCLT, filterByName
import limitstates.design.csa.o86.c19 as c19

import pytest

def _init():
    Es = 11700
    Gs = 731
    myMatS = MaterialElastic(Es, Gs)
    myMatS.E90 = Es/30
    myMatS.G90 = Gs/13
    myMatS.grade = 'strong axis'
    
    Ew = 9000
    Gw = 731
    myMatW = MaterialElastic(Es, Gs)
    myMatW.E90 = Ew/30
    myMatW.G90 = Gw/13
    myMatW.grade = 'weak axis'
    
    # t = 35
    myLayer1 = LayerClt(35, myMatS)
    myLayer2 = LayerClt(35, myMatW, False)
    myLayer3 = LayerClt(35, myMatS)
    
    return [myLayer1, myLayer2, myLayer3]


def _initDB(w=1000, lUnit = 'mm'):
    sections    = c19.loadCltSections(w=w, lUnit=lUnit)
    E1Sections  = filterByName(sections, 'E1')
    
    return E1Sections
   

def test_panel_EI_E1_105():
    
    layers = _init()
    layerGroup = LayerGroupClt(layers)
    
    # Width is assumed to be 1000mm - layers do not account for width.
    EI = layerGroup.getEI(sUnit='MPa', lUnit='mm') * 1e-9 * 1000 
    GA = layerGroup.getGA(sUnit='MPa', lUnit='mm') * 1e-6 * 1000 # Width is assumed to be 1000mm

    EISol = 1088
    GASol = 7.3
    assert EI == pytest.approx(EISol, 0.005)
    assert GA == pytest.approx(GASol, 0.005)

def test_panel_EI_E1_105_DB():
      
    panel = _initDB()[0]
    EI = panel.getEIs(sUnit='MPa', lUnit='mm') * 1e-9  
    GA = panel.getGAs(sUnit='MPa', lUnit='mm') * 1e-6
    EISol = 1088
    GASol = 7.3
    assert EI == pytest.approx(EISol, 0.005)
    assert GA == pytest.approx(GASol, 0.005)


def test_panel_EI_E1_245_DB():
      
    panel = _initDB()[2]
    EI = panel.getEIs(sUnit='MPa', lUnit='mm') * 1e-9  
    GA = panel.getGAs(sUnit='MPa', lUnit='mm') * 1e-6
    EISol = 10306
    GASol = 22
    assert EI == pytest.approx(EISol, 0.005)
    assert GA == pytest.approx(GASol, 0.005)

# def test_panel_EI_E1_245_DB_imp():
      
#     panel = _initDB(12, 'in')[2]
#     EI = panel.getEIs(sUnit='psi', lUnit='in') * 1e-6  
#     GA = panel.getGAs(sUnit='psi', lUnit='in') * 1e-6
#     EISol = 899
#     GASol = 1.5
#     assert EI == pytest.approx(EISol, 0.005)
#     assert GA == pytest.approx(GASol, 0.005)



if __name__ == '__main__':
    # pass
    test_panel_EI_E1_105()
    test_panel_EI_E1_105_DB()
    test_panel_EI_E1_245_DB()

    