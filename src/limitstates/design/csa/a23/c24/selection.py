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
# from limitstates import DesignDiagram, SectionConcrete
from limitstates.objects.section.concrete import  getRebarLocationEnum
from .beamColumn import (phiC, phiS, getSectionMr, solveForNA, 
                         getSectionBalancedRho, getSectionAsmin)


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
        raise Exception('The descriminant is less than zero, a larger section is required.')
    
    # get the required amount of steel
    sfactor = rebar.mat.sConvert('MPa')
    fy = rebar.mat.fy * sfactor
    As = alpha* phiC * fc * b / (phiS*fy) * (dEst - discriminant**0.5)

    return As   

def _checkMr(section, yMoment, posMoment):
    NA    = solveForNA(section, yMoment, posMoment)
    MrSol = getSectionMr(section, NA, yMoment, posMoment)
    return MrSol

def _getNbarReq(Mr, dEst, section, rebar, b):

    As   = getRequiredSteelForMr(Mr, section.concrete.mat, rebar, dEst, b)
    Asmin = getSectionAsmin(section)
    As = max(As, Asmin)
    NbarReq = ceil(As/rebar.A)
    
    return NbarReq

def _isOverReinforced(rhoBA, rhoNet):
    isOverReinforced = False
    if rhoBA <= rhoNet:
        isOverReinforced = True

    return isOverReinforced
 

def setBottomSteelForMr(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        sectionInd: int = 0,
                        yMoment: bool = True,
                        posMoment: bool = True,
                        matRebar: MaterialRebarCSA24 = None,
                        addTopSteel: bool = True, 
                        runDesignItertion: bool = True,
                        placementStrategy: int = 1, 
                        lUnit: str = 'mm'):

    """
    Places bottom steel in a section. The the rebar will be placed such that
    the section has a moment capacity larger, than the input moment, if it is 
    possible to find a solution.
    
    The minimum steel will be used for the section, if it is larger than the
    required steel.

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

    Returns
    -------
    isOverReinforced : bool
        DESCRIPTION.

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
    designProps = element.designProps

    # get the width and depth of the section.
    b = section.getWidth(yMoment, lUnit)    
    d = section.getDepth(yMoment, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yMoment, posMoment)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)
    
    Nrow  = len(section.rebar)
    bottomBarInds = list(range(Nrow))
    
    
    # Check if the beam is over-reinforced
    dEstBot = section.getdeff(yMoment, posMoment, lUnit)
    rhoBA   = getSectionBalancedRho(section)
    rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

    # # Add top bars if the secton is over reinforced.
    isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
    if isOverReinforced:
        drho  = rhoNet - rhoBA
        _placeTopBarIfOverreinforced(element, sectionInd, yMoment, posMoment,  
                                     drho, barType, rebar, lUnit)   

    if runDesignItertion:
        _runDesignIteration(Mr, element, barType, NbarReq, bottomBarInds,
                            rebar,sectionInd, yMoment, posMoment, lUnit)
       
    return isOverReinforced



def _initalBottomBarPlacement(Mr, element, sectionInd, yMoment, posMoment,  
                                 barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    # Get the section, and reset the rebar in the section.
    section = element.getSection(sectionInd)
    section.rebar = None
    
    designProps = element.designProps

    # get the width and depth of the section.
    b = section.getWidth(yMoment, lUnit)    
    d = section.getDepth(yMoment, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yMoment, posMoment)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)





def _placeTopBarIfOverreinforced(element, sectionInd, yMoment, posMoment,  
                                 drho, barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    designProps = element.designProps
    section = element.getSection(sectionInd)
    b = section.getWidth(yMoment, lUnit)    
    d = section.getDepth(yMoment, lUnit)
    
    AsTop = (b * d) * drho
    NbarReqTop = ceil(AsTop / rebar.A)
    if NbarReqTop < 2:
        NbarReqTop = 2

    
    location = getRebarLocationEnum(yMoment, not posMoment)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReqTop, barType, location)


def _runDesignIteration(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        NbarReq:int,
                        bottomBarInds,
                        rebar,
                        sectionInd: int = 0,
                        yMoment: bool = True,
                        posMoment: bool = True,
                        lUnit: str = 'mm'):
       
    """
    There are two scenerios: 
        We need to add more bars, (dest was too big)
        We can reduce the number of bars

        To deal with 1, we add check the moment is smaller than, and add bars
        if it isn't
        
        To deal with 2, we try to reduce the number of bars required, until 
        reaching failure

    """
    designProps = element.designProps
    section = element.getSection(sectionInd)
    b = section.getWidth(yMoment, lUnit)    


    NA    = solveForNA(section, yMoment, posMoment)
    MrSol = getSectionMr(section, NA, yMoment, posMoment) / 1000
    momentLow = MrSol < Mr

    hasTopBars = len(bottomBarInds) != len(section.rebar)

    if momentLow:
        atMin = True 
    else:
        atMin = False
    
    
    while momentLow or not atMin:
        
        # If the moment is too small, increase the number of bars
        if momentLow:
            NbarReq = NbarReq + 1
        else:
            NbarReq = NbarReq - 1
        
        # Remove the bottom bars
        section.rebar.removeGroups(bottomBarInds)
        NgroupsTop = len(section.rebar)
            
        location = getRebarLocationEnum(yMoment, posMoment)
        placer   = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
        placer.place(NbarReq, barType, location)
        
        if not hasTopBars:
            dEstBot = section.getdeff(yMoment, posMoment, lUnit)
            rhoBA   = getSectionBalancedRho(section)
            rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

            # # Add top bars if the secton is over reinforced.
            isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
            
            if isOverReinforced:
                drho  = rhoNet - rhoBA
                _placeTopBarIfOverreinforced(element, sectionInd, yMoment, 
                                             posMoment,  drho, barType, rebar, 
                                             lUnit)
            
                hasTopBars = True

        
        # Remove update teh bottom bar inds for later removal.
        Ngroups = len(section.rebar)
        bottomBarInds = list(range(NgroupsTop, Ngroups))

        NA = solveForNA(section, yMoment, posMoment, NAtrial=NA)
        MrSol = getSectionMr(section, NA, yMoment, posMoment)  / 1000
        
        momentLow = MrSol < Mr
        if momentLow:
            atMin = True
    
