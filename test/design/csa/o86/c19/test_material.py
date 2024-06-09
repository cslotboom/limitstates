"""
Tests if sections load properly for CSA o86
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

mm = 0.001
m = 1
MPa = 1
width = 356*mm
depth = 600*mm
Length = 6*m


# =============================================================================
# Manually create elements
# =============================================================================
def test_repr():
    """
    this test might be a bad idea - we are coupling the name to the output
    very tightly. I'd feel better if ther was a way we could couple this 
    more loosly'
    
    """
    
    myMatManual = csa.MaterialGlulamCSA19({'E':9500*MPa, 'fb':25*MPa})
    myMatDB   = csa.loadGlulamMaterialDB()[0]
    
    assert myMatManual.name == "CSAo86-19 glulam"
    assert str(myMatManual) == "<limitstates CSAo86-19 glulam material.>"
    assert myMatDB.name == "CSAo86-19 glulam DF 24f-E"
    assert str(myMatDB) == "<limitstates CSAo86-19 glulam DF 24f-E material.>"


def test_loadMat():

    myMat = csa.loadGlulamMaterial('SPF', '20f-E')

    assert myMat.species == 'SPF'
    assert myMat.grade == '20f-E'
    assert str(myMat) == "<limitstates CSAo86-19 glulam SPF 20f-E material.>"

if __name__ == "__main__":
    test_repr()
    test_loadMat()