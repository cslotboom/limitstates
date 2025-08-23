"""
Contains the code designc clauses
"""
# from enum import IntEnum
from math import ceil

import limitstates as ls

from .element import BeamColumnConcreteCsa24 
from .section import REBARFACTORY, loadRebarFactory, Rebar
from .material import MaterialRebarCSA24, MaterialConcreteCSA24
from .rebarPlacers import RebarPlacerRowCSA24, placeRebarInElement
from limitstates import DesignDiagram, SectionConcrete
from limitstates.objects.section.concrete import SectionNASolver, RebarSpacingConfig, getRebarLocationEnum, SectionConcrete
from .beamColumn import phiC, phiS, getSectionMr, solveForNA



def getRequiredSteelForMr(Mr:float, 
                        mat: MaterialConcreteCSA24,
                        rebar: Rebar,
                        dEst: float, 
                        b: float):
    """
    Determines a As required, given a moment, a section, a estimate of the 
    effective depth, and the sections width. 

    Parameters
    ----------
    Mr : float
        The applied moment the beam is being designed for.
        The moment must have a positive value, direction of the moment is set
        by the flag "posMoment"
    section : SectionConcrete
        The section to check.
    rebar : Rebar
        The rebar to be used in the section.
    dEst : float
        The estimated depth of the section.
    b : float
        The width of the section.

    Returns
    -------
    As : float
        The required area area in mm2.

    """
    # Calculate the required according to the "direct" method
    sfactor = mat.sConvert('MPa')
    fc = mat.fc * sfactor
    alpha = mat.alpha    
    
    # get the discriminant of the sections rebar. 
    discriminant =  (dEst**2 - 1e6 *2*Mr / (phiC*alpha*fc*b))
    
    # If the discriminant is less than zero, no amount of rebar will fufil the
    # section requirements.
    if discriminant < 0:
        raise Exception('The descriminant is less than zero, a large section is required.')
    
    # get the required amount of steel
    sfactor = rebar.mat.sConvert('MPa')
    fy = rebar.mat.fy * sfactor
    As = alpha* phiC * fc * b / (phiS*fy) * (dEst - discriminant**0.5)

    return As   

def setBottomSteelForMr(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        sectionInd: int = 0,
                        yMoment: bool = True,
                        posMoment: bool = True,
                        matRebar: MaterialRebarCSA24 = None,
                        lUnit: str = 'mm'):
    """
    Places bottom steel in a section. The the rebar will be placed such that
    the section has a moment capacity larger, than the input moment, if it is 
    possible to find a solution.

    Parameters
    ----------
    Mr : float
        The applied moment the beam is being designed for.
        The moment must have a positive value, direction of the moment is set
        by the flag "posMoment"
    element : BeamColumnConcreteCsa24
        The beamcolumn element to place rebar in .
    barType : str
        The type of rebar to be used. Must be a valid canadian rebar type,
        i.e. 10M, 15M, 20M, 25M, 30M, 35M, 40M, 45M.
    sectionInd : int, optional
        If there are multiple sections in the beamcolumn element, this variable
        can be set to modify which section to place rebar in. The default is 0,
        which places it in the first concrete section.
    yMoment : bool, optional
        A flg that specifies if the moment is applied in the y or x direction. 
        The default is True, which applies moment in the y direction, i.e.,
        about the x axis.
    posMoment : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.
    matRebar : MaterialRebarCSA24, optional
        The material to use for the rebar. The default is 400MPa steel.
    lUnit : str, optional
        The length unit to use for the rebar added. The default is in 'mm'.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    None.

    """
  
    
    # Init the material and rebar factory.
    if matRebar is None:
        rebar = REBARFACTORY.getRebar(barType, lUnit)    
    else:
        factory = loadRebarFactory(matRebar, lUnit)
        rebar = factory.getRebar(barType, lUnit) 
    
    # Get the section, and reset the rebar in the section.
    section = element.getSection(sectionInd)
    section.rebar = None

    # get the width and depth of the section.
    b = section.getWidth(yMoment, lUnit)    
    d = section.getDepth(yMoment, lUnit)
    
    # estimate where the rebar in the section is placed
    dEst = d*0.9 
    As   = getRequiredSteelForMr(Mr, section.concrete.mat, rebar, dEst, b)
    NbarReq = ceil(As/rebar.A)
    
    location = getRebarLocationEnum(yMoment, posMoment)
    placementKwargs = {'location':location}
    
    placeRebarInElement(element, NbarReq, barType, sectionInd,
                        placementKwargs = placementKwargs,
                        rebarMat = rebar.mat,
                        lUnit = lUnit)

    NA = solveForNA(section, yMoment, posMoment)
    MrSol = getSectionMr(section, NA, yMoment, posMoment)
    if MrSol < Mr:
        placeRebarInElement(element, NbarReq + 1, barType, sectionInd,
                            placementKwargs = placementKwargs,
                            rebarMat = rebar.mat,
                            lUnit = lUnit)

    # TODO: fix
    dEst = d - section.getdeff(yMoment, posMoment, lUnit)
    As = getRequiredSteelForMr(Mr, section.concrete.mat, rebar, dEst, b)
    NbarReqNew = ceil(As/rebar.A)
    
    # If the new section requires
    if NbarReqNew < NbarReq:
        placeRebarInElement(element, NbarReq, barType, sectionInd,
                            placementKwargs = placementKwargs,
                            rebarMat = rebar.mat,
                            lUnit = lUnit)