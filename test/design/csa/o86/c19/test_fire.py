"""
Tests if the fire sections instantiat proprely.
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

import numpy as np
mats = o86.loadGlulamMaterialDB()
sections = o86.loadGlulamSections(mats[0])


def test_FirePotection_rect():
    port = o86.GypusmRectangleCSA19(['12.7mm', '15.9mmx2', 'exposed', 'exposed'])
    assert tuple(port.getPortectionTime()) == (15,60,0,0)


def test_getFirePotection():
    port1 = o86.getGypsumFirePortection('beamWithPanel', '12.7mm')
    port2 = o86.getGypsumFirePortection('beamColumn', '12.7mm')
    port3 = o86.getGypsumFirePortection('panel', '15.9mm')
    assert tuple(port1.getPortectionTime()) == (15,15,15,0)
    assert tuple(port2.getPortectionTime()) == (15,15,15,15)
    assert port3.getPortectionTime()[0] == 30
    
    
def test_assignFirePotection():
    port1 = o86.getGypsumFirePortection('beamWithPanel', '12.7mm')
    port2 = o86.getGypsumFirePortection('beamColumn', '12.7mm')
    port3 = o86.getGypsumFirePortection('panel', '15.9mm')
    assert tuple(port1.getPortectionTime()) == (15,15,15,0)
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
    port = o86.getGypsumFirePortection('beamWithPanel', '12.7mm')
    portTime = np.array(port.getPortectionTime())
    myTime = o86.getNetBurnTime(np.array([60,60,60,60]), portTime)
    bfi, dfi = o86.getBurntRectangularDims(myTime, width, depth)

    assert bfi == (width - 2*(45*0.7 + 7))
    assert dfi == (depth - (45*0.7 + 7))


# def test_burnSection():
#     mySection = ls.SectionRectangle(mats[0], 200, 400)
    
#     sectionFire  = getBurntSection(section, FRR, firePortection)
#     sectionFire  = getBurntDimensions(inputDims, burnDims)
#     sectionFire  = getBurntSection(section, FRR, firePortection)
#     assert True


if __name__ == "__main__":
    test_FirePotection_rect()
    test_getFirePotection()
    test_assignFirePotection()
    
    test_Rect_netBurnTime()
    test_Rect_netBurnDims_1()
    test_Rect_netBurnDims_2()