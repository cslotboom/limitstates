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


def _init_placer():
    h = 500
    b = 400
    fc = 25
    c = 30

    mat      = c24.MaterialConcreteCSA24(fc)
    section  = ls.SectionRectangle(mat, b, h)
    stirrups    = c24.getStandardStirrupGroup('10M')
    concreteSection = ls.SectionConcrete(section, stirrups = stirrups)
    designProps = c24.DesignPropsConcrete24(cover= c)
    
    return c24.RebarPlacerRowCSA24(concreteSection, designProps)

    
def _init_element(Nstirrups = 1):
    h = 500
    b = 400
    fc = 25
    c = 30

    mat         = c24.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    stirrups    = c24.getStandardStirrupGroup('10M', Nstirrups = Nstirrups)
    concreteSection = ls.SectionConcrete(section, stirrups = stirrups)
    designProps = c24.DesignPropsConcrete24(cover = c)
    
    member = ls.initSimplySupportedMember(5, 'm')
    
    return c24.BeamColumnConcreteCsa24(member, concreteSection, designProps)


def test_placement_init():
    barType = '30M'
    placer  = _init_placer()
    
    config  = c24.getSectionSpacingRules(placer._getBar(barType), placer.section, placer.c)
    assert config.clearSpacing == 1.4*30
    
    placer.setSpacingConfig(config)
    placer._initPlacement(barType, 1)
    assert placer.clearCover == 40    
    assert placer.NbarsMax == 5
    

def test_placement_bottom():
    barType = '30M'
    Nbar = 6
    locationEnum = 1
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum, includeRadius = False)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == 40 + dbar/2
    assert coords[0,1] == (40 + dbar/2)

    assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    assert coords[-1,1] == (40 + dbar/2 + dbar + dbar*1.4)

def test_placement_top():
    barType = '30M'
    Nbar = 7
    locationEnum = 2
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum, includeRadius = False)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == 40 + dbar/2
    assert coords[0,1] == section.concrete.d - (40 + dbar/2)

    assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    assert coords[-1,1] == section.concrete.d - (40 + dbar/2 + dbar + dbar*1.4)


def test_placement_side():
    barType = '30M'
    Nbar = 7
    locationEnum = 3
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum, includeRadius = False)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1]  == 40 + dbar/2 + dbar + sActual
    
    locationEnum = 4
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum, includeRadius = False)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == section.concrete.b - (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == section.concrete.b - (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1]  == 40 + dbar/2 + dbar + sActual
    

def test_element_placement_bottom():
    barType = '30M'
    Nbar = 6
    locationEnum = 1
    
    element = _init_element()
    c24.placeRebarInElement(element, Nbar, barType, 
                            placementKwargs = {'location':locationEnum},
                            includeRadius = False)
    
    section = element.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    dbar = 30
    coords = section.rebar.getCoords(flatten=True)
    sActual = 42.5

    assert coords[0,0] == 40 + dbar/2
    assert coords[0,1] == (40 + dbar/2)

    assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    assert coords[-1,1] == (40 + dbar/2 + dbar + dbar*1.4)

def test_element_placement_top():
    barType = '30M'
    Nbar = 7
    locationEnum = 2
    
    element = _init_element()
    c24.placeRebarInElement(element, Nbar, barType, 
                            placementKwargs = {'location':locationEnum},
                            includeRadius = False)
    
    section = element.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    dbar = 30
    coords = section.rebar.getCoords(flatten=True)
    sActual = 42.5

    assert coords[0,0] == 40 + dbar/2
    assert coords[0,1] == section.concrete.d - (40 + dbar/2)

    assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    assert coords[-1,1] == section.concrete.d - (40 + dbar/2 + dbar + dbar*1.4)




def test_element_placement_side():
    barType = '30M'
    Nbar = 7
    locationEnum = 3
    
    dbar = 30

    element = _init_element()
    c24.placeRebarInElement(element, Nbar, barType, 
                            placementKwargs = {'location':locationEnum},
                            includeRadius = False)
        
    section = element.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    dbar = 30
    coords = section.rebar.getCoords(flatten=True)
    sActual = 48

    assert coords[0,0] == (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1]  == 40 + dbar/2 + dbar + sActual
    
    locationEnum = 4
    
    dbar = 30

    element = _init_element()
    c24.placeRebarInElement(element, Nbar, barType, 
                            placementKwargs = {'location':locationEnum},
                            includeRadius = False)
        
    section = element.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = 48

    assert coords[0,0] == section.concrete.b - (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == section.concrete.b - (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1]  == 40 + dbar/2 + dbar + sActual
    

# def test_element_placement_stirrups():
    
#     element = _init_element(Nstirrups = 2)
    
#     c24.setStirrupPosition(element)
    
def test_placement_stirrup_override():
    """
    confirms if stirrup placement can manually be overriden using the dstirrup
    kwarg
    """
    assert False    
    
    
    
if __name__ == '__main__':
    # pass
    test_placement_init()
    test_placement_bottom()
    test_placement_top()
    test_placement_side()
    test_element_placement_bottom()
    test_element_placement_top()
    test_element_placement_side()
