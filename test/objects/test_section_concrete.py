"""
Author: CS
Date: 202050803
Description:
    Checks if rebar is palced correctly.
"""

import numpy as np

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
    # plt.show()
    assert 430 == section.getRebarMaxDepth(posForce = True)
    assert 450 == section.getRebarMaxDepth(posForce = False)

def test_section_bottom_bar_status():


    section = _init_beam_vertical_placer()
    solution = np.array([True, True, True, True, True, False, False])
    output = section.getBottomBarStatus()
    assert np.all(solution == output)

    solution = np.array([False, False, False, False, False, True, True])
    output = section.getBottomBarStatus(posForce = False)
    assert np.all(solution == output)


def test_section_deff():


    section = _init_beam_vertical_placer()
    solution = 430
    assert solution == approx(section.getdeff())

    solution = 450
    assert solution == approx(section.getdeff(posForce = False))


if __name__ == '__main__':
    test_deff_overwrite_bottom()
    test_section_bottom_bar_status()
    test_section_deff()
