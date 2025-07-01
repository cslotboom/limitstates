"""
Hss sections under Cr
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest


# def test_beam_underReinforced():


def _get_beam_1():
    """
    John Pao E.x 3.1


    Returns
    -------
    concreteSection : TYPE
        DESCRIPTION.

    """

    h = 500
    b = 400
    deff = 450
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    section = ls.SectionRectangle(mat, b, h)
    config = DBConfig('csa', 'rebar', 'rebar')
    
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacer(rebarFactory)
    
    layer2 = placer.getRebarLayer(2, '25M', deff, 300)
    Lbars = ls.RebarCollection([layer2])
    concreteSection = ls.SectionConcrete(section, Lbars)
    
    return concreteSection


def test_beam_Tr_1():
    
    """
    John Pao E.x 3.1
    
    Checks that the steel force is being calcualted correctly for a given NA 
    location.

    """
    a = 65
    c = a / 0.9
    concreteSection = _get_beam_1()
    Tr = c24.getSectionSr(concreteSection, c)
    assert sum(Tr) == pytest.approx(340000)

def test_beam_Cr_1():
    
    """
    John Pao E.x 3.1
    
    Checks that the Cc is being calcualted correctly for a given NA location.

    """

    concreteSection = _get_beam_1()
    a = 65.4
    c = a / concreteSection.concrete.mat.beta
    Cr = c24.getSectionCr(concreteSection, c)
    assert Cr == pytest.approx(340000, 0.02)



def test_beam_underReinforced_NA():
    
    """
    John Pao E.x 3.1
    
    Checks that the Tr is being calcualted correctly for a given NA location.

    """
    
    
    concreteSection = _get_beam_1()
    solver = ls.SectionNASolver(concreteSection, c24.getSectionCr, c24.getSectionSr)
    
    NA = solver.calcNA()
    # a = 65.4
    # c = a / 0.9
    
    
    Cr = c24.getSectionCr(concreteSection, NA)
    Tr = sum(c24.getSectionSr(concreteSection, NA))
    assert Cr == pytest.approx(Tr, 0.001)


def test_beam_overReinforced():
    fc = 30
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)

    b = 500
    d = 300
    section = ls.SectionRectangle(mat, b, d)
    config = DBConfig('csa', 'rebar', 'rebar')

    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacer(rebarFactory)

    layer1 = placer.getRebarLayer(5, '25M', 375, 300, 50)
    layer2 = placer.getRebarLayer(5, '25M', 425, 300, 50)

    Lbars = ls.RebarCollection([layer1, layer2])

    concreteSection = ls.SectionConcrete(section, Lbars)

# steelSections = getSteelSections(mat, 'csa', 'cisc_12', 'hss')

# def _initColumn(beamName, L):
#     section = ls.getByName(steelSections, beamName)
#     column = s16.getBeamColumnSteelCsa24(L, section, 'mm')
#     return column


if __name__ == "__main__":
    test_beam_Tr_1()
    test_beam_Cr_1()
    test_beam_underReinforced_NA()
