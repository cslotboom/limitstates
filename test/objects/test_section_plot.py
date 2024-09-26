"""
Tests if plots are generated properly.
If the plots are run through command line, a non-gui back-end is used
and no figures are shown.
"""

import limitstates as ls
import matplotlib.pyplot as plt
import numpy as np
import pytest

# switch the back-end if running through command line
if __name__ != "__main__":
    plt.switch_backend("Agg")

def PolyArea(x,y):
    """
    Shamelessly copied from github:
        https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    """
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def test_plot_rectangle():  
    myMat       = ls.MaterialElastic(9.5*1000)
    section     = ls.SectionRectangle(myMat, 200, 400)
    fig, ax     = ls.plotSection(section)
    
    ax.lines
    xy = ax.patches[0].get_xy()
    assert xy[0][1] == 0
    assert xy[1][1] == 400


def test_plot_I_beam():
    myMat = ls.MaterialElastic(200*1000)

    sections = ls.getSteelSections(myMat, 'us', 'aisc_16_si', 'W')
    section = sections[0]
    fig, ax     = ls.plotSection(section)
    xy = ax.patches[0].get_xy()
    assert 13 == len(xy)
    
    assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]),0.01)


def test_plot_I_beam_round():
    myMat = ls.MaterialElastic(200*1000)

    sections = ls.getSteelSections(myMat, 'csa', 'cisc_12', 'W')
    section = sections[0]
    fig, ax     = ls.plotSection(section)

    xy = ax.patches[0].get_xy()
    assert 53 == len(xy)
    assert section.A == pytest.approx(PolyArea(xy[:,0], xy[:,1]),0.02)


if __name__ == "__main__":
    test_plot_rectangle()
    test_plot_I_beam()
    test_plot_I_beam_round()
else:
    plt.close('all')