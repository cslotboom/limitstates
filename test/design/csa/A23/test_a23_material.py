"""
Hss sections under Cr
"""

import limitstates.design.csa.a23.c24 as c24
# import limitstates as ls
import pytest
# from limitstates.objects.read import getSteelSections


fc = 30
fy = 400
mat      = c24.MaterialConcreteCSA24(fc)
matRebar = c24.MaterialRebarCSA24(fy)

def test_fc():
    """
    Mr from compression tables in blue book
    """
    assert mat.fc == 30
    assert matRebar.fy == 400
    


if __name__ == "__main__":
    test_fc()

