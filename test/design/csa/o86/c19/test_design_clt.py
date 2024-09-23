"""
Checks 8.5.10 from the Canadian CLT handbook.
"""

import limitstates as ls

import limitstates.design.csa.o86.c19 as o86

import pytest

def _init():
    Es = 11700
    Gs = 731
    
    myMatS = ls.MaterialElastic(Es, Gs)
    myMatS.E90 = Es/30
    myMatS.G90 = Gs/13
    myMatS.fb = 28.2
    myMatS.fs = 0.5
    myMatS.name = 'strong axis'
    myMatS.grade = 'test'
    
    Ew = 9000
    Gw = 731
    myMatW = ls.MaterialElastic(Ew, Gw)
    myMatW.E90 = Ew/30
    myMatW.G90 = Gw/13
    myMatW.fb = 7.0
    myMatW.fs = 0.5
    myMatW.name = 'weak axis'
    myMatW.grade = 'test'
    
    # t = 35
    myLayer1 = ls.LayerClt(35, myMatS)
    myLayer2 = ls.LayerClt(35, myMatW, False)
    myLayer1 = ls.LayerClt(35, myMatS)
    
    return [myLayer1, myLayer2, myLayer1, myLayer2, myLayer1]


def _initDB()  -> list[ls.SectionCLT] :
    return o86.loadCltSections()

def test_Panel_Mr():
    
    """
    E1 CLT, with k factor applied.
    """
    
    layers = _init()
    layerGroup = ls.LayerGroupClt(layers)
    section = ls.SectionCLT(layerGroup)
    member = ls.initSimplySupportedMember(6, 'm')
    beamColumn = o86.BeamColumnCltCsa19(member, section)
    
    MrSol = 87.8*1e3
    Mr = o86.checkMrCltBeam(beamColumn)
    
    MrWSol = 12*1e3*0.9
    MrW = o86.checkMrCltBeam(beamColumn,useStrongAxis=False)

    assert MrSol == pytest.approx(Mr, 0.005)
    assert MrWSol == pytest.approx(MrW, 0.04) # There is likely rounding erros in the presented solution.

def test_Panel_Vr():
    
    """
    E1 CLT, with k factor applied.
    """
    
    layers = _init()
    layerGroup = ls.LayerGroupClt(layers)
    section = ls.SectionCLT(layerGroup)
    member = ls.initSimplySupportedMember(6, 'm')
    beamColumn = o86.BeamColumnCltCsa19(member, section)
    
    VrSol = 58*1e3*0.9
    Vr = o86.checkCltBeamShear(beamColumn)
    
    VrWSol = 35*1e3*0.9
    VrW = o86.checkCltBeamShear(beamColumn,useStrongAxis=False)

    assert VrSol == pytest.approx(Vr, 0.01)
    assert VrWSol == pytest.approx(VrW, 0.01) # There is likely rounding erros in the presented solution.



def test_Panel_DB():
    
    """
    Tests E5 245 CLT, from PRG 2019, table A4
    """
    
    sections = _initDB()

    assert 'E1' in sections[0].name

    member = ls.initSimplySupportedMember(6, 'm')
    beamColumn = o86.BeamColumnCltCsa19(member, sections[11])
    
    MrSol = 146*1e3*0.9
    Mr = o86.checkMrCltBeam(beamColumn)
    
    MrWSol = 29*1e3*0.9
    MrW = o86.checkMrCltBeam(beamColumn,useStrongAxis=False)

    assert MrSol == pytest.approx(Mr, 0.005)
    assert MrWSol == pytest.approx(MrW, 0.04) # There is likely rounding erros in the presented solution.
    
    VrSol = 87*1e3*0.9
    Vr = o86.checkCltBeamShear(beamColumn)
    
    VrWSol = 62*1e3*0.9
    VrW = o86.checkCltBeamShear(beamColumn,useStrongAxis=False)

    assert VrSol == pytest.approx(Vr, 0.01)
    assert VrWSol == pytest.approx(VrW, 0.01) # There is likely rounding erros in the presented solution.

if __name__ == '__main__':
    # pass
    test_Panel_Mr()
    test_Panel_Vr()
    
    test_Panel_DB()


    