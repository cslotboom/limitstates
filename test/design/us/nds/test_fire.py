"""
Tests if the fire sections instantiat proprely.
"""

import limitstates as ls
import limitstates.design.us.nds.c24 as nds
import limitstates.design.csa.o86.c19 as o86

import pytest
import numpy as np
mats = o86.loadGlulamMaterialDB()
sections = o86.loadGlulamSections(mats[0])


def test_ConditionEnum():
    assert nds.FireConditions.beamColumn.value == 1

def test_FirePotection_rect():
    port = nds.GypusmRectangleNds24(['1/2', '(5/8)x2', 'exposed', 'exposed'])
    assert tuple(port.getPortectionTime()) == (30,80,0,0)


def test_getFirePotection():
    port1 = nds.getGypsumFirePortection(2, '1/2')
    port2 = nds.getGypsumFirePortection(1, '1/2')
    port3 = nds.getGypsumFirePortection(3, '5/8')
    assert tuple(port1.getPortectionTime()) == (0, 30,30,30)
    assert tuple(port2.getPortectionTime()) == (30,30,30,30)
    assert port3.getPortectionTime()[0] == 40
    
    
def test_assignFirePotection():
    port1 = nds.getGypsumFirePortection(2, '1/2')
    port2 = nds.getGypsumFirePortection(1, '1/2')
    port3 = nds.getGypsumFirePortection(3, '5/8')
    assert tuple(port1.getPortectionTime()) == (0, 30,30,30)
    assert tuple(port2.getPortectionTime()) == (30,30,30,30)
    assert port3.getPortectionTime()[0] == 40



def test_Rect_netBurnTime():
    port = nds.GypusmRectangleNds24('1/2')
    portTime = port.getPortectionTime()
    myTime = nds.getNetBurnTime(np.array([60,60,60,60]), portTime)

    assert np.all(myTime == [30,30,30,30])

def test_burn_ammount():
    burnAmount = nds.getBurnDimensions(np.array([60,0,0,0]))
    assert  burnAmount[0] == pytest.approx(1.2*1.5, 0.02)

    burnAmount = nds.getBurnDimensions(np.array([90,0,0,0]))
    assert  burnAmount[0] == pytest.approx(1.2*1.5*(90/60)**0.813, 0.02)

def test_Rect_netBurnDims_1():
    width = 8
    depth = 16
    port = nds.GypusmRectangleNds24('1/2')
    portTime = np.array(port.getPortectionTime())
    myTime = nds.getNetBurnTime(np.array([60,60,60,60]), portTime)
    burnAmount = nds.getBurnDimensions(myTime)

    bfi, dfi = nds.getBurntRectangularDims(burnAmount, width, depth)

    assert  bfi == pytest.approx(width - 2*(1.2*1.5*(30/60)**0.813), 0.02)
    assert  dfi == pytest.approx(depth - 2*(1.2*1.5*(30/60)**0.813), 0.02)




def test_Rect_netBurnDims_2():
    width = 8
    depth = 16
    port = nds.getGypsumFirePortection(2, '1/2')
    portTime = np.array(port.getPortectionTime())
    myTime = nds.getNetBurnTime(np.array([0,60,60,60]), portTime)
    burnAmount = nds.getBurnDimensions(myTime)

    bfi, dfi = nds.getBurntRectangularDims(burnAmount, width, depth)

    assert  bfi == pytest.approx(width - 2*(1.2*1.5*(30/60)**0.813), 0.01)
    assert  dfi == pytest.approx(depth - (1.2*1.5*(30/60)**0.813), 0.01)
    
    
def test_Rect_sectionFire():
    width = 200
    depth = 400
    mySection = ls.SectionRectangle(mats[0], width, depth)
    mySection.convertUnits('in')
    
    port = nds.GypusmRectangleNds24('1/2')
    FRR = np.array([0,60,60,60])
    fiSection, _ = nds.getBurntRectangularSection(mySection, FRR, port)

    # assert fiSection.b == (width - 2*(45*0.7 + 7))
    # assert fiSection.d == (depth - 1*(45*0.7 + 7))
    aburn = (1.2*1.5*(30/60)**0.813)
    assert  fiSection.b == pytest.approx(width/25.4 - 2*aburn, 0.01)
    assert  fiSection.d == pytest.approx(depth/25.4 - aburn, 0.01)

# def test_Rect_glulam_setSection():
    
#     width = 300
#     depth = 600
#     mySection = ls.SectionRectangle(mats[0], width, depth)
#     myElement = o86.getBeamColumnGlulamCsa19(4, mySection)
#     FRR = np.array([0,60,60,60])
#     myElement.designProps.firePortection = o86.GypusmRectangleCSA19('15.9mm')

#     o86.setFireSectionGlulamCSA(myElement, FRR)
#     fiSection = myElement.designProps.sectionFire

#     assert fiSection.b == (width - 2*(30*0.7 + 7))
#     assert fiSection.d == (depth - 1*(30*0.7 + 7))


if __name__ == "__main__":
    test_ConditionEnum()
    # test_standard_conditions()
    
    test_FirePotection_rect()
    test_getFirePotection()
    test_assignFirePotection()
    
    test_burn_ammount()
    test_Rect_netBurnTime()
    test_Rect_netBurnDims_1()
    test_Rect_netBurnDims_2()
    test_Rect_sectionFire()
    
    # test_Rect_glulam_setSection()