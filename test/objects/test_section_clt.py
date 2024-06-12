"""
Tests if the CLT section is properly counting layers.

"""

from limitstates import MaterialElastic, LayerClt, LayerGroupClt
import numpy as np
import pytest

E = 9500
myMat = MaterialElastic(E)
myMat.name = 'testing'
t = 35
myLayer = LayerClt(35, myMat)
myLayer2 = LayerClt(35, myMat, 90)
myLayer3 = LayerClt(35, myMat)

layers = [myLayer, myLayer2, myLayer]
# layerGroup = LayerGroupClt([myLayer, myLayer2, myLayer3])
# layerGroup.setLayerPosition()


def test_layerRepr():
    assert "35mm" in str(myLayer)


def test_getLayerAttr():
    layerGroup = LayerGroupClt(layers)
    out1 = layerGroup.getLayerAttr('t')
    assert np.all(out1 == [35,35,35])
    assert np.all(layerGroup.d == 105)

def test_layerGroup_Boundaries():
    layerGroup = LayerGroupClt(layers)

    layerGroup._setLayerBoundaries()
    
    output = layerGroup.lBoundaries
    solution = np.array([0, 35, 70, 105])
    
    assert np.all(output == solution)

def test_layerGroup_Position():
    layers = [myLayer, myLayer2, myLayer]
    layerGroup = LayerGroupClt(layers)
    layerGroup._setLayerBoundaries()
    layerGroup._setLayerPositions()
    
    output = layerGroup.lMidpointsAbs
    solution = np.array([17.5, 52.5, 87.5])
    
    assert np.all(output == solution)


def test_layerGroup_ybar():
    layers = [myLayer, myLayer2, myLayer]
    layerGroup = LayerGroupClt(layers)
    layerGroup._setLayerBoundaries()
    layerGroup._setLayerPositions()
    layerGroup._setYbar()
    
    output = layerGroup.ybar
    solution = 105/2
    
    assert output == solution


_getLayerE(isStrongAxis, layer)



if __name__ == '__main__':
    # pass
    test_layerRepr()
    test_getLayerAttr()
    test_layerGroup_Boundaries()
    test_layerGroup_Position()
    test_layerGroup_ybar()
