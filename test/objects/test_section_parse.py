"""
Tests if materials can initalize correctly and use unit conversions.
"""

from limitstates import MaterialElastic, SectionRectangle
import pytest

import limitstates as ls

import limitstates.design.csa.o86.c19 as o86
mats = o86.loadGlulamMaterialDB()
sections = o86.loadGlulamSections(mats[0])



def test_sortAtter():
    """
    Tests Sorting
    """
    newList = ls.sortSectionsByAttr(sections, 'd')
    solution = max([item.d for item in sections])
    assert newList[-1].d == solution

def test_sortAtter_2():
    newList = ls.sortSectionsByAttr(sections, 'd', False)
    newList2 = ls.sortSectionsByAttr(sections, 'Ix', False)
    assert newList[0].d == newList2[0].d

def test_filterAtter_min():
    lowerLim = 500
    filteredList = ls.filterSectionsByAttr(sections, 'd', lowerLim)
    newMin = min([item.d for item in filteredList])
    assert lowerLim <= newMin

def test_filterAtter_max():
    upperLim = 500
    filteredList = ls.filterSectionsByAttr(sections, 'd', upperLim = upperLim)
    newMax = max([item.d for item in filteredList])
    assert newMax <= upperLim

def test_filterAtter_minmax():
    lowerLim = 300
    upperLim = 500
    filteredList = ls.filterSectionsByAttr(sections, 'd', lowerLim, upperLim)
    
    output = [item.d for item in filteredList]
    newMin = min(output)
    newMax = max(output)
    assert lowerLim <= newMin
    assert newMax <= upperLim



if __name__ == '__main__':
    test_sortAtter()
    test_sortAtter_2()
    test_filterAtter_min()
    test_filterAtter_max()
    test_filterAtter_minmax()
    # test_SectionProps()
    # test_convertSectionUnits()
