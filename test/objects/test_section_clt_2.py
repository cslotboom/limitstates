"""
Checks 8.5.10 from the Canadian CLT handbook.
"""

from limitstates import MaterialElastic, LayerClt, LayerGroupClt, SectionCLT
import pytest

def _init():
    Es = 11700
    Gs = 731
    myMatS = MaterialElastic(Es, Gs)
    myMatS.E90 = Es/30
    myMatS.G90 = Gs/13
    myMatS.grade = 'strong axis'
    
    Ew = 9000
    Gw = 731
    myMatW = MaterialElastic(Es, Gs)
    myMatW.E90 = Ew/30
    myMatW.G90 = Gw/13
    myMatW.grade = 'weak axis'
    
    # t = 35
    myLayer1 = LayerClt(35, myMatS)
    myLayer2 = LayerClt(35, myMatW, False)
    myLayer3 = LayerClt(26, myMatS)
    
    return [myLayer1, myLayer2, myLayer3]


def test_layerGroup_EI():
    
    layers = _init()
    layerGroup = LayerGroupClt(layers)
    
    ybarout = layerGroup.getYbar()
    EI = layerGroup.getEI()

    ybarSol = 45.4 # From example
    EISol = 807.8*1e3 
    # rmaxSol = max(ybarSol, ((35*4 + 15) - ybarSol))
    assert ybarout == pytest.approx(ybarSol, 0.005)
    assert EI == pytest.approx(EISol, 0.005)
    # assert rmaxOut == pytest.approx(rmaxSol)

def test_layerGroup_GA():
      
    layers = _init()
    layerGroup = LayerGroupClt(layers)
    GA = layerGroup.getGA(NlayerTotal = 5)

    GAeff = 9.03*1e6 
    assert GA == pytest.approx(GAeff, 0.01)

def test_Section_GA():
      
    layers = _init()
    layerGroup = LayerGroupClt(layers)
    section = SectionCLT(layerGroup, NlayerTotal = 5)
    GA = section.getGAs()

    GAeff = 9.03*1e6 
    assert GA == pytest.approx(GAeff, 0.01)



if __name__ == '__main__':
    # pass
    test_layerGroup_EI()
    test_layerGroup_GA()
    test_Section_GA()

    