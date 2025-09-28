"""
Contains the code designc clauses
"""
from enum import IntEnum
from math import ceil, floor

import limitstates as ls
from limitstates.objects.section.concrete import  getRebarLocationEnum

from .element import BeamColumnConcreteCsa24, ShearConfigurations, phiC, phiS
from .section import REBARFACTORY, loadRebarFactory, Rebar
from .material import MaterialRebarCSA24, MaterialConcreteCSA24
from .rebarPlacers import RebarPlacerRowCSA24, placeRebarInElement
# from limitstates import DesignDiagram, SectionConcrete
from .beamColumn import (getSectionBalancedRho, getSectionAsmin, getElementVrc,
                         getElementVrs, getElementVmax, getElementVr, 
                         getElementSmax, getElementSminForVrs,
                         getElementSmaxGeom, getElementSmaxStirrup)
from .nasolver import getSectionMr, solveForNA


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
        by the flag "posForce"
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

def _checkMr(section, yForce, posForce):
    NA    = solveForNA(section, yForce, posForce)
    MrSol = getSectionMr(section, NA, yForce, posForce)
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

def designBottomSteelForMr(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        sectionInd: int = 0,
                        yForce: bool = True,
                        posForce: bool = True,
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
        by the flag "posForce"
    element : BeamColumnConcreteCsa24
        The beamcolumn element to place rebar in .
    barType : str
        The type of rebar to be used. Must be a valid canadian rebar type,
        i.e. 10M, 15M, 20M, 25M, 30M, 35M, 40M, 45M.
    sectionInd : int, optional
        If there are multiple sections in the beamcolumn element, this variable
        can be set to modify which section to place rebar in. The default is 0,
        which places it in the first concrete section.
    yForce : bool, optional
        A flg that specifies if the moment is applied in the y or x direction. 
        The default is True, which applies moment in the y direction, i.e.,
        about the x axis.
    posForce : bool, optional
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
    b = section.getWidth(yForce, lUnit)    
    d = section.getDepth(yForce, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yForce, posForce)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)
    
    Nrow  = len(section.rebar)
    bottomBarInds = list(range(Nrow))
    
    
    # Check if the beam is over-reinforced
    dEstBot = section.getdeff(yForce, posForce, d / 2, lUnit)
    rhoBA   = getSectionBalancedRho(section)
    rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

    # # Add top bars if the secton is over reinforced.
    isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
    if isOverReinforced:
        drho  = rhoNet - rhoBA
        _placeTopBarIfOverreinforced(element, sectionInd, yForce, posForce,  
                                     drho, barType, rebar, lUnit)   

    if runDesignItertion:
        _runDesignIteration(Mr, element, barType, NbarReq, bottomBarInds,
                            rebar,sectionInd, yForce, posForce, lUnit)
       
    return isOverReinforced

def _initalBottomBarPlacement(Mr, element, sectionInd, yForce, posForce,  
                                 barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    # Get the section, and reset the rebar in the section.
    section = element.getSection(sectionInd)
    section.rebar = None
    
    designProps = element.designProps

    # get the width and depth of the section.
    b = section.getWidth(yForce, lUnit)    
    d = section.getDepth(yForce, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yForce, posForce)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)

def _placeTopBarIfOverreinforced(element, sectionInd, yForce, posForce,  
                                 drho, barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    designProps = element.designProps
    section = element.getSection(sectionInd)
    b = section.getWidth(yForce, lUnit)    
    d = section.getDepth(yForce, lUnit)
    
    AsTop = (b * d) * drho
    NbarReqTop = ceil(AsTop / rebar.A)
    if NbarReqTop < 2:
        NbarReqTop = 2

    
    location = getRebarLocationEnum(yForce, not posForce)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReqTop, barType, location)


def _runDesignIteration(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        NbarReq:int,
                        bottomBarInds,
                        rebar,
                        sectionInd: int = 0,
                        yForce: bool = True,
                        posForce: bool = True,
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
    b = section.getWidth(yForce, lUnit)    


    NA    = solveForNA(section, yForce, posForce)
    MrSol = getSectionMr(section, NA, yForce, posForce) / 1000
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
            
        location = getRebarLocationEnum(yForce, posForce)
        placer   = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
        placer.place(NbarReq, barType, location)
        
        if not hasTopBars:
            # XXX: Consider recalculating NA Nocation
            dEstBot = section.getdeff(yForce, posForce, NA, lUnit)
            rhoBA   = getSectionBalancedRho(section)
            rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

            # # Add top bars if the secton is over reinforced.
            isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
            
            if isOverReinforced:
                drho  = rhoNet - rhoBA
                _placeTopBarIfOverreinforced(element, sectionInd, yForce, 
                                             posForce,  drho, barType, rebar, 
                                             lUnit)
            
                hasTopBars = True

        
        # Remove update teh bottom bar inds for later removal.
        Ngroups = len(section.rebar)
        bottomBarInds = list(range(NgroupsTop, Ngroups))

        NA = solveForNA(section, yForce, posForce, NAtrial=NA)
        MrSol = getSectionMr(section, NA, yForce, posForce)  / 1000
        
        momentLow = MrSol < Mr
        if momentLow:
            atMin = True
    

class ShearResultEnum(IntEnum):
    rebarPlaced = 1
    noRebarPlaced = 2
    noSolutionPossible = 3
    designFailed = 4
    


# def _get_initial_Vc(element, sectionInd, dvEstimate, dbar, logging):
        
#     # Initial Vc calculation
#     if not element.rebar:
#         printIfLogging(logging, f'No longditudinal bars found, attempting to use estimate.')
#         dvEstimate = None
#     elif not dvEstimate:
#         printIfLogging(logging, f'No dv estimate given, estimating dv.')
#         h = element.
#         dvEstimate = element.designProps.cover + dbar + 25
#         printIfLogging(logging, f'dv estimated as {dvEstimate}.')
        
#     Vc = getElementVrc(element, sectionInd, yForce, posForce, 
#                        dvEstimate = dvEstimate) 


    
# def printIfLogging(string, logging):
#     if logging:
#         print(string)

# TODO: implement designer superclass?
class StirrupDesigner:
    
    def __init__(self, Vr: float, 
                        element: BeamColumnConcreteCsa24, 
                        sectionInd: int = 0,
                        yForce: bool = True,
                        posForce: bool = True,
                        barType: str = '10M',
                        ds: float = 50,
                        smin: float = 100,
                        NlegMax: int = 8,
                        dvEstimate: float = None,
                        logging = False,
                        logFunction = print):
        """
        The rebar material used will be 400MPa rebar.
        """
        
        self.Vr = Vr 
        self.element = element
        self.sectionInd = sectionInd
        self.designSection = element.getSection(sectionInd)
        
        self.yForce = yForce
        self.posForce = posForce
        
        self.ds = ds
        self.smin = smin
        self.NlegMax  = NlegMax
        
        self.dvEstimate = dvEstimate

        
        self.barType = barType
        # self.matRebar = matRebar
        self.rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
        # if matRebar:
        #     self.rebar.setMat(matRebar)

        self.logging = logging
        self.logFunction = logFunction
        

    def log(self, string):
        if self.logging:
            self.logFunction(string)
        
    def getdvEst(self):
        element = self.element
        section = self.designSection
        dbar = self.rebar.d
        
        
        if self.dvEstimate:
            dvEstimate = self.dvEstimate
            self.log('Using manual dv estimate.')
        elif section.rebar:
            dvEstimate = None
            self.log('Using dv calculated from rebar.')
        else:
            self.log("No longditudinal bars found, and no manual dv estimate"\
                     " given, estimating dv.")
            h = section.getDepth(self.yForce, 'mm')
            dvEstimate = h - (element.designProps.cover + dbar + 25)
            self.log(f'dv estimated as: {dvEstimate}')
        
        return dvEstimate

    def VcCalc(self, dvEst):
        return getElementVrc(self.element, self.sectionInd, self.yForce, 
                           self.posForce, dvEstimate = dvEst)


    def _roundSmin(self, sminTrial):
        return floor( sminTrial / self.ds) * self.ds


    def runTrial(self, VsReq, NlegTrial, sMaxGeom, dvEst):
        
        smin = self.smin       
        sminTrial = getElementSminForVrs(self.element, VsReq, self.sectionInd,
                                         self.barType, NlegTrial, dvEst,
                                         self.yForce, self.posForce)
        
        sMaxRebar = getElementSmaxStirrup(self.element, self.sectionInd, 
                                          self.barType, NlegTrial, 
                                          self.rebar.mat.fy, self.yForce)

        sMax = min(sMaxGeom, sMaxRebar)
        # Do we have a valid solution?
        if sminTrial > sMax:
            sminTrial = sMax

        sBar = self._roundSmin(sminTrial)
        
        if smin < sBar:
            return sBar, True
        else:
            return sBar, False

    def runDesignIteration(self, VsReq, dvEst, SMaxgeom):
        

        NlegTrial = 2
        solution = False
        while not solution and (NlegTrial <= self.NlegMax):           
            spacing, solution = self.runTrial(VsReq, NlegTrial, SMaxgeom, dvEst)
            if not solution:
                NlegTrial += 2
                
        return spacing, solution, NlegTrial


    # def runDesignCleanup(self, s, Nleg, dvEst, Vrmax):
    #     stirrups = ls.StirrupGroup(self.rebar, s, Nleg, 'mm')
    #     self.designSection.stirrups = stirrups

    #     VrOut = getElementVr(self.element, self.sectionInd, 
    #                          self.yForce, self.posForce, dvEst)
    
    #     # If we are now greater than Vmax/2, the maximum spacing has changed.
    #     # TODO: add iteration if greater than new smax
    #     SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
    #                                   self.yForce, self.posForce, 
    #                                   dvEst, VrOut, Vrmax)

        # SMaxgeom < s:
            
        # if sBar = self._roundSmin(sminTrial)




    def design(self) -> (float, ShearResultEnum):
        designProps = self.element.designProps
        designProps.shearReinforcementType = ShearConfigurations.NoTransverse
        # dbar  = self.rebar.d
        
        Vr    = self.Vr
        dvEst = self.getdvEst()
        
        
        # Case 1: the section needs no reinforcing.
        Vc    = self.VcCalc(dvEst)
        if Vr < Vc:
            return Vc, ShearResultEnum.noRebarPlaced
        
        # Case 2: Vrmax is exceeded.
        Vrmax = getElementVmax(self.element, self.sectionInd, 
                               self.yForce, self.posForce, dvEst)
        if Vr > Vrmax:
            self.log(f'No stirrup design possible for {self.designSection},\
                  Vr = {round(Vr)} > Vrmax = {round(Vrmax)}')
            return Vc, ShearResultEnum.noSolutionPossible

        # Case 3: Try to find a spacing / Nleg pairing.
        # TODO: update so this is not tied to a section,
        designProps = self.element.designProps
        designProps.shearReinforcementType = ShearConfigurations.MinTransverse
        Vc    = self.VcCalc(dvEst)
        
        VsReq = Vr - Vc
        SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
                                        self.yForce, self.posForce, 
                                        dvEst, Vr, Vrmax)

        s, isSol, Nleg = self.runDesignIteration(VsReq, dvEst, SMaxgeom)
        
        # Set the solution and do some final clean up
        if isSol:
            stirrups = ls.StirrupGroup(self.rebar, s, Nleg, 'mm')
            self.designSection.stirrups = stirrups

            VrOut = getElementVr(self.element, self.sectionInd, 
                                 self.yForce, self.posForce, dvEst)
        
            # If we are now greater than Vmax/2, the maximum spacing has changed.
            # TODO: add iteration if greater than new smax
            SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
                                          self.yForce, self.posForce, 
                                          dvEst, Vr, Vrmax)
            
        if SMaxgeom < s:
            s, isSol, Nleg = self.runDesignIteration(VsReq, dvEst, SMaxgeom)
            stirrups = ls.StirrupGroup(self.rebar, s, Nleg, 'mm')
            self.designSection.stirrups = stirrups
            

            VrOut = getElementVr(self.element, self.sectionInd, 
                                 self.yForce, self.posForce, dvEst)
        
            # If we are now greater than Vmax/2, the maximum spacing has changed.
            SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
                                          self.yForce, self.posForce, 
                                          dvEst, Vr, Vrmax)
        
        if not isSol:
            self.log(f'The maximum capacity found is less than the design ,\
                  shear, with VrReq = {round(Vr)} > VrOut = {round(VrOut)}')
            return VrOut, ShearResultEnum.designFailed
        else:
            return VrOut, ShearResultEnum.rebarPlaced



        
        
        
        
def designStirrupsForVr(Vr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str = '10M',
                        sectionInd: int = 0,
                        yForce: bool = True,
                        posForce: bool = True,
                        ds: float = 50,
                        dvEstimate: float = None,
                        matRebar: MaterialRebarCSA24 = None,
                        lUnit: str = 'mm',
                        logging = True) -> ShearResultEnum:
    pass
    
    # # initially estimate capacity with no stirrups.
    # designProps = element.designProps
    # designProps.shearReinforcementType = ShearConfigurations.NoTransverse
    
    # rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')    
    # dbar  = rebar.d
    
    
    # # Initial Vc calculation
    # if not element.rebar:
    #     printIfLogging(logging, f'No longditudinal bars found, attempting to use dv estimate.')
    #     dvEstimate = None
    # elif not dvEstimate:
    #     printIfLogging(logging, f'No manual dv estimate given, estimating dv.')
    #     h = element.section.concrete
    #     dvEstimate = designProps.cover + dbar + 25
    #     printIfLogging(logging, f'dv estimated as {dvEstimate}.')
    # return  ShearResultEnum.noRebarPlaced
        
    # Vc = getElementVrc(element, sectionInd, yForce, posForce, 
    #                    dvEstimate = dvEstimate) 
    # # getSectionSmax(section, barType,)
    
    # if Vr < Vc:
    #     return ShearResultEnum.noRebarPlaced


    
    # Vrmax = getElementVmax(element, sectionInd, yForce, posForce)
    # section = element.getSection(sectionInd)
    # if Vr > Vrmax:
    #     if logging:
    #         print(f'No stirrup design possible for {section},\
    #               Vr = {round(Vr)} > Vrmax = {round(Vrmax)}')
    #     return ShearResultEnum.noSolutionPossible

    
    # # set the stirrups to the 
    # designProps = element.designProps
    # designProps.shearReinforcementType = ShearConfigurations.MinTransverse
    # Vc = getElementVrc(element, sectionInd, yForce, posForce) 

    # dV = Vr - Vc
    # getElementVrs(ele)
    
    
        
        
        
    