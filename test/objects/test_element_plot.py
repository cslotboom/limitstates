"""
Tests if plots are generated properly.
If the plots are run through command line, a non-gui back-end is used
and no figures are shown.
"""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86
import limitstates.design.csa.s16.c24 as s16


# switch the back-end if running through command line
if __name__ != "__main__":
    plt.switch_backend("Agg")

myMat       = ls.MaterialElastic(9.5*1000)
section = ls.SectionRectangle(myMat, 215, 456)
L = 7

def PolyArea(x,y):
    """
    Shamelessly copied from github:
        https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    """
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


def test_plot_glulam_condition_1():
    
    myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')
    FRR = 60
    FRR = o86.getFRRfromFireConditions(FRR, 1)
    o86.setFireSectionGlulamCSA(myElement, FRR)   

    fig, ax     = ls.plotElementSection(myElement)
    
    sectionFire = myElement.designProps.sectionFire
    x_fi = -sectionFire.b / 2
    y_fi = (sectionFire.d) / 2
    # ax.lines
    xy = ax.patches[1].get_xy()
    
    assert xy[0][0] == pytest.approx(x_fi, 0.01)
    assert xy[1][1] == pytest.approx(y_fi, 0.01)


def test_plot_glulam_condition_2():
    
    myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')
    FRR = 60
    FRR = o86.getFRRfromFireConditions(FRR)
    o86.setFireSectionGlulamCSA(myElement, FRR)   

    fig, ax     = ls.plotElementSection(myElement)
    
    sectionFire = myElement.designProps.sectionFire
    x_fi = sectionFire.b / 2
    y_fi = section.d / 2
    xy = ax.patches[1].get_xy()
    
    assert xy[0][0] == pytest.approx(-x_fi, 0.01)
    assert xy[1][1] == pytest.approx(y_fi, 0.01)

def test_plot_glulam_condition_2_raised():
    
    myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')
    FRR = 60
    FRR = o86.getFRRfromFireConditions(FRR)
    o86.setFireSectionGlulamCSA(myElement, FRR)
    
    myElement.eleDisplayProps.setPlotOrigin(2)

    fig, ax     = ls.plotElementSection(myElement)
    
    sectionFire = myElement.designProps.sectionFire
    x_fi = sectionFire.b / 2
    y_fi = section.d 
    xy = ax.patches[1].get_xy()
    
    assert xy[0][0] == pytest.approx(-x_fi, 0.01)
    assert xy[1][1] == pytest.approx(y_fi, 0.01)

def test_plot_I_beam():
    myMat = ls.MaterialElastic(200*1000)

    sections = ls.getSteelSections(myMat, 'us', 'aisc_16_si', 'W')
    section = sections[0]

    member  = ls.initSimplySupportedMember(L, 'm')
    element = s16.BeamColumnSteelCsa24(member, section)
    fig, ax = ls.plotElementSection(element)
    xy = ax.patches[0].get_xy()
    
    assert 13 == len(xy)
    assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]),0.01)




def test_plot_I_beam_raised():
    myMat = ls.MaterialElastic(200*1000)

    sections = ls.getSteelSections(myMat, 'us', 'aisc_16_si', 'W')
    section = sections[0]

    member  = ls.initSimplySupportedMember(L, 'm')
    element = s16.BeamColumnSteelCsa24(member, section)

    element.eleDisplayProps.setPlotOrigin(3)

    fig, ax = ls.plotElementSection(element)

    xy = ax.patches[0].get_xy()

    
    assert xy[0][0] == pytest.approx(0, 0.01)
    assert xy[0][1] == pytest.approx(section.d , 0.01)


def test_plot_I_beam_round():
    myMat = ls.MaterialElastic(200*1000)
    sectionName = 'W310x118'

    sections = ls.getSteelSections(myMat, 'csa', 'cisc_12', 'W')
    section         = ls.getByName(sections, sectionName)

    section = sections[-1]

    member  = ls.initSimplySupportedMember(L, 'm')
    element = s16.BeamColumnSteelCsa24(member, section)
    fig, ax = ls.plotElementSection(element)
    xy = ax.patches[0].get_xy()
    
    # The plotted are will be bigger than the actual area
    assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]), 0.05)

def test_plot_CLT():
    section = o86.loadCltSections()[1]
    member = ls.initSimplySupportedMember(6, 'm')
    
    # Make a typical section
    clt = o86.BeamColumnCltCsa19(member, section)
    fig, ax = ls.plotElementSection(clt)
    
    children = ax.get_children()
    
    lines = children[2]
    lineVerts =     lines.get_paths()
    assert len(lineVerts) == 21 
        
    assert lineVerts[0]._vertices[0][1] == 140
    assert lineVerts[3]._vertices[1][1] == 105
    assert lineVerts[3]._vertices[0][1] == 140
    
    patches = children[3]
    assert len(patches.get_paths()) == 2 
   
if __name__ == "__main__":
    # pass
    test_plot_glulam_condition_1()
    test_plot_glulam_condition_2()
    test_plot_glulam_condition_2_raised()
    test_plot_I_beam()
    test_plot_I_beam_raised()
    test_plot_I_beam_round()
    test_plot_CLT()
else:
    plt.close('all')