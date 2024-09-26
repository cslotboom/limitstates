"""
Tests if plots are generated properly.
If the plots are run through command line, a non-gui back-end is used
and no figures are shown.
"""

import matplotlib.pyplot as plt
import numpy as np

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86


# switch the back-end if running through command line
if __name__ != "__main__":
    plt.switch_backend("Agg")


myMat       = ls.MaterialElastic(9.5*1000)
section = ls.SectionRectangle(myMat, 215, 456)
L = 7
myElement = o86.getBeamColumnGlulamCsa19(L, section, 'm')
FRR = 60
FRR = o86.getFRRfromFireConditions(FRR)
o86.setFireSectionGlulamCSA(myElement, FRR)   

ls.plotElementSection(myElement)
ls.plotSection(section)

def PolyArea(x,y):
    """
    Shamelessly copied from github:
        https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    """
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def test_plot_rectangle():  
    myMat       = ls.MaterialElastic(9.5*1000)
    section     = ls.SectionRectangle(myMat, 300, 200)
    fig, ax     = ls.plotSection(section)
    
    ax.lines
    xy = ax.patches[0].get_xy()
    assert xy[0][1] == 0
    assert xy[1][1] == 300



def test_plot_rectangle_fire():  
    myMat       = ls.MaterialElastic(9.5*1000)
    section     = ls.SectionRectangle(myMat, 300, 200)
    fig, ax     = ls.plotSection(section)
    
    ax.lines
    xy = ax.patches[0].get_xy()
    assert xy[0][1] == 0
    assert xy[1][1] == 300



# def test_plot_I_beam():
#     myMat = ls.MaterialElastic(200*1000)

#     sections = ls.getSteelSections(myMat, 'us', 'aisc_16_si', 'W')
#     section = sections[0]
#     fig, ax     = ls.plotSection(section)
#     xy = ax.patches[0].get_xy()
#     assert 13 == len(xy)
    
#     assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]),0.01)


# def test_plot_I_beam_round():
#     myMat = ls.MaterialElastic(200*1000)

#     sections = ls.getSteelSections(myMat, 'csa', 'cisc_12', 'W')
#     section = sections[0]
#     fig, ax     = ls.plotSection(section)

#     xy = ax.patches[0].get_xy()
#     assert 53 == len(xy)
#     assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]),0.02)


if __name__ == "__main__":
    pass
    # test_plot_rectangle()
    # test_plot_I_beam()
    # test_plot_I_beam_round()
else:
    plt.close('all')