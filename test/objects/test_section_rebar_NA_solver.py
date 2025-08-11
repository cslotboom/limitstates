"""
Hss sections under Cr
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls
import pytest


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
    placer = ls.RebarPlacerManual(rebarFactory)
    
    layer2 = placer.getRebarLayer(2, '25M', deff, 300)
    Lbars  = ls.RebarCollection([layer2])
    concreteSection = ls.SectionConcrete(section, Lbars)
   
    return concreteSection


def _get_beam_2():
    """
    John Pao E.x 3.1, but upside-down

    """


    h = 500
    b = 400
    deff = 50
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    section = ls.SectionRectangle(mat, b, h)
    config = DBConfig('csa', 'rebar', 'rebar')
    
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacerManual(rebarFactory)
    
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

def test_beam_underReinforced_NA_reversed():   
    """
    John Pao E.x 3.1
   
    Checks that the Tr is being calcualted correctly for a given NA location.
    """
    
    
    concreteSection = _get_beam_2()
    solver = ls.SectionNASolver(concreteSection, c24.getSectionCr, c24.getSectionSr,
                                positiveMoment=False)
   
    NA = solver.calcNA()
    a = 65.4
    c = a / 0.9
    assert NA == pytest.approx(c, 0.03)
   
    Cr = c24.getSectionCr(concreteSection, NA, positiveMoment=False)
    Tr = sum(c24.getSectionSr(concreteSection, NA, positiveMoment=False))
    assert Cr == pytest.approx(Tr, 0.001)



def test_beam_overReinforced():
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)

    mat.alpha = 0.8
    mat.beta  = 0.9
    b = 400
    d = 500
    c = 280 # value is taken directly form 
   
    section = ls.SectionRectangle(mat, b, d)
    config = DBConfig('csa', 'rebar', 'rebar')

    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacerManual(rebarFactory)

    layer1 = placer.getRebarLayer(5, '25M', 375, 300, 50)
    layer2 = placer.getRebarLayer(5, '25M', 425, 300, 50)

    Lbars = ls.RebarCollection([layer1, layer2])
    concreteSection = ls.SectionConcrete(section, Lbars)
    Tr = c24.getSectionSr(concreteSection, c)
    TrNet = sum(Tr)
    assert TrNet == pytest.approx(1275000)
   
    # c = 278
    Cr = c24.getSectionCr(concreteSection, c)
    assert Cr == pytest.approx(1275000, 0.03)
   

    # there are rounding errors in textbook, confirm NA is close enough
    solver = ls.SectionNASolver(concreteSection, c24.getSectionCr, c24.getSectionSr)
    NA = solver.calcNA()
    assert NA == pytest.approx(277, 0.02)
    

    Tr = c24.getSectionSr(concreteSection, NA)
    Cr = c24.getSectionCr(concreteSection, NA)
    TrNet = sum(Tr)
    assert TrNet == pytest.approx(Cr, 0.001)
    

def test_beam_compression_steel():
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    mat.alpha = 0.8
    mat.beta  = 0.9
    b = 400
    h = 500
    c = 91 # value is taken directly from the example 
   
    section = ls.SectionRectangle(mat, b, h)
    config = DBConfig('csa', 'rebar', 'rebar')
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacerManual(rebarFactory)

    layer1 = placer.getRebarLayer(2, '25M', 50, 300, 50)
    layer2 = placer.getRebarLayer(4, '25M', 450, 300, 50)

    Lbars = ls.RebarCollection([layer1, layer2])

    concreteSection = ls.SectionConcrete(section, Lbars)

    Tr = c24.getSectionSr(concreteSection, c)
    TrNet = sum(Tr)
    assert TrNet == pytest.approx(426400, 0.05)
    
    # c = 278
    Cr = c24.getSectionCr(concreteSection, c)
    assert Cr == pytest.approx(426400, 0.05)
   

    # there are rounding errors in textbook, confirm NA is close enough
    solver = ls.SectionNASolver(concreteSection, c24.getSectionCr, c24.getSectionSr)
    NA = solver.calcNA()
    assert NA == pytest.approx(91, 0.02)
   
    Mr = c24.getSectionMr(concreteSection, NA)
    assert Mr == pytest.approx(279000, 0.02)
   


if __name__ == "__main__":
    test_beam_Tr_1()
    test_beam_Cr_1()
    test_beam_underReinforced_NA()
    test_beam_underReinforced_NA_reversed()
    test_beam_overReinforced()
    test_beam_compression_steel()
