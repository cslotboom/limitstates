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
    Determines the As required to meet a input force, given a moment, 
    a section, an estimate of the effective depth, and the sections width. 
    
    Moment is assumed to be in Nm, and all dimensions are in mm.

    Parameters
    ----------
    Mr : float
        The applied moment the beam is being designed for.
        The moment must have a positive value, direction of the moment is set
        by the flag "posDir"
    mat : MaterialConcreteCSA24
        The concrete material to use.
    rebar : Rebar
        The rebar to be used in the section.
    dEst : float
        The estimated rebar effective depth of the section in mm.
    b : float
        The width of the section in mm.

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

def _checkMr(section: ls.SectionConcrete, yDir: bool, posDir: bool):
    NA    = solveForNA(section, yDir, posDir)
    MrSol = getSectionMr(section, NA, yDir, posDir)
    return MrSol

def _getNbarReq(Mr: float, dEst: float, section: ls.SectionConcrete, 
                rebar: Rebar, b:float):

    As   = getRequiredSteelForMr(Mr, section.concrete.mat, rebar, dEst, b)
    Asmin = getSectionAsmin(section)
    As = max(As, Asmin)
    NbarReq = ceil(As/rebar.A)
    
    return NbarReq

def _isOverReinforced(rhoBA: float, rhoNet: float):
    isOverReinforced = False
    if rhoBA <= rhoNet:
        isOverReinforced = True
    return isOverReinforced 

def designBottomSteelForMr(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str = '20M',
                        sectionInd: int = 0,
                        yDir: bool = True,
                        posDir: bool = True,
                        matRebar: MaterialRebarCSA24 = None,
                        addTopSteel: bool = True, 
                        runDesignItertion: bool = True,
                        placementStrategy: int = 1, 
                        lUnit: str = 'mm'):


    """
    Places bottom steel in a section. The rebar will be placed such that
    the section has a moment capacity larger than the input moment, if it is 
    possible to find a solution.
    
    The minimum steel will be used for the section, if it is larger than the
    required steel.

    Parameters
    ----------
    Mr : float
        The applied moment the beam is being designed for.
        The moment must have a positive value, direction of the moment is set
        by the flag "posDir"
    element : BeamColumnConcreteCsa24
        The beamcolumn element to place rebar in.
    barType : str
        The type of rebar to be used. Must be a valid canadian rebar type,
        i.e. 10M, 15M, 20M, 25M, 30M, 35M, 40M, 45M.
    sectionInd : int, optional
        If there are multiple sections in the beamcolumn element, this variable
        can be set to modify which section to place rebar in. The default is 0,
        which places it in the first concrete section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.
    matRebar : MaterialRebarCSA24, optional
        The material to use for the rebar. The default is 400MPa steel.
    addTopSteel : bool, optional
        A flag that specifies if top steel should be included. 
        The default is True.
    runDesignItertion : bool, optional
        A flag that specifies if, once top steel is set, an additional design
        iteration should be run to see if the bottom steel can be reduced. 
        The default is True.
    placementStrategy : int, optional
        The enumeration for how bars are placed within the secton. 
        XXX CURRENTLY UNUSED XXX
        The default is 1.
    lUnit : str, optional
        The length unit to use for the rebar added. The default is in 'mm'.

    Returns
    -------
    isOverReinforced : bool
        A flag that specifies if the section is overreinforced or not..

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
    b = section.getWidth(yDir, lUnit)    
    d = section.getDepth(yDir, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yDir, posDir)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)
    
    Nrow  = len(section.rebar)
    bottomBarInds = list(range(Nrow))
    
    # Check if the beam is over-reinforced
    dEstBot = section.getdeff(yDir, posDir, d / 2, lUnit)
    rhoBA   = getSectionBalancedRho(section)
    rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

    # # Add top bars if the secton is over reinforced.
    isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
    if isOverReinforced:
        drho  = rhoNet - rhoBA
        _placeTopBarIfOverreinforced(element, sectionInd, yDir, posDir,  
                                     drho, barType, rebar, lUnit)   

    if runDesignItertion:
        _runDesignIteration(Mr, element, barType, NbarReq, bottomBarInds,
                            rebar,sectionInd, yDir, posDir, lUnit)
       
    return isOverReinforced

def _initalBottomBarPlacement(Mr, element, sectionInd, yDir, posDir,  
                                 barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    # Get the section, and reset the rebar in the section.
    section = element.getSection(sectionInd)
    section.rebar = None
    
    designProps = element.designProps

    # get the width and depth of the section.
    b = section.getWidth(yDir, lUnit)    
    d = section.getDepth(yDir, lUnit)
    
    # estimate where the rebar in the section is placed
    dEstBot = d*0.9    
    NbarReq = _getNbarReq(Mr, dEstBot, section, rebar, b)
    
    location = getRebarLocationEnum(yDir, posDir)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReq, barType, location)

def _placeTopBarIfOverreinforced(element, sectionInd, yDir, posDir,  
                                 drho, barType, rebar, lUnit):
    """
    Places top bars in the section.
    """
    designProps = element.designProps
    section = element.getSection(sectionInd)
    b = section.getWidth(yDir, lUnit)    
    d = section.getDepth(yDir, lUnit)
    
    AsTop = (b * d) * drho
    NbarReqTop = ceil(AsTop / rebar.A)
    if NbarReqTop < 2:
        NbarReqTop = 2

    
    location = getRebarLocationEnum(yDir, not posDir)
    placer = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
    placer.place(NbarReqTop, barType, location)

def _runDesignIteration(Mr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str,
                        NbarReq:int,
                        bottomBarInds,
                        rebar,
                        sectionInd: int = 0,
                        yDir: bool = True,
                        posDir: bool = True,
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
    b = section.getWidth(yDir, lUnit)    


    NA    = solveForNA(section, yDir = yDir, posDir = posDir)
    MrSol = getSectionMr(section, NA, yDir, posDir) / 1000
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
            
        location = getRebarLocationEnum(yDir, posDir)
        placer   = RebarPlacerRowCSA24(section, designProps, rebar.mat, lUnit)
        placer.place(NbarReq, barType, location)
        
        if not hasTopBars:
            # XXX: Consider recalculating NA Nocation
            dEstBot = section.getdeff(yDir, posDir, NA, lUnit)
            rhoBA   = getSectionBalancedRho(section)
            rhoNet  = section.rebar.getNetArea('mm') / (b * dEstBot)    

            # # Add top bars if the secton is over reinforced.
            isOverReinforced = _isOverReinforced(rhoBA, rhoNet)
            
            if isOverReinforced:
                drho  = rhoNet - rhoBA
                _placeTopBarIfOverreinforced(element, sectionInd, yDir, 
                                             posDir,  drho, barType, rebar, 
                                             lUnit)
            
                hasTopBars = True

        
        # Remove update the bottom bar inds for later removal.
        Ngroups = len(section.rebar)
        bottomBarInds = list(range(NgroupsTop, Ngroups))

        NA = solveForNA(section, yDir, posDir, NAtrial=NA)
        MrSol = getSectionMr(section, NA, yDir, posDir)  / 1000
        
        momentLow = MrSol < Mr
        if momentLow:
            atMin = True  

class ShearResultEnum(IntEnum):
    """
    An enumeration that represents possible results for the stirrup designer.
    1 represents a successful design, with stirrups placed. 2 represents a 
    successful design where no stirrups are needed. 3 represents a design case
    where it is not possible to design the section, i.e. no 
    4 represents a case where the design failed.
    """
    rebarPlaced = 1
    noRebarPlaced = 2
    noSolutionPossible = 3
    designFailed = 4
    
class StirrupDesigner:
    """
    The stirrup designer class is used to try and set stirrups within a 
    section, to resist the input load. 
    
    The rebar material used will be 400MPa rebar.
    
    Spacing rules according to A23.3 will be respected for bars.
    
    The value of dv for the section is either calculate using rebar, or
    estimated using the given cover and an assumed 25M lognditudinal bar.
    
    All units are assumed to be in mm.
    
    Parameters
    ----------
    Vr : float
        The required shear the section stirrups will attempt to be designed
        for.
    element : BeamColumnConcreteCsa24
        The design element to be used in design.
    barType : str
        The type of rebar to be used. Must be a valid canadian rebar type,
        i.e. 10M, 15M, 20M, 25M, 30M, 35M, 40M, 45M.
    sectionInd : int, optional
        If there are multiple sections in the beamcolumn element, this variable
        can be set to modify which section to place rebar in. The default is 0,
        which places it in the first concrete section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
    ds : float, optional
        The incriment for possible spacing values between stirrups along 
        the section, in mm. For example, if the input value is 75, spacing
        would only be allowed: 75, 150, etc. The default is 50.
    smin : float, optional
        The minimum value to be used for spacing between stirrups along 
        the beam, in mm.The default is 100.
    NlegMax : int, optional
        The maximum number of legs to be used in the section. 
        The default is 8.
    dvEstManual : float, optional
        An mannual override for dv in mm. This value will be taken 
        instead of any internal calculations / estimates on dv.
        The default is None, resulting in the calculated value of dv being
        used
    logging : float, optional
        A flag that specifies if outputs are to be logged. The default is False.
    logFunction : float, optional
        A function to be called used by the logger. The default is print.
    
    """
    
    def __init__(self, Vr: float, 
                        element: BeamColumnConcreteCsa24, 
                        barType: str = '10M',
                        sectionInd: int = 0,
                        yDir: bool = True,
                        posDir: bool = True,
                        ds: float = 50,
                        smin: float = 100,
                        NlegMax: int = 8,
                        dvEstManual: float = None,
                        logging = False,
                        logFunction = print):
        
        self.Vr = Vr 
        self.element = element
        self.sectionInd = sectionInd
        self.designSection = element.getSection(sectionInd)
        
        self.yDir = yDir
        self.posDir = posDir
        
        self.ds = ds
        self.smin = smin
        self.NlegMax  = NlegMax
        
        self.dvEst = dvEstManual

        
        self.barType = barType

        self.rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')

        self.logging = logging
        self.logFunction = logFunction
        

    def log(self, string):
        if self.logging:
            self.logFunction(string)
        
    def getdvEst(self):
        element = self.element
        section = self.designSection
        dbar = self.rebar.d
        
        
        if self.dvEst:
            dvEst = self.dvEst
            self.log('Using manual dv estimate.')
        elif section.rebar:
            dvEst = None
            self.log('Using dv calculated from rebar.')
        else:
            self.log("No longditudinal bars found, and no manual dv estimate"\
                     " given, estimating dv.")
            h = section.getDepth(self.yDir, 'mm')
            dvEst = h - (element.designProps.cover + dbar + 25)
            self.log(f'dv estimated as: {dvEst}')
        
        return dvEst

    def VcCalc(self, dvEst):
        return getElementVrc(self.element, self.sectionInd, self.yDir, 
                           self.posDir, dvEst = dvEst)


    def _roundSmin(self, sminTrial):
        return floor( sminTrial / self.ds) * self.ds


    def runTrial(self, VsReq, NlegTrial, sMaxGeom, dvEst):
        
        smin = self.smin       
        sminTrial = getElementSminForVrs(self.element, VsReq, self.sectionInd,
                                         self.barType, NlegTrial, dvEst,
                                         self.yDir, self.posDir)
        
        sMaxRebar = getElementSmaxStirrup(self.element, self.sectionInd, 
                                          self.barType, NlegTrial, 
                                          self.rebar.mat.fy, self.yDir)

        sMax = min(sMaxGeom, sMaxRebar)
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

    def _getStirrups(self, Nstirrups, s):
        stirrups = [None]*Nstirrups
        for ii in range(Nstirrups):
            stirrups[ii] = ls.Stirrup(self.rebar, ls.StirrupTypeEnum.Closed, 2, s, 'mm')
        return ls.StirrupGroup(stirrups)

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
                               self.yDir, self.posDir, dvEst)
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
                                        self.yDir, self.posDir, 
                                        dvEst, Vr, Vrmax)

        s, isSol, Nleg = self.runDesignIteration(VsReq, dvEst, SMaxgeom)
        
        # Set the solution and do some final clean up
        if isSol:
            Nstirrup = int(Nleg / 2)            
            
            self.designSection.stirrups = self._getStirrups(Nstirrup, s)

            VrOut = getElementVr(self.element, self.sectionInd, 
                                 self.yDir, self.posDir, dvEst)
        
            # If we are now greater than Vmax/2, the maximum spacing has changed.
            # TODO: add iteration if greater than new smax
            SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
                                          self.yDir, self.posDir, 
                                          dvEst, Vr, Vrmax)
            
        if SMaxgeom < s:
            s, isSol, Nleg = self.runDesignIteration(VsReq, dvEst, SMaxgeom)
            Nstirrup = int(Nleg / 2)

            self.designSection.stirrups = self._getStirrups(Nstirrup, s)

            VrOut = getElementVr(self.element, self.sectionInd, 
                                 self.yDir, self.posDir, dvEst)
        
            # If we are now greater than Vmax/2, the maximum spacing has changed.
            SMaxgeom = getElementSmaxGeom(self.element, self.sectionInd, 
                                          self.yDir, self.posDir, 
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
                        yDir: bool = True,
                        posDir: bool = True,
                        ds: float = 50,
                        dvEstManual: float = None,
                        matRebar: MaterialRebarCSA24 = None,
                        lUnit: str = 'mm',
                        logging = True) -> ShearResultEnum:
    """
    A function used to place stirrups within a section to resist the an input 
    load. Spacing rules according to A23.3 will be respected for bars.
    
    The value of dv for the section is either calculate using rebar, or
    estimated using the given cover and an assumed 25M lognditudinal bar.
    
    All units are assumed to be in mm. 
    The rebar material used will be 400MPa rebar.

    
    Parameters
    ----------
    Vr : float
        The required shear the section stirrups will attempt to be designed
        for.
    element : BeamColumnConcreteCsa24
        The design element to be used in design.
    barType : str
        The type of rebar to be used. Must be a valid canadian rebar type,
        i.e. 10M, 15M, 20M, 25M, 30M, 35M, 40M, 45M.
    sectionInd : int, optional
        If there are multiple sections in the beamcolumn element, this variable
        can be set to modify which section to place rebar in. The default is 0,
        which places it in the first concrete section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
    ds : float, optional
        The incriment for possible spacing values between stirrups along 
        the section, in mm. For example, if the input value is 75, spacing
        would only be allowed: 75, 150, etc. The default is 50.
    smin : float, optional
        The minimum value to be used for spacing between stirrups along 
        the beam, in mm.The default is 100.
    NlegMax : int, optional
        The maximum number of legs to be used in the section. 
        The default is 8.
    dvEstManual : float, optional
        An mannual override for dv in mm. This value will be taken 
        instead of any internal calculations / estimates on dv.
        The default is None, resulting in the calculated value of dv being
        used
    logging : float, optional
        A flag that specifies if outputs are to be logged. The default is False.
    logFunction : float, optional
        A function to be called used by the logger. The default is print.
    
    """
    designer = StirrupDesigner(Vr, element, barType, sectionInd,
                            yDir, posDir, ds, dvEstManual, matRebar,
                            lUnit, logging)
    
    return designer.design()
    
    
        
        
        
    