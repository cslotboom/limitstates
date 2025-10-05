"""
Tests if rebar specific to CSA A23 works correctly.
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest


def test_rebar_factory():
    """
    Mr from compression tables in blue book
    """
    fy = 400
    matRebar = c24.MaterialRebarCSA24(fy)
    
    factory = c24.loadRebarFactory(matRebar)
    
    rebar30M = factory.getRebar('30M')
    
    assert rebar30M.d == 30
    assert rebar30M.A == 700
    
    
    rebar10M = factory.getRebar('10M')

    assert rebar10M.d == 10
    assert rebar10M.A == 100
    

def test_getStandardRebar():
    """
    Mr from compression tables in blue book
    """

    
    rebar30M = c24.getStandardRebar('30M')
    assert rebar30M.d == 30
    assert rebar30M.A == 700
    
    rebar10M = c24.getStandardRebar('10M')
    assert rebar10M.d == 10
    assert rebar10M.A == 100
    

if __name__ == "__main__":
    test_rebar_factory()
    test_getStandardRebar()

