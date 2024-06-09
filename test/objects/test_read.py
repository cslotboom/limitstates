"""
Tests if the read functions proprely return database values.

We will use the a specific function from csa o86-19 to check
"""

# from limitstates.design.read import _loadMaterialDBDict, _loadMaterialDatabase
import limitstates.design.csa.o86.c19 as o86
# import pytest


    
# mydict = _loadMaterialDBDict('csa','o86', 'c19', "glulam_csa.csv")
def test_matLoad():
    mats=o86.loadGlulamMaterials()

    myMat = mats[0]
    assert myMat.fb == 30.6
    assert myMat.fv == 2.0
    assert myMat.sUnit == 'MPa'

if __name__ == '__main__':
    test_matLoad()