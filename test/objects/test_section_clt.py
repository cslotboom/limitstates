"""
Tests if the CLT section is properly counting layers.

"""

from limitstates import MaterialElastic, LayerClt, LayerGroupClt
import numpy as np
import pytest

E = 9500
myMat = MaterialElastic(E)
myMat.E90 = E/30
myMat.grade = 'testing'
myMat.lamGrade = 'testing'
t = 35
myLayer  = LayerClt(35, myMat)
myLayer2 = LayerClt(35, myMat, False)
myLayer3 = LayerClt(15, myMat)


def test_layerRepr():
    assert "35mm" in str(myLayer)

def test_getLayerAttr():
    layers = [myLayer, myLayer2, myLayer]

    layerGroup = LayerGroupClt(layers)
    out1 = layerGroup.getLayerAttr('t')
    assert np.all(out1 == [35,35,35])
    assert np.all(layerGroup.d == 105)

def test_layerGroup_Boundaries():
    layers = [myLayer, myLayer2, myLayer]

    # layer boundaries are set on init
    layerGroup = LayerGroupClt(layers)
    
    output = layerGroup.lBoundaries
    solution = np.array([0, 35, 70, 105])
    
    assert np.all(output == solution)

def test_layerGroup_Position():
    layers = [myLayer, myLayer2, myLayer]
    layerGroup = LayerGroupClt(layers)
    
    output = layerGroup.lMidpointsAbs
    solution = np.array([17.5, 52.5, 87.5])
    
    assert np.all(output == solution)


def test_layerGroup_ybar():
    layers = [myLayer, myLayer2, myLayer]
    layerGroup = LayerGroupClt(layers)

    output = layerGroup.getYbar()
    solution = 105/2
    assert output == pytest.approx(solution)

def test_layerGroup_ybar2():
    layers = [myLayer, myLayer2, myLayer, myLayer2, myLayer3]
    layerGroup = LayerGroupClt(layers)
    
    ybarout = layerGroup.getYbar()
    rmaxOut = layerGroup.getYmax()
    
    yA = 35*((17.5) + (17.5+35)/30 + (17.5+70) + (17.5+105)/30) + 15*(15/2+140)
    A = (35 + 35/30 + 35 + 35/30 + 15)
    ybarSol = yA / A
    
    rmaxSol = max(ybarSol, ((35*4 + 15) - ybarSol))
    assert ybarout == pytest.approx(ybarSol)
    assert rmaxOut == pytest.approx(rmaxSol)

def test_layer_orientation():
    
    layers = [myLayer, myLayer2, myLayer, myLayer2, myLayer3]
    layerGroup = LayerGroupClt(layers)
    orientations = layerGroup.getLayerOrientations()

    assert np.all(orientations == [True, False, True, False, True])

def test_layer_orientation_2():
    
    layers = [myLayer, myLayer2, myLayer, myLayer2, myLayer3]
    layerGroup = LayerGroupClt(layers)
    orientations = layerGroup.getLayerOrientations(False)

    assert np.all(orientations == [False, True, False, True, False])


def test_layer_orientation_3():
    
    layers = [myLayer, myLayer, myLayer2, myLayer, myLayer]
    layerGroup = LayerGroupClt(layers)
    orientations = layerGroup.getLayerOrientations()

    assert np.all(orientations == [True, True, False, True, True])

if __name__ == '__main__':
    # pass
    test_layerRepr()
    test_getLayerAttr()
    test_layerGroup_Boundaries()
    test_layerGroup_Position()
    
    test_layerGroup_ybar()
    test_layerGroup_ybar2()
    test_layer_orientation()
    test_layer_orientation_2()
    test_layer_orientation_3()

    