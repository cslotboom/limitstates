"""
Tests the design of glulam elements according to csa o86
"""

# import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa24()

steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'hss')
section = steelSections[0]

def test_classify_Flange_HSS_305x305():
    """
    Steel book compression tables
    """
    
    section = ls.getByName(steelSections, 'hss304.8x304.8x7.9')
    sClass = s16.classifyFlangeHssSection(section)
    
    assert sClass == 3

    section = ls.getByName(steelSections, 'hss304.8x304.8x9.5')
    sClass = s16.classifyFlangeHssSection(section)
    
    assert sClass == 2
    # section = ls.getByName(steelSections, 'W310x283')
    # sClass = s16.classifyFlangeWSection(section)

    # assert sClass == 1


def test_classify_Flange_HSS_178x128_weak():
    """
    Steel book compression tables
    """
    
    section = ls.getByName(steelSections, 'HSS177.8X127X4.8')
    sClass = s16.classifyFlangeHssSection(section, useX = False)
    
    assert sClass == 3



def test_classify_HSS_overall():
    """
    Table 5-1 steel book
    """
    
    section = ls.getByName(steelSections, 'HSS355.6X203.2X9.5')
    sClass = s16.classifySection(section)
    assert sClass == 1
    Cf80 = 0.8*(0.9*section.getCy())
    sClass = s16.classifySection(section, Cf=Cf80)
    assert sClass == 1
    
    
    section = ls.getByName(steelSections, 'HSS355.6X203.2X7.9')
    sClass = s16.classifySection(section)
    assert sClass == 1

    Cf80 = 0.8*(0.9*section.getCy())
    sClass = s16.classifySection(section, Cf=Cf80)
    assert sClass == 2

    # Class 4 bending    
    section = ls.getByName(steelSections, 'HSS355.6X203.2X4.8')
    sClass = s16.classifySection(section)
    assert sClass == 4

    section = ls.getByName(steelSections, 'HSS203.2X101.6X4.8')
    sClass = s16.classifySection(section)
    assert sClass == 1
    Cf80 = 0.8*(0.9*section.getCy())
    sClass = s16.classifySection(section, Cf=Cf80)
    assert sClass == 1

    section = ls.getByName(steelSections, 'HSS304.8X203.2X6.4')
    sClass = s16.classifySection(section)
    assert sClass == 2
    
    Cf80 = 0.85*(0.9*section.getCy())
    sClass = s16.classifySection(section, Cf=Cf80)
    assert sClass == 3



if __name__ == "__main__":    
    test_classify_Flange_HSS_305x305()
    test_classify_Flange_HSS_178x128_weak()
    test_classify_HSS_overall()
