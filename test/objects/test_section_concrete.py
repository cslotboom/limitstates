"""
Author: CS
Date: 202050803
Description:
    Checks if rebar is palced correctly.
"""

import limitstates.design.csa.a23.c24 as c24
import limitstates as ls
import matplotlib.pyplot as plt
from pytest import approx

def _init_beam_vertical_placer():
    h = 500
    b = 400
    fc = 25
    fy = 400
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    section  = ls.SectionRectangle(mat, b, h)
    configDB = ls.DBConfig('csa', 'rebar', 'rebar')
    
    concreteSection = ls.SectionConcrete(section)
    rebarFactory  = ls.RebarFactory(matRebar, configDB, 'mm')   
    
    c = 30
    s = 1.4*30
    dstirrup = 10
    configPlacement = ls.RebarSpacingConfig(s, c, dstirrup)
    
    placer =  ls.RebarPlacerRow(concreteSection, rebarFactory, configPlacement)

    barType = '30M'
    Nbar = 5
    locationEnum = 1
    
    placer.place(Nbar, barType, locationEnum, 70)
    placer.place(2, '20M', 2, 50)
    return  placer.section


def test_deff_overwrite_bottom():


    section = _init_beam_vertical_placer()
    ls.plotSection(section) 
    # plt.show()
    assert 430 == section.getRebarDepth(posShear = True)
    assert 450 == section.getRebarDepth(posShear = False)


if __name__ == '__main__':

    test_deff_overwrite_bottom()
    # test_placement_side()
