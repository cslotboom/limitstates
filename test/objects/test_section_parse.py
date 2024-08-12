"""
Tests if materials can initalize correctly and use unit conversions.
"""

import limitstates as ls


import limitstates.design.csa.o86.c19 as o86
from limitstates.objects.read import getSteelSections

mats = o86.loadGlulamMaterialDB()
sections = o86.loadGlulamSections(mats[0])

steelSections = getSteelSections(mats[0], 'us', 'aisc_16_si', 'W')


def test_sortAtter():
    """
    Tests Sorting
    """
    newList = ls.sortByAttr(sections, 'd')
    solution = max([item.d for item in sections])
    assert newList[-1].d == solution

def test_sortAtter_2():
    newList = ls.sortByAttr(sections, 'd', False)
    newList2 = ls.sortByAttr(sections, 'Ix', False)
    assert newList[0].d == newList2[0].d

def test_filterAtter_min():
    lowerLim = 500
    filteredList = ls.filterByAttrRange(sections, 'd', lowerLim)
    newMin = min([item.d for item in filteredList])
    assert lowerLim <= newMin

def test_filterAtter_max():
    upperLim = 500
    filteredList = ls.filterByAttrRange(sections, 'd', upperLim = upperLim)
    newMax = max([item.d for item in filteredList])
    assert newMax <= upperLim

def test_filterAtter_minmax():
    lowerLim = 300
    upperLim = 500
    filteredList = ls.filterByAttrRange(sections, 'd', lowerLim, upperLim)
    
    output = [item.d for item in filteredList]
    newMin = min(output)
    newMax = max(output)
    assert lowerLim <= newMin
    assert newMax <= upperLim

def test_filterAtter_name():

    filterVal = 'W460'
    filteredList = ls.filterByName(steelSections, filterVal)

    assert filterVal in filteredList[0].name 
    assert filterVal in filteredList[-1].name


if __name__ == '__main__':
    test_sortAtter()
    test_sortAtter_2()
    test_filterAtter_min()
    test_filterAtter_max()
    test_filterAtter_minmax()

    test_filterAtter_name()
