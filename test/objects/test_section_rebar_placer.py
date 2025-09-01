"""
Author: CS
Date: 202050803
Description:
    Checks if rebar is palced correctly.
"""

import limitstates.design.csa.a23.c24 as c24
import limitstates as ls


# def test_beam_underReinforced():

    
def _init_placer():
    h = 500
    b = 400
    # deff = 450
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    section  = ls.SectionRectangle(mat, b, h)
    configDB = ls.DBConfig('csa', 'rebar', 'rebar')
    
    
    concreteSection = ls.SectionConcrete(section)
    rebarFactory  = ls.RebarFactory(matRebar, configDB, 'mm')   
    
    c = 30
    s = 1.4*30
    dstirrup = 10
    configPlacement = ls.RebarSpacingConfig(s, c, dstirrup)
    
    return ls.RebarPlacerRow(concreteSection, rebarFactory, configPlacement)


def test_bar_position():
    assert 1 == ls.getRebarLocationEnum(True, True)
    assert 2 == ls.getRebarLocationEnum(True, False)


def test_placement_init():
    barType = '30M'
    strategy = _init_placer()
    strategy._initPlacement(barType, 1)
    assert strategy.clearCover == 40    
    assert strategy.NbarsMax == 5
    
    # assert 


def test_placement_bottom():
    barType = '30M'
    Nbar = 6
    locationEnum = 1
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum)
    
    section = placer.section
    
    assert '5 bars at x = 55' in str(section.rebar.groups[0])
    
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
    placer.place(Nbar, barType, locationEnum)
    
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
    placer.place(Nbar, barType, locationEnum)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1] == 40 + dbar/2 + dbar + sActual
    
    assert c24.getSectionMr(section)
    
    locationEnum = 4
    
    dbar = 30

    placer = _init_placer()
    placer.place(Nbar, barType, locationEnum)
    
    section = placer.section
    
    assert len(section.rebar) == 2
    assert section.rebar.Nbars == Nbar

    coords = section.rebar.getCoords(flatten=True)
    sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    assert coords[0,0] == section.concrete.b - (40 + dbar/2)
    assert coords[0,1] == 40 + dbar/2

    assert coords[-1,0] == section.concrete.b - (40 + dbar/2 + dbar + dbar*1.4)
    assert coords[1,1] == 40 + dbar/2 + dbar + sActual
    


if __name__ == '__main__':
    test_bar_position()
    test_placement_init()
    test_placement_bottom()
    test_placement_top()
    test_placement_side()
    # test_placement_side()
