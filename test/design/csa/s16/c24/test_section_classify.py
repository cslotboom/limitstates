"""
Tests the design of glulam elements according to csa o86
"""

# import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

from limitstates.objects.read import getSteelSections

mat = s16.MaterialSteelCsa24()

steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')



def test_classify_Flange_W_W460x464():
    section = ls.getByName(steelSections, 'W460x464')
    sClass = s16.classifyFlangeWSection(section)
    
    assert sClass == 1

    section = ls.getByName(steelSections, 'W310x283')
    sClass = s16.classifyFlangeWSection(section)

    assert sClass == 1



def test_classify_W_flexure_major():
    """
    Table 5-1 steel book
    """
    section = ls.getByName(steelSections, 'W460x464')
    sClass = s16.classifySection(section)
    
    assert sClass == 1

    section = ls.getByName(steelSections, 'W250x17.9')
    sClass = s16.classifyFlangeWSection(section)

    assert sClass == 3

    section = ls.getByName(steelSections, 'W530x82')
    sClass = s16.classifyFlangeWSection(section)

    assert sClass == 2

    section = ls.getByName(steelSections, 'W610x155')
    sClass = s16.classifyFlangeWSection(section)

    assert sClass == 2

def test_classify_W_flexure_major_compression():
    """
    Table 4-3 steel book
    """
    section = ls.getByName(steelSections, 'W1000x222')
    Cy = section.Cy
    sClass = s16.classifySection(section, Cf = Cy*0.2*0.9)
    assert sClass == 2

    sClass = s16.classifySection(section, Cf = Cy*0.62*0.9)
    assert sClass == 3


    section = ls.getByName(steelSections, 'W530x150')
    Cy = section.Cy
    sClass = s16.classifySection(section, Cf = Cy*0.8*0.9)
    assert sClass == 1

    sClass = s16.classifySection(section, Cf = Cy*0.92*0.9)
    assert sClass == 2

    sClass = s16.classifySection(section, Cf = Cy*0.938*0.9)
    assert sClass == 3





if __name__ == "__main__":
    
    
    test_classify_Flange_W_W460x464()
    test_classify_W_flexure_major()
    test_classify_W_flexure_major_compression()
    # test_kLa()
    # test_kLb()
    # test_kLc2()
    # test_bending_table_1()
    
    # test_compression_Design_Example_Cc()
    # test_compression_Design_Example_Pr()
    # test_compression_Table()
    
    # test_Interaction_ecc()
    # test_Interaction_ecc_table()
