"""
Author: CS
Date: 20251005
Description:
    Checks if stirrups are placed correctly.
"""

import limitstates.design.csa.a23.c24 as c24
import limitstates as ls


cover = 30
dstir = 10 
clCover = cover + dstir / 2 

# def test_beam_underReinforced():

def _initRebarFactory():
    fy = 400
    matRebar = c24.MaterialRebarCSA24(fy)
    configDB = ls.DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, configDB, 'mm')
    return rebarFactory

def _initSection(h = 500, b = 400):
    
    # deff = 450
    fc = 25
    mat      = c24.MaterialConcreteCSA24(fc)
    section  = ls.SectionRectangle(mat, b, h)
    concreteSection = ls.SectionConcrete(section)
    return concreteSection


def _ManuallySetRebar(concreteSection, rebarFactory):
    
    Nstirrup = 2
    stirrups = []

    for bar in range(Nstirrup):
        rebar = rebarFactory.getRebar('10M')
        stirrups.append(ls.Stirrup(rebar))

    stirrups = ls.StirrupGroup(stirrups)
    
    concreteSection.setStirrups(stirrups)
    
def _initRebarPlacer(section):
    
    designProps = c24.DesignPropsConcrete24(cover = cover)
        
    return c24.StirrupPlacerRowCSA24(section, designProps)


def _standardChecks(section):
    assert len(section.stirrups) == 2

    stirrup1 = section.stirrups[0]
    
    assert stirrup1.position
    assert stirrup1.position.h == (500 - clCover*2)
    assert stirrup1.position.b == (400 - clCover*2) / 3
    assert stirrup1.position.xy0[0] == clCover + (400 - clCover*2) / 3
    assert stirrup1.position.xy0[1] == clCover

    stirrup2 = section.stirrups[1]
    
    assert stirrup2.position
    assert stirrup2.position.h == 500 - clCover*2
    assert stirrup2.position.b == (400 - clCover*2)
    assert stirrup2.position.xy0[0] == (clCover)
    assert stirrup2.position.xy0[1] == (clCover)


def _dshift_checks(section, dshift):

    stirrup1 = section.stirrups[0]
    
    assert stirrup1.position
    assert stirrup1.position.h == (500 - clCover*2)
    assert stirrup1.position.b == (400 - clCover*2) / 3 + dshift
    assert stirrup1.position.xy0[0] == 35 + (400 - 10 - cover*2) / 3
    assert stirrup1.position.xy0[1] == 35

    stirrup2 = section.stirrups[1]
    
    assert stirrup2.position
    assert stirrup2.position.h == 500 - 10 - cover*2
    assert stirrup2.position.b == (400 - 10 - cover*2)
    assert stirrup2.position.xy0[0] == (35)
    assert stirrup2.position.xy0[1] == (35)



def test_placement_init():
    barType = '10M'
    section = _initSection()
    factory   = _initRebarFactory()

    _ManuallySetRebar(section, factory)    
    placer = _initRebarPlacer(section)
    
    
    placer._initPlacement(barType, True)
    assert placer.clCover == cover    
    # assert placer.clCover == 30

def test_set_position():
    section = _initSection()
    factory   = _initRebarFactory()
    _ManuallySetRebar(section, factory)

    placer = _initRebarPlacer(section)
    placer.setPosition()
    
    section = placer.section
        
    _standardChecks(section)
    

def test_set_position_x():
    section = _initSection()
    factory   = _initRebarFactory()

    _ManuallySetRebar(section, factory)
    placer = _initRebarPlacer(section)
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



def test_place():

    section = _initSection()
    placer = _initRebarPlacer(section)
    
    placer.place(2, '10M')
    
    section = placer.section
        
    _standardChecks(section)

    

def test_place_function():

    section = _initSection()
    member = ls.initSimplySupportedMember(5, 'm')
    designProps = c24.DesignPropsConcrete24(cover = cover)
    ele = c24.BeamColumnConcreteCsa24(member, section, designProps = designProps)
    c24.placeStirrupRowInElement(ele, 2, '10M')
    
    # placer = _initRebarPlacer(section)
    # placer.place(2, '10M')
    
    section = ele.getSection()
        
    _standardChecks(section)
    

def test_place_dshift():
    """
    Confirms that the dshift kwarg can he used to modify stirrup placement.
    This will shift the locations of to avoid possible clashes
    """
    dshift  = 30
    section = _initSection()
    placer = _initRebarPlacer(section)
    
    placer.place(2, '10M', dshift = dshift)
    
    section = placer.section    
    _dshift_checks(section, dshift)


def test_place_function_dshift():
    """
    Confirms that the dshift kwarg can he used to modify stirrup placement.
    """
    dshift  = 30

    section = _initSection()
    member = ls.initSimplySupportedMember(5, 'm')
    designProps = c24.DesignPropsConcrete24(cover = cover)
    
    ele = c24.BeamColumnConcreteCsa24(member, section, designProps = designProps)
    c24.placeStirrupRowInElement(ele, 2, '10M', dshift = dshift)    
    
    _dshift_checks(section, dshift)



if __name__ == '__main__':
    test_placement_init()
    test_set_position()
    test_set_position_x()
    
    test_place()
    test_place_function()
    
    test_place_dshift()
    test_place_function_dshift()

