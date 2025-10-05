"""
Tests if rebar specific to CSA A23 works correctly.
"""

import limitstates.design.csa.a23.c24 as c24
import limitstates as ls
import pytest


def test_stirrup_init():
    """
    Mr from compression tables in blue book
    """
    fy = 400
    matRebar = c24.MaterialRebarCSA24(fy)
    factory = c24.loadRebarFactory(matRebar)
    
    sType = ls.StirrupTypeEnum.Closed
    
    rebar10M = factory.getRebar('10M')
    stirrup  = ls.Stirrup(rebar10M, sType, 2)
    
    assert stirrup.rebar.d == 10
    assert stirrup.rebar.A == 100
    
    assert stirrup.rebar.lUnit == 'mm'
    
    assert stirrup.getAv() == 200
    
    

if __name__ == "__main__":
    test_stirrup_init()
    # test_getStandardRebar()

