"""
Checks beams under the balanced service condition - this is more a proprety
of the cross section, and rebar hasn't been set yet.
"""

import limitstates.design.csa.a23.c24 as a23
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest


# def test_beam_underReinforced():


def _get_beam_1():
    """
    John Pao E.x 3.3


    Returns
    -------
    concreteSection : TYPE
        DESCRIPTION.

    """

    h = 500
    b = 400
    deff = 400
    fc = 25
    fy = 400
    mat      = a23.MaterialConcreteCSA24(fc)
    
    section = ls.SectionRectangle(mat, b, h)
    concreteSection = ls.SectionConcrete(section)

    return concreteSection


def test_beam_NA():
    
    """
    John Pao E.x 3.1
    
    Checks that the steel force is being calcualted correctly for a given NA 
    location.

    """
    # a = 65
    # c = a / 0.9
    concreteSection = _get_beam_1()
    
    
    c = a23.getSectionBalancedNA(concreteSection, 400)
    
    assert 255 == pytest.approx(c, 0.01)
    


def test_beam_As():
    
    """
    John Pao E.x 3.1
    
    Checks that the steel force is being calcualted correctly for a given NA 
    location.

    """
    # a = 65
    # c = a / 0.9
    concreteSection = _get_beam_1()
    
    
    Anet = a23.getSectionBalancedAnet(concreteSection, 400)
    
    assert 3518 == pytest.approx(Anet, 0.02)
# Tr = c24.getSectionSr(concreteSection, c)
# assert sum(Tr) == pytest.approx(340000)


if __name__ == "__main__":
    test_beam_NA()
    test_beam_As()

    
