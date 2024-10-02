"""
Tests if the fire sections instantiat proprely.
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

import numpy as np
mats = o86.loadGlulamMaterialDB()
sections = o86.loadGlulamSections(mats[0])


def test_ConditionEnum():
    assert o86.FireConditions.beamColumn.value == 1

def test_standard_conditions():
    FRR = o86.getFireDemands(120,3)

    assert len(FRR) == 1
    assert FRR[0] == 120

def test_FirePotection_rect():
    port = o86.GypusmRectangleCSA19(['12.7mm', '15.9mmx2', 'exposed', 'exposed'])
    assert tuple(port.getPortectionTime()) == (15,60,0,0)


def test_getFirePotection():
    port1 = o86.getGypsumFirePortection(2, '12.7mm')
    port2 = o86.getGypsumFirePortection(1, '12.7mm')
    port3 = o86.getGypsumFirePortection(3, '15.9mm')
    assert tuple(port1.getPortectionTime()) == (0, 15,15,15)
    assert tuple(port2.getPortectionTime()) == (15,15,15,15)
    assert port3.getPortectionTime()[0] == 30
    
    
def test_assignFirePotection():
    port1 = o86.getGypsumFirePortection(2, '12.7mm')
    port2 = o86.getGypsumFirePortection(1, '12.7mm')
    port3 = o86.getGypsumFirePortection(3, '15.9mm')
    assert tuple(port1.getPortectionTime()) == (0, 15,15,15)
    assert tuple(port2.getPortectionTime()) == (15,15,15,15)
    assert port3.getPortectionTime()[0] == 30



def test_Rect_netBurnTime():
    port = o86.GypusmRectangleCSA19('12.7mm')
    portTime = port.getPortectionTime()
    myTime = o86.getNetBurnTime(np.array([60,60,60,60]), portTime)

    assert np.all(myTime == [45,45,45,45])


def test_Rect_netBurnDims_1():
    width = 200
    depth = 400
    port = o86.GypusmRectangleCSA19('12.7mm')
    portTime = np.array(port.getPortectionTime())
    myTime = o86.getNetBurnTime(np.array([60,60,60,60]), portTime)
    bfi, dfi = o86.getBurntRectangularDims(myTime, width, depth)

    assert bfi == (width - 2*(45*0.7 + 7))
    assert dfi == (depth - 2*(45*0.7 + 7))

def test_Rect_netBurnDims_2():
    width = 200
    depth = 400
    port = o86.getGypsumFirePortection(2, '12.7mm')
    portTime = np.array(port.getPortectionTime())
    myTime = o86.getNetBurnTime(np.array([0,60,60,60]), portTime)
    bfi, dfi = o86.getBurntRectangularDims(myTime, width, depth)

    assert bfi == (width - 2*(45*0.7 + 7))
    assert dfi == (depth - (45*0.7 + 7))

def test_Rect_sectionFire():
    width = 200
    depth = 400
    mySection = ls.SectionRectangle(mats[0], width, depth)
    
    port = o86.GypusmRectangleCSA19('12.7mm')
    FRR = np.array([0,60,60,60])
    fiSection = o86.getBurntRectangularSection(mySection, FRR, port)

    assert fiSection.b == (width - 2*(45*0.7 + 7))
    assert fiSection.d == (depth - 1*(45*0.7 + 7))


def test_Rect_glulam_setSection():
    
    width = 300
    depth = 600
    mySection = ls.SectionRectangle(mats[0], width, depth)
    myElement = o86.getBeamColumnGlulamCsa19(4, mySection)
    FRR = np.array([0,60,60,60])
    myElement.designProps.firePortection = o86.GypusmRectangleCSA19('15.9mm')

    o86.setFireSectionGlulamCSA(myElement, FRR)
    fiSection = myElement.designProps.sectionFire

    assert fiSection.b == (width - 2*(30*0.7 + 7))
    assert fiSection.d == (depth - 1*(30*0.7 + 7))


if __name__ == "__main__":
    test_ConditionEnum()
    test_standard_conditions()
    
    test_FirePotection_rect()
    test_getFirePotection()
    test_assignFirePotection()
    
    test_Rect_netBurnTime()
    test_Rect_netBurnDims_1()
    test_Rect_netBurnDims_2()
    test_Rect_sectionFire()
    
    test_Rect_glulam_setSection()