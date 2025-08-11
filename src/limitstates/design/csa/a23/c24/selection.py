"""
Contains the code designc clauses
"""
# from enum import IntEnum
from math import ceil

import limitstates as ls

from .element import BeamColumnConcreteCsa24 
from .section import REBARFACTORY, loadRebarFactory
from .material import MaterialRebarCSA24
from .rebarPlacers import RebarPlacerRowCSA24, placeRebarInElement
from limitstates import DesignDiagram, SectionConcrete
from limitstates.objects.section.concrete import SectionNASolver, RebarSpacingConfig
from .beamColumn import phiC, phiS, getSectionMr, solveForNA

def setBottomSteelForMr(Mr:float, 
                        element:BeamColumnConcreteCsa24, 
                        barType:str,
                        sectionInd:int = 0,
                        yMoment:bool = True,
                        positiveMoment = True,
                        matRebar:MaterialRebarCSA24 = None,
                        lUnit:str = None):
    
    if lUnit is None:
        lUnit = 'mm'
        
    if matRebar is None:
        rebar = REBARFACTORY.getRebar(barType, lUnit)    
    else:
        factory = loadRebarFactory(matRebar, lUnit)
        rebar = factory.getRebar(barType, lUnit) 
    
    section = element.getSection(sectionInd)
    section.rebar = None

    b = section.getWidth(yMoment, positiveMoment, lUnit)    
    d = section.getDepth(yMoment, positiveMoment, lUnit)
    
    dEst = d*0.9
    sfactor = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sfactor
    alpha = section.concrete.mat.alpha
    
    
    discriminant =  (dEst**2 - 1e6 *2*Mr / (phiC*alpha*fc*b))
    
    if discriminant < 0:
        raise Exception('The descriminant is less than zero, a large section is required.')
    
    sfactor = rebar.mat.sConvert('MPa')

    fy = rebar.mat.fy * sfactor
    As = alpha* phiC * fc * b / (phiS*fy) * (dEst - discriminant**0.5)

    NbarReq = ceil(As/rebar.A)

    placementKwargs = {'location':1}
    
    placeRebarInElement(element, NbarReq, barType, sectionInd,
                        placementKwargs = placementKwargs,
                        rebarMat = rebar.mat,
                        lUnit = lUnit)



    NA = solveForNA(section, yMoment, positiveMoment)
    MrSol = getSectionMr(section, NA, yMoment, positiveMoment)
    if MrSol < Mr:
        placeRebarInElement(element, NbarReq + 1, barType, sectionInd,
                        placementKwargs = placementKwargs,

                            rebarMat = rebar.mat,
                            lUnit = lUnit)


    # TODO: fix
    dEst = d - section.rebar.getdeff()
    
    discriminant =  (dEst**2 - 1e6 *2*Mr / (phiC*alpha*fc*b))
    if discriminant < 0:
        raise Exception('The descriminant  is less zero, a large section is required.')
    As = alpha* phiC * fc * b / (phiS*fy) * (dEst - discriminant**0.5)
    NbarReqNew = ceil(As/rebar.A)
    
    if NbarReqNew < NbarReq:
        placeRebarInElement(element, NbarReq, barType, sectionInd,
                            placementKwargs = placementKwargs,
                            rebarMat = rebar.mat,
                            lUnit = lUnit)