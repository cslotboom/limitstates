"""
Author: CS
Date: 20251005
Description:
    Checks if stirrups are placed correctly.
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
    rebarFactory  = ls.RebarFactory(matRebar, configDB, 'mm')   
    
    stirrups = []
    
    Nstirrup = 2
    for bar in range(Nstirrup):
        rebar = rebarFactory.getRebar('10M')
        stirrups.append(ls.Stirrup(rebar))

    stirrups = ls.StirrupGroup(stirrups)
    
    concreteSection = ls.SectionConcrete(section, stirrups=stirrups)
    
    c = 30
    s = 1.4*30
    dstir = 10
    configPlacement = ls.RebarSpacingConfig(s, c, dstir)
    
    return ls.StirrupPlacerRow(concreteSection, configPlacement)
    
def _init_placer_no_stirrup():
    h = 500
    b = 400
    # deff = 450
    fc = 25
    mat      = c24.MaterialConcreteCSA24(fc)
    section  = ls.SectionRectangle(mat, b, h)

    fy = 400
    matRebar = c24.MaterialRebarCSA24(fy)
    configDB = ls.DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, configDB, 'mm')   
        
    concreteSection = ls.SectionConcrete(section)
    
    c = 30
    s = 1.4*30
    dstir = 10
    configPlacement = ls.RebarSpacingConfig(s, c, dstir)
    
    return ls.StirrupPlacerRow(concreteSection, configPlacement, rebarFactory)

def test_placement_init():
    strategy = _init_placer()
    strategy._initPlacement(True)
    assert strategy.clCover == 35    

def test_set_position():

    placer = _init_placer()
    placer.setPosition()
    
    section = placer.section
        
    assert len(section.stirrups) == 2

    stirrup1 = section.stirrups[0]
    
    assert stirrup1.position
    assert stirrup1.position.h == (500 - 10 - 60)
    assert stirrup1.position.b == (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[0] == 35 + (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[1] == 35

    stirrup2 = section.stirrups[1]
    
    assert stirrup2.position
    assert stirrup2.position.h == 500 - 10 - 60
    assert stirrup2.position.b == (400 - 10 - 60)
    assert stirrup2.position.xy0[0] == (35)
    assert stirrup2.position.xy0[1] == (35)
    

def test_set_position_x():

    placer = _init_placer()
    placer.setPosition(False)
    
    section = placer.section
        
    assert len(section.stirrups) == 2

    stirrup1 = section.stirrups[0]
    
    assert stirrup1.position
    assert stirrup1.position.b == (500 - 10 - 60)
    assert stirrup1.position.h == (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[1] == 35 + (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[0] == 35

    stirrup2 = section.stirrups[1]
    
    assert stirrup2.position
    assert stirrup2.position.b ==  500 - 10 - 60
    assert stirrup2.position.h == (400 - 10 - 60)
    assert stirrup2.position.xy0[1] == (35)
    assert stirrup2.position.xy0[0] == (35)
    
    # coords = section.rebar.getCoords(flatten=True)
    # sActual = (placer.bRow - dbar) / (placer.NbarsMax-1) - dbar

    # assert coords[0,0] == 40 + dbar/2
    # assert coords[0,1] == (40 + dbar/2)

    # assert coords[1,0] == 40 + dbar/2 + dbar + sActual
    # assert coords[-1,1] == (40 + dbar/2 + dbar + dbar*1.4)


def test_place():

    placer = _init_placer_no_stirrup()
    placer.place(2, '10M')
    
    section = placer.section
        
    assert len(section.stirrups) == 2

    stirrup1 = section.stirrups[0]
    
    assert stirrup1.position
    assert stirrup1.position.h == (500 - 10 - 60)
    assert stirrup1.position.b == (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[0] == 35 + (400 - 10 - 60) / 3
    assert stirrup1.position.xy0[1] == 35

    stirrup2 = section.stirrups[1]
    
    assert stirrup2.position
    assert stirrup2.position.h == 500 - 10 - 60
    assert stirrup2.position.b == (400 - 10 - 60)
    assert stirrup2.position.xy0[0] == (35)
    assert stirrup2.position.xy0[1] == (35)
    



if __name__ == '__main__':
    test_placement_init()
    test_set_position()
    test_set_position_x()
    
    test_place()

