"""
Hss sections under Cr
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import numpy as np
# import pytest
# from limitstates.objects.read import getSteelSections

# fc = 30
fy = 400
matRebar = c24.MaterialRebarCSA24(fy)
# mat      = c24.MaterialConcreteCSA24(fc)
# steelSections = getSteelSections(mat, 'csa', 'cisc_12', 'hss')

   
# rebar1  = sc.RebarMetric('25M', steel, [0, 650*si.mm])
# bars1   = sc.RebarGroup([rebar1]*3)   

# def _initColumn(beamName, L):
#     section = ls.getByName(steelSections, beamName)
#     column = s16.getBeamColumnSteelCsa24(L, section, 'mm')
#     return column

def test_db():
    """
    Mr from compression tables in blue book
    """
    
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    bar = rebarFactory.getRebar('30M')
    assert bar.d == 30
    assert bar.A == 700
     
def test_Rebar_mutation():
    """
    Confirms that bars have shared propreties in a rebar group.
    """
    
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    xy = (0, 350)
    rebar1 = rebarFactory.getRebar('30M', xy)
    
    
    bars   = ls.RebarGroup([rebar1]*3)
    
    bars[0].mat.E = 400
    assert bars[1].mat.E == 400

 
def test_Rebar_group():
    """
    Checks the behaviour of a rebar group
    """
    
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    xy = (0, 350)
    rebar1 = rebarFactory.getRebar('30M', xy)
    
    bars1   = ls.RebarGroup([rebar1]*3)
    coords  = bars1.getCoords()
    ycoords = bars1.getyCoords()
    
    # Coordinates        
    assert np.all(coords[1] == xy)
    assert ycoords[0] == xy[1]
    assert ycoords[1] == xy[1]
    assert ycoords[2] == xy[1]
    
    # deff
    assert 350 == bars1.getdeff()
    
    # Anet
    assert 2100 == bars1.getNetArea()
    assert 2100e-6 == bars1.getNetArea('m')

    # getAttr
    assert len(bars1.getAttr('dnet')) == 3
  

def _getCollection():
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    xy1 = (0, 350)
    xy2 = (0, 400)
    rebar1 = rebarFactory.getRebar('30M', xy1)
    rebar2 = rebarFactory.getRebar('30M', xy2)
    
    bars1   = ls.RebarGroup([rebar1]*3)
    bars2   = ls.RebarGroup([rebar2]*3)
    
    barCollection = ls.RebarCollection([bars1, bars2])
    
    return barCollection
 
def test_Rebar_Collection():
    """
    Checks the behaviour of a rebar group
    """
    
    barCollection = _getCollection()
    coords  = barCollection.getCoords()
    assert len(coords) == 2
    assert len(coords[0]) == 3
    
    
    
    ycoords = barCollection.getyCoords()
    assert len(ycoords) == 2
    assert ycoords[0][1] == 350
    assert ycoords[1][1] == 400
    
    
    # deff
    assert 375 == barCollection.getdeff()
    
    # Anet
    assert 4200 == barCollection.getNetArea()
    assert 4200e-6 == barCollection.getNetArea('m')

    # getAttr
    assert len(barCollection.getAttr('A')) == 2


def test_Rebar_Collection_positions():
    """
    Checks the behaviour of a rebar group
    """
    
    barCollection = _getCollection()

    coords = barCollection.coords
    coordsFlat = barCollection.coordsFlat
    assert len(coords) == 2
    assert len(coordsFlat) == 6
    assert coords[0][0,1] == 350
    assert coords[1][0,1] == 400
    
    xCoords = barCollection.getxCoords()
    assert len(xCoords) == 2
    assert len(xCoords[0]) == 3
    assert xCoords[0][0] == 0
    
    xCoords = barCollection.getxCoords(flatten = True)
    assert len(xCoords) == 6
    assert xCoords[0] == 0
    assert xCoords[5] == 0
    
    radii = barCollection.getAttr('d')
    assert len(radii) == 2
    radii = barCollection.getAttr('d', True)
    assert len(radii) == 6

    # assert xCoords[0] == 0
    # assert xCoords[5] == 0
        
 
def test_Rebar_layer_placement_1():
    """
    Tests is rebar can be placed within a layer.
    """
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')

    placer = ls.RebarPlacer(rebarFactory)

    d = 400
    b = 350
    bars = placer.getRebarLayer(1, '20M', d, b)
    assert len(bars) == 1
    xy = bars[0].xy
    
    
    assert xy[0] == b / 2
    assert xy[1] == d

    bars = placer.getRebarLayer(2, '20M', d, b)
    assert bars[0].xy[0] == 0
    assert bars[0].xy[1] == d
    assert bars[1].xy[0] == b
    assert bars[1].xy[1] == d

if __name__ == "__main__":
    test_db()
    test_Rebar_mutation()
    test_Rebar_group()
    test_Rebar_Collection()
    test_Rebar_Collection_positions()
    test_Rebar_layer_placement_1()

