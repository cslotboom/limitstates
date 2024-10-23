"""
Tests if the verticies are corretly output for the model files.
"""

import numpy as np
import pytest

from limitstates.objects.output.model import GeomModelRectangle, GeomModelClt

import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

def PolyArea(x,y):
    """
    Shamelessly copied from github:
        https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    """
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


def test_geom_rectangle():
    b = 200
    d = 400
    # myMat       = ls.MaterialElastic(9.5*1000)
    # section     = ls.SectionRectangle(myMat, 200, 400)
    
    geom = GeomModelRectangle(b, d)
    x, y = geom.getVerticies()
    
    Aout = PolyArea(x, y)
    assert b*d == pytest.approx(Aout, 0.01)

    assert x[1] == -100
    assert y[1] == 200


def test_clt():
    """
    A test to see if the geometry of the CLT function is initializing 
    correctly.
    """
    b = 200
    d = 400
    
    section = o86.loadCltSections()[0]
    layers  = section.sLayers
    
    
    geom = GeomModelClt(layers)
        
    verts = geom.getFillVerticies()
    assert len(verts[0]) == 11

# member  = ls.initSimplySupportedMember(6, 'm')
# beamColumn = o86.BeamColumnCltCsa19(member, section)


if __name__ == "__main__":
    test_geom_rectangle()
    test_clt()
    # test_plot_glulam_condition_2()
    # test_plot_glulam_condition_2_raised()
    # test_plot_I_beam()
    # test_plot_I_beam_raised()
    # test_plot_I_beam_round()
