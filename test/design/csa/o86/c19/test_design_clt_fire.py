"""
Checks values from the CSA wood design manual.
Checks 8.5.9 from the Canadian CLT handbook.

"""

from limitstates import MaterialElastic, LayerClt, LayerGroupClt, SectionCLT, initSimplySupportedMember

import limitstates.design.csa.o86.c19 as o86

import pytest


import limitstates as ls
import numpy as np
mm = 0.001
m = 1
MPa = 1
# Length = 6*m


# =============================================================================
# Import sections using a design library
# =============================================================================

"""
The easiest way to load sections, is to use functions that load them directly
from the design libary..
"""



def _init()  -> list[SectionCLT] :
    return o86.loadCltSections()


def test_Panel_dims_fail():
    
    """
    Test what happens if we burn through a whole panel.
    We expect at least one empty layer.
    """
    
    # layers = 
    sections = _init()
    section = sections[16]
    FRR = 900
    cltLayers = o86.getCLTBurnDims(np.array([FRR]), section)
    
    assert cltLayers[0].t == 0

def test_Panel_WoodHandbook_dims():
    
    """
    Example 1 of fire design in wood design handbook.
    Checks the dimensions work out okay.
    """
    
    # layers = 
    sections = _init()
    section = sections[16]
    member = ls.initSimplySupportedMember(6, 'm')

    beamColumn = o86.BeamColumnCltCsa19(member, section)

    FRR = 90
    
    cltLayers = o86.getCLTBurnDims(np.array([FRR]), section)
    
    assert len(cltLayers) == 3
    assert cltLayers.d == pytest.approx(96, 0.001) 
    


def test_Panel_WoodHandbook_Dims_2():
    
    """
    Example 1 of fire design in wood design handbook.
    Checks the dimensions work out okay when we use the raw objects

    """
    
    # layers = 
    sections = _init()
    section = sections[16]
    firePortection = o86.GypusmFlatCSA19('15.9mm')
    designProps = o86.DesignPropsClt19(firePortection)

    member = ls.initSimplySupportedMember(6, 'm')

    clt = o86.BeamColumnCltCsa19(member, section, designProps = designProps)


    FRR = 120
    o86.setFireSectionCltCSA(clt, FRR)
    
    cltLayers = clt.designProps.sectionFire.sLayers
    
    assert len(cltLayers) == 3
    assert cltLayers.d == pytest.approx(96, 0.001) 



# def test_Panel_WoodHandbook_Dims_Tables():
    
#     """
#     Example 1 of fire design in wood design handbook.
#     Checks the dimensions work out okay when we use the raw objects

#     """
    
#     # layers = 
#     sections = _init()
#     section = sections[16]
#     designProps = o86.DesignPropsClt19()

#     member = ls.initSimplySupportedMember(4, 'm')

#     clt = o86.BeamColumnCltCsa19(member, section, designProps = designProps)


#     FRR = 45
#     o86.setFireSectionCltCSA(clt, FRR)
    
#     cltLayers = clt.designProps.fireSection.sLayers
    
#     assert len(cltLayers) == 3
#     assert cltLayers.d == pytest.approx(96, 0.001) 
    
    
def test_Panel_WoodHandbook_Design():
    
    """
    Example 1 of fire design in wood design handbook.
    Checks the dimensions work out okay when we use the raw objects

    """
    
    sections = _init()
    section = sections[16]
    firePortection = o86.GypusmFlatCSA19('15.9mm')
    designProps = o86.DesignPropsClt19(firePortection)

    member = ls.initSimplySupportedMember(6, 'm')

    clt = o86.BeamColumnCltCsa19(member, section, designProps = designProps)
    FRR = 120
    o86.setFireSectionCltCSA(clt, FRR)
    knet = o86.kdfi*o86.kfi['cltV']

    Mr = o86.checkMrCltBeam(clt, knet, useFire = True)    
    
    MrSol = 23.6*1e3
    
    assert MrSol == pytest.approx(Mr, 0.01) 
        
        
def test_Panel_WoodHandbook_Tables_Design():
    
    """
    uses tables to estimate Mx and My in fire.
    Note, the 

    """
    
    sections = _init()
    section = sections[0]

    member = ls.initSimplySupportedMember(6, 'm')
    clt = o86.BeamColumnCltCsa19(member, section)
    FRR = 45
    o86.setFireSectionCltCSA(clt, FRR, 0.65)
    knet = o86.kdfi*o86.kfi['cltE']

    Mrx = o86.checkMrCltBeam(clt, knet, useFire = True)    
    Mry = o86.checkMrCltBeam(clt, knet, useFire = True, useStrongAxis=False)    
    
    MrxSol = 7.03*1e3
    MrySol = 1.91*1e3
    
    assert MrxSol == pytest.approx(Mrx, 0.01) 
    assert MrySol == pytest.approx(Mry, 0.01) 
    
# def test_Panel_CLTWoodHandbook():
    
#     """
#     E1 CLT, with k factor applied.
#     """
    
#     # layers = 
#     sections = _init()
#     section = sections[16]
#     firePortection = o86.GypusmFlatCSA19('15.9mm')
#     designProps = o86.DesignPropsClt19(firePortection)
#     # beamColumn = ls.getBeamColumn(6, section)
#     member = ls.initSimplySupportedMember(6, 'm')

#     beamColumn = o86.BeamColumnCltCsa19(member, section)

#     FRR = 60
    
#     cltLayers = o86.getCLTBurnDims(np.array([FRR]), section)
    
    
    # o86.setBurntSection(beamColumn, FRR)       
    # MrSol = 87.8*1e3
    # Mr = o86.checkMrCltBeam(beamColumn)
    
    # MrWSol = 12*1e3*0.9
    # MrW = o86.checkMrCltBeam(beamColumn,useStrongAxis=False)

    # assert MrSol == pytest.approx(Mr, 0.005)
    # assert MrWSol == pytest.approx(MrW, 0.04) # There is likely rounding erros in the presented solution.

def test_Panel_Vr():
    
    """
    E1 CLT, with k factor applied.
    """
    
    layers = _init()
    
    
    
def test_Beam_GAeff():
    
    """
    There are no tests for the, but GAeff is shown in a FP Innovations example
    8.5.10
    """
    
    sections = _init()
    section = sections[1]

    
    firePortection = o86.GypusmFlatCSA19('15.9mm')
    designProps = o86.DesignPropsClt19(firePortection)
    member = ls.initSimplySupportedMember(6, 'm')
    clt = o86.BeamColumnCltCsa19(member, section, designProps=designProps)
    FRR = 120
    o86.setFireSectionCltCSA(clt, FRR)
    # knet = o86.kdfi*o86.kfi['cltE']
    
    GAx = clt.designProps.sectionFire.getGAs()
    GAxsol = 9.03e6
    assert GAx == pytest.approx(GAxsol, 0.01) 

    # assert (abs(GAx / (GAxsol) - 1)  < 0.01)
    # layerGroup = LayerGroupClt(layers)
    # section = SectionCLT(layerGroup)
    # member = initSimplySupportedMember(6, 'm')
    # beamColumn = o86.BeamColumnCltCsa19(member, section)
    
    # VrSol = 58*1e3*0.9
    # Vr = o86.checkCltBeamShear(beamColumn)
    
    # VrWSol = 35*1e3*0.9
    # VrW = o86.checkCltBeamShear(beamColumn,useStrongAxis=False)

    # assert VrSol == pytest.approx(Vr, 0.01)
    # assert VrWSol == pytest.approx(VrW, 0.01) # There is likely rounding erros in the presented solution.


if __name__ == '__main__':
    # pass
    test_Panel_dims_fail()
    test_Panel_WoodHandbook_dims()
    test_Panel_WoodHandbook_Dims_2()
    test_Panel_WoodHandbook_Design()
    test_Panel_WoodHandbook_Tables_Design()
    
    test_Beam_GAeff()
    test_Panel_Vr()


    