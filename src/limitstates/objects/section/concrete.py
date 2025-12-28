"""
Represents a concrete section.

"""

from abc import ABC, abstractmethod
from enum import IntEnum
from dataclasses import dataclass
import math


import numpy as np

from .section import SectionRectangle
from .rebar import (RebarFactory, RebarCollection, StirrupGroup, RebarLayer, 
                    Stirrup, StirrupPositionBox)


class SectionConcrete:
    """
    Represents a concrete section. The concrete is composed of longditudinal 
    rebar (top / bottom bars), and transverse rebar (stirrups)
    
    Special sections, such as T-beams cannot be repersented using this section.

    Parameters
    ----------
    concrete : SectionRectangle
        The concrete in the section, must be a rectangle.
    rebar : RebarCollection, optional
        The longditudinal rebar in the section. Rebar collections contain
        a number of groups, i.e. top bars and bottom bars.
        The default is None.
    stirrups : StirrupGroup, optional
        The a group of stirrups in the section. The default is None.

    Returns
    -------
    None.

    
    """
    concrete: SectionRectangle
    rebar: RebarCollection
    stirrups: StirrupGroup
    
    
    def __init__(self, concrete: SectionRectangle,
                        rebar: RebarCollection = None,
                        stirrups: StirrupGroup = None):   

        self.concrete = concrete
        self.rebar    = rebar
        self.stirrups = stirrups

    def addBars(self, rebar: RebarCollection):
        """
        Adds a new set of longditudinal bars to the current rebar collection.

        Parameters
        ----------
        rebar : RebarCollection
            The rebar colection to add to the group. Any bars from the original
            collection will be merged with the new collection.

        Returns
        -------
        None.

        """
        if not self.rebar:
            self.rebar = rebar
        else:
            self.rebar.addBars(rebar.groups)

    def getWidth(self, yDir: bool = True, lunit: str = 'mm') -> float:
        """
        Gets the width of the section in the orientation specified, i.e. y/x. 
        The default units are mm

        Parameters
        ----------
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
        lunit : str, optional
            The output units. The default is 'mm'.

        Returns
        -------
        b : float
            The width of the beam in the input set of units.

        """          
        
        lfactor = self.concrete.lConvert(lunit)
        if yDir:
            b = self.concrete.b * lfactor
        else:
            b = self.concrete.d * lfactor
        return b

    def getDepth(self, yDir: bool = True, 
                 lUnit: str = 'mm') -> float:
        """
        Gets the depth of the section in the orientation specified, i.e. y/x. 
        The default units are mm

        Parameters
        ----------
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
        lunit : str, optional
            The output units. The default is 'mm'.

        Returns
        -------
        b : float
            The width of the beam in the input set of units.

        """          
        
                
        lfactor = self.concrete.lConvert(lUnit)
        if yDir:
            d = self.concrete.d * lfactor
        else:
            d = self.concrete.b * lfactor
        return d
    
    def getRebarMaxDepth(self, yDir: bool = True, 
                        posDir: bool = True, 
                        lUnit: str = 'mm') -> float:
        """
        Returns the depth from the compression face to the furthest away rebar.

        Parameters
        ----------
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
        posDir : bool, optional
            A flag that specifies if force should be positive or negative. 
            Positive is defined as force or moment that creates tension at the 
            "bottom" of the beam. e.g. a simply supported beam has positive 
            bending, a downards shear force is positive.
            The default is True.
        lunit : str, optional
            The output units. The default is 'mm'.

        Returns
        -------
        dmax : float
            The maximum depth from the compression face to the furthest away
            rebar.

        """
        if yDir:
            coords = self.rebar.getyCoords(lUnit, flatten=True)
        else:
            coords = self.rebar.getxCoords(lUnit, flatten=True)
        if posDir:
            dbeam = self.getDepth(yDir, lUnit)
            drebar = min(coords)
            dv = dbeam - drebar
        else:
            dv = max(coords)
        return dv
    
    
    
    def _get_rebar_depths(self, yDir: bool = True, 
                          posDir: bool = True, 
                          lUnit: str = 'mm'):
            
        d = self.getDepth(yDir, lUnit)

        if yDir:
            depths = self.rebar.getyCoords(lUnit, True)
        else:
            depths = self.rebar.getxCoords(lUnit, True)
        
        if posDir:
            depths = d - depths
            
        return depths
    
    def getBottomBarStatus(self, NAlocation:float = None, 
                            yDir: bool = True, posDir: bool = True,
                            lUnit: str = 'mm') -> list[bool]:
        """
        For each bar in the section, return a flag that specifies if it is in
        compression or not, given a assumed NA location.
        
        Bottom bar status depends on wether the bar is in tension or 
        compression. Bars in tension will be considered bottom bars, while
        bars in compression are considered top bars.
        
        The NA location is specified, measured from the bottom of the section.
        
        If no NA location is specified, then the section will assume the 
        neutral axis is at the middle of the beam.

        Parameters
        ----------
        NAlocation : float, optional
            The location of the neutral axis, measured from the compression
            face of the. The default is None, which results in half the depth
            of the beam in the direction of interest.
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
        posDir : bool, optional
            A flag that specifies if force should be positive or negative. 
            Positive is defined as force or moment that creates tension at the 
            "bottom" of the beam. e.g. a simply supported beam has positive 
            bending, a downards shear force is positive.
            The default is True.
        lunit : str, optional
            The output units. The default is 'mm'.

        Returns
        -------
        status: list[boolean]
            A list of boolean variables for the output status of each bar.

        """
        
        d = self.getDepth(yDir, lUnit)
        depths = self._get_rebar_depths(yDir, posDir, lUnit)
        
        if not NAlocation:
            NAlocation = d / 2
    
        return depths > NAlocation
    
    
    def getdeff(self, yDir: bool = True, posDir: bool = True,
                NAlocation:float = None, lUnit: str = 'mm') -> float:
        """
        Gets the effective depth in the input direction of interest. The 
        effective depth is the depth to the centroid of the tension bar group.
        If only one layer of bars is used, then the effective depth will be
        equal to the maximum depth.
        
        The NA location in the direction of interst is used to exclued bars 
        from the depth calucation. 
        

        Parameters
        ----------
        
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
        NAlocation : float, optional
            A manual overwrite, which can be used to specify the neutral axis
            location. This is used to determine which bars should be used
            when calculating deff. By default, the centerline of the beam is
            used.  This will exclude top bars, but may include skin reinforcing 
            if there is any.
        lUnit : str, optional
            The output units. The default is 'mm'.

        Returns
        -------
        deff : float
            The effective depth, i.e. the depth to the centroid of the bottom
            bars.

        """
        
        # Notes, this function seems like it should happen in rebar, however,
        # the rebar will not know the section depth, which is needed
        
        d = self.getDepth(yDir, lUnit)
        depths = self._get_rebar_depths(yDir, posDir, lUnit)
        areas  = np.array(self.rebar.getAreas(lUnit, True))
        if not NAlocation:
            NAlocation = d / 2
    
        bottomBars = depths > NAlocation
        
        depths = depths[bottomBars]
        areas  = areas[bottomBars]
        
        return sum(depths * areas) / sum(areas)

    def setStirrups(self, stirrups: StirrupGroup):
        """
        Adds stirrups to the section. Existing stirrups will be replaced

        Parameters
        ----------
        stirrups : StirrupGroup
            The stirrup group to be added.

        """
        self.stirrups = stirrups
        
# =============================================================================
# 
# =============================================================================

class SectionNASolver:
    """
    Attempts to solves for the neutral axis of a section. Assumes all 
    bars use the same material.
    
    Solves for the neutral axis within a section.
    The neutral axis is measured from the top of the section.

    Parameters
    ----------
    section : SectionConcrete
        The concrete section to solve the NA of.
    concreteFunction : function
        A function that returns the compressive force in the concrete, 
        given the section and neutral axis location.
    steelFunction : function
        A function that returns the tensile force in the steel, 
        
    Pf : float, optional
        A axial force applied to the section. The default is 0.
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
    tol : float, optional
        The tolerance required for convergence, i.e. the difference between
        the calcualted concrete and steel force. The default is 1e-3.
    maxIter : float, optional
        The maximum number of iterations needed before convergence is 
        reached. The default is 100.
    logging : bool, optional
        A flag that turns on or off logging. Currently is inactive. 
        The default is True.

    Returns
    -------
    None.

    """
    def __init__(self, section: SectionConcrete, 
                 concreteFunction, steelFunction,
                 Pf:float = 0, yDir: bool = True, 
                 posDir: bool = True,
                 NAtrial = None,
                 tol: float = 1e-3, maxIter: int = 100,
                 logging:bool = True):

        
        self.section = section
        self.rebar = section.rebar
        
        self.compressiveFunction = concreteFunction
        self.steelFunction = steelFunction
        
        self.yDir = yDir
        self.posDir = posDir
        
        if yDir:
            self.rebarCoords = self.rebar.getyCoords(flatten=True)
            self.d = section.concrete.d
            self.b = section.concrete.b
        else:
            self.rebarCoords = self.rebar.getxCoords(flatten=True)
            self.d = section.concrete.b
            self.b = section.concrete.d

        # If the moment isn't positive, flip the orientation of the rebar
        if not posDir:
            self.rebarCoords = self.d - self.rebarCoords
        
        if not NAtrial:
            self.NAtrial = self.d / 2
        else:
            self.NAtrial = NAtrial

        
        self.tol = tol
        self.maxIter = maxIter
        self.logging = logging

    def getCr(self, NAtrial):
        return self.compressiveFunction(self.section, NAtrial, 
                                        self.yDir, self.posDir)
    
    def getFsteel(self, NAtrial):
        return self.steelFunction(self.section, NAtrial, 
                                        self.yDir, self.posDir)

        
    def checkEqulibrium(self, NAtrial: float) -> float:
        """
        The ratio between tension and compression force for a given input 
        NAtrial value.

        Parameters
        ----------
        NAtrial : TYPE
            The trial value for the neutral axis.

        Returns
        -------
        ratio : float
            The ratio between the net tension force, and the 
            net compression force.

        """
        Cr     = self.getCr(NAtrial)
        Fsteel = self.getFsteel(NAtrial)        
        Fnet = np.sum(Fsteel)

        ratio = abs(Fnet/Cr)

        return ratio
    
    def calcNA(self, root:float = 0.4) -> float:
        """
        Calculates a trial value for the NA, given a particular "root".
        The root affects the solver and how quickly it converges.

        Parameters
        ----------
        root : float
            The root to use in the solver.

        Returns
        -------
        NAtrial : float
            The ratio between the net tension force, and the 
            net compression force.

        """
        NAtrial, Niters = self._run_analysis(root)

        if Niters == self.maxIter:
            if self.logging:
                print(f'Analysis with root {root*2} failed to converge, attempting root {root}')
            root = root / 2
            NAtrial, Niters = self._run_analysis(root)

        if Niters == self.maxIter:
            raise Exception('Convergence not reached. Try a smaller root in the solver.')
        
        self.Niters = Niters
        self.section.NA = NAtrial
        
        return NAtrial    

    
    def _run_analysis(self, root):

        NAtrial = self.NAtrial
        
        
        self.trials = []
        self.residual = []
        r = self.checkEqulibrium(NAtrial)
        self.trials.append(NAtrial)
        self.residual.append(r)        
        nn = 0
        while self.tol < abs(r - 1) and nn < self.maxIter:
            r = self.checkEqulibrium(NAtrial)
            NAtrial = NAtrial*r**root
            self.trials.append(NAtrial)
            self.residual.append(r)
            nn += 1
        return NAtrial, nn

def solveForNA(section: SectionConcrete, 
             Pf:float = 0, yDir: bool = True, 
             posDir: bool = True,
             NAtrial: float = None,
             tol: float = 1e-3, maxIter: float = 100):
    
    
    naSolver = SectionNASolver(section, Pf, yDir, posDir, NAtrial,
                               tol, maxIter)

    return naSolver.calcNA()

# =============================================================================
# 
# =============================================================================

class RebarPlacementStrategyEnum(IntEnum):
    """
    A enumeration that represents possible placement strategies for. 
    rebar placers. Face places the rebar along a single face in a row.
    FaceWithRadius places rebar along a single face, but takes into acount the 
    bend of the accompanying stirrups.
    Perimeter distributes rebar along the edge of the section evenly.
    """
    Face = 1
    FaceWithRadius = 2
    Perimeter = 3

class RebarLocationEnum(IntEnum):
    """
    A enumeration that represents where the bars can be placed in square or
    rectangular section.
    """
    Bottom = 1
    Top = 2
    Left = 3
    Right = 4
    

placementDict = {(True,  True):  RebarLocationEnum.Bottom, 
                 (True,  False): RebarLocationEnum.Top, 
                 (False, True):  RebarLocationEnum.Left, 
                 (False, False): RebarLocationEnum.Right }

def getRebarLocationEnum(yDir:bool = True, 
                         posDir:bool = True) -> RebarLocationEnum:
    """
    Returns the appropriate placement enumeration for a direction and pos/neg 
    direction combination.

    Parameters
    ----------
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.

    Returns
    -------
    RebarLocationEnum
        The location enumeration for the given input parameters.

    """
    return placementDict[(yDir, posDir)]

# =============================================================================
# 
# =============================================================================

@dataclass
class   RebarSpacingConfig:
    """
    A configuraton class that specifies the information needed to place rebar
    within a section.
        
    Parameters
    ----------
    clearSpacing : float
        The clear distance between longditudinal rebar
    cover : float
        The the clear cover to either the bars or stirrups.
    dstir : float, optional
        The stirrup diameter.
    stirrupCurveRadius : float, optional
        The curve radius of the stirrups.
    lUnit : string, optional
        The length units.

    
    """
    clearSpacing: float
    cover: float
    dstir: float
    stirrupCurveRadius: float = 0
    lUnit:str = None

class RebarPlacerAbstract(ABC):
    """
    The an abstract class to use for the rebarplacer, contains some useful 
    interfaces
    
    Parameters
    ----------
    section : SectionConcrete
        The section to place rebar in.
    rebarFactory : RebarFactory
        The factory object which will be used to produce rebar.
    spacingConfig : RebarSpacingConfig, optional
        A spacing configuration object. Rules specified by the spacing 
        configuration will be used to change rebar spacing. 
        The default is None.

    """    
    
    def __init__(self, section: SectionConcrete,
                 rebarFactory:  RebarFactory,
                 spacingConfig: RebarSpacingConfig = None):

        self.section      = section 
        self.factory = rebarFactory
        
        if spacingConfig:
            self.setSpacingConfig(spacingConfig)

    @abstractmethod
    def place(self, Nbars:int, barType:str):
        pass
    
    def setSpacingConfig(self, spacingConfig: RebarSpacingConfig):
        self.c = spacingConfig.cover
        self.s = spacingConfig.clearSpacing
        self.dstir = spacingConfig.dstir
        self.rcurve = spacingConfig.stirrupCurveRadius


class RebarPlacerManual():
    """
    A rebar placer, where the user manually specifies the position of
    the bars from the top / side of the section. Rebar spacing rules according
    to building codes are not enforced.
    enforced.
    
    Parameters
    ----------
    factory : RebarFactory
        The initialized rebar factory used to produce bars.

    Returns
    -------
    RebarLayer
        The layer of rebar created at the input "position".

    """     
    def __init__(self, factory:RebarFactory):        
        self.factory = factory
        
    def getRebarLayer(self, Nbars: int, barType: str, 
                     position: float, width: float, offset:float = 0, 
                     yDir: bool = True) -> RebarLayer:
        """
        Evenly distributes Nbars of the given type within a row "width" wide, 
        and at "position" within the section. Bars will be linearly distributed 
        from centerline to centerline across this width.
        
        "position" is 

        Parameters
        ----------
        Nbars : int
            The number of bars to place in the section.
        barType : str
            The bar type to place in the section. Must 
        position : float
            The depth to place the rebar in, measured from the bottom of the 
            section for the rebar placed in the y axis, or from the left wall 
            for rebar placed in the x axis.
        width : float
            The width to place bars across. 
        offset : float, optional
            The offset from the edge of the beam for the first bar. 
            The default is 0.
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
            If true position is to measured from the top (i.e. from strong 
            axis bending), if false from the left. 
            The default is True, resulting in strong axis bending.

        Returns
        -------
        RebarLayer
            The layer of rebar created at the input "position".

        """

        if yDir:
            positions = self._getBarPositon(Nbars, width, offset)
            xyOut = [(x, position) for x in positions]
        else:
            positions = self._getBarPositon(Nbars, width)
            xyOut = [(position, y) for y in positions]
        
        bars = []
        for ii in range(Nbars):
            bars.append(self.factory.getRebar(barType, xyOut[ii]))
            
        return  RebarLayer(bars)
            
    def _getBarPositon(self, Nbars:int, width:float, offset:float):
        
        if Nbars == 1:
            return [(width - offset)/2]
        else:
            return list(np.linspace(offset, width + offset, Nbars))
        

# TODO: document
class RebarPlacerRow(RebarPlacerAbstract):
    """
    A generic rebar placer. It takes in a factor object used to produce rebar,
    and a placement configuration that has the spacing rules used to place
    rebar.
    

    Rebar is placed in the section using rules defined in the placementConfig
    If the row fills up, the rebar will be shifted to the next row.

    Parameters
    ----------
    section : SectionConcrete
        The concrete secton to place rebar in.
    rebarFactory : RebarFactory
        The the rebar factory to use - all rebar will be created using this
        object.
    placementConfig : RebarSpacingConfig
        The placement config class, which contains spacing rules.
    
    Returns
    -------
    None.

    """
    

    def __init__(self, section: SectionConcrete, 
                 rebarFactory: RebarFactory,
                 placementConfig: RebarSpacingConfig = None):
        super().__init__(section, rebarFactory, placementConfig)
    
    def _setDimensions(self, location):
        if location == 1 or location == 2:
            self.h = self.section.concrete.d
            self.b = self.section.concrete.b
            
        else:
            self.h = self.section.concrete.b
            self.b = self.section.concrete.d   

    def _setClearCover(self, dstir):
        # manually overwrite clear cover
        if not dstir:
            dstir = self.dstir

        self.clearCover = self.c + dstir
        self.bRow = self.b - self.clearCover * 2 
        
        if self.rcurve:
            self.bRow = self.bRow - (self.rcurve - self.dbar/2)* 2
       
    def getMaxBarsInRow(self):
        
        Nbars = (self.bRow - self.dbar) / (self.dbar + self.s)
        
        return math.ceil(Nbars)
     
    def _getBarPositon(self, Nbars:int, width:float, cover):
        if Nbars == 1:
            return [width/2 + cover]
        else:
            return list(np.linspace(0,1, Nbars)*width + cover)


    def _initPlacement(self, barType:str, location:RebarLocationEnum, 
                       dstir = None):
        
        try:
            self.dbar = self.factory.dbDict[barType]['d']
        except:
            raise Exception('The input bar type could not be found in the database.')
        
        self._setDimensions(location)
        self._setClearCover(dstir)
        self.NbarsMax = self.getMaxBarsInRow()
   
    def _place(self, Nbars:int, barType:str, location: RebarLocationEnum,
                     depthOverwrite: float = None, dstirOverwrite = None):
        if Nbars < 2:
            raise Exception('Two or more bars must be placed in the section.')        
        
        self._initPlacement(barType, location, dstirOverwrite)
        
        NrowRequired  = math.ceil(Nbars / self.NbarsMax)
        barsRemaining = Nbars 
        
        layers = []        
        dbar = self.dbar
        for ii in range(NrowRequired):
            if barsRemaining > self.NbarsMax:
                NBarRow = self.NbarsMax
            else:
                NBarRow = barsRemaining                
            
            dRow = (dbar + self.s)*ii
            
            if depthOverwrite:
                dbase = depthOverwrite
            else:
                dbase = self.clearCover + dbar/2

            if location==1 or location==3:
                deff = (dbase + dRow)
            else:
                deff = self.h - (dbase + dRow)
            
            cover = self.clearCover + dbar/2 
            if self.rcurve:
                cover = cover + self.rcurve - self.dbar/2 
            
            positions = self._getBarPositon(NBarRow, 
                                            self.bRow - dbar, 
                                            cover)
            
            if location==1 or location==2:
                xyOut = [(x, deff) for x in positions]            
            else:
                xyOut = [(deff, y) for y in positions]
                
            bars = [self.factory.getRebar(barType, xy) for xy in xyOut]            
            layers.append(RebarLayer(bars))
            barsRemaining -= self.NbarsMax
    
        return RebarCollection(layers)
    
    def place(self, Nbars:int, barType:str, location:RebarLocationEnum = 1,
              depthOverwrite = None, dstirOverwrite = None):      
        """
        Place Nbars of the type "barType" within the rebar section. The location
        enumeration is used to specify where the section the bars are placed,
        i.e. at the bottom, top, left or right. By default the bars are placed
        in the bottom layer.
        
        dstirrup is an overwrite

        Parameters
        ----------
        Nbars : int
            The number of bars to place.
        barType : str
            The type of bar to place.
        location : RebarLocationEnum
            The location bars are placed. 1 for bottom, 2 for top, 3 for left,
            and 4 for right.

        """          
        self.section.addBars(self._place(Nbars, barType, location, 
                                         depthOverwrite, dstirOverwrite))
 
    
 
    
def RebarPlacerFactory(placementStrategy: RebarPlacementStrategyEnum) -> RebarPlacerAbstract:
    # pass
    if placementStrategy == RebarPlacementStrategyEnum.BeamBottomBars:
        return RebarPlacerRow
    

# =============================================================================
# 
# =============================================================================



class StirrupPlacementStrategyEnum(IntEnum):
    Nested = 1
    ColumnTypical = 2
    

     
def _getBarPositon(self, Nbars:int, width:float, cover):
    if Nbars == 1:
        return [width/2 + cover]
    else:
        return list(np.linspace(0,1, Nbars)*width + cover)

class StirrupPlacer(ABC):
    
    def __init__(self, section, spacingConfig: RebarSpacingConfig = None):
        self.section = section         
        if spacingConfig:
            self.setSpacingConfig(spacingConfig)

    @abstractmethod
    def place(self, Nbars:int, barType:str):
        pass
    
    def setSpacingConfig(self, spacingConfig: RebarSpacingConfig):
        self.c = spacingConfig.cover
        self.s = spacingConfig.clearSpacing
        self.dstir = spacingConfig.dstir
        self.rcurve = spacingConfig.stirrupCurveRadius


# TODO: rename into box?
class StirrupPlacerRow(RebarPlacerAbstract):
    """
    Places stirrups in rows in the given section. 

    Parameters
    ----------
    section : SectionConcrete
        The concrete secton to place rebar in.
    rebarFactory : RebarFactory
        The the rebar factory to use - all rebar will be created using this
        object.
    placementConfig : RebarSpacingConfig
        The placement config class, which contains spacing rules.

    Returns
    -------
    None.

    """  
    def __init__(self, section: SectionConcrete, 
                         rebarFactory: RebarFactory = None,
                        placementConfig: RebarSpacingConfig = None):
        super().__init__(section, rebarFactory, placementConfig)
    
    def _setDimensions(self, yDir):
        if yDir:
            self.h = self.section.concrete.d
            self.b = self.section.concrete.b
        else:
            self.h = self.section.concrete.b
            self.b = self.section.concrete.d   

    def _setCenterLineCover(self):
        # self.clCover = self.c
        self.clCover = self.c + self.dstir / 2
        self.bRow = self.b - self.clCover*2
        self.hRow = self.h - self.clCover*2
    
 
    def _initPlacement(self, yDir:bool):        
        self._setDimensions(yDir)
        self._setCenterLineCover()
   
    def _getStirrupPositions(self, Nstirrup, yDir, dshift = None):
        """
        The stirrup position is to the C.L. of a rectangle

        """
        
        if not dshift:
            dshift = 0
        
        # !!! Assumes that all stirrup have two legs.
        Nrows = (2*Nstirrup - 1)
        positions = []
        # We start at the smallest and increase in size.
        for ii in range(Nstirrup):
            
            if yDir:
                dB = self.bRow / Nrows
                hStirrup = self.hRow
                # Expand all interior except for the outside
                bStirrup = dB * (2*ii + 1) + bool(Nstirrup - ii - 1) * dshift
                xy0 = (self.clCover + (Nstirrup - ii - 1) * dB, self.clCover)
                
            else:
                dh = self.hRow / Nrows
                hStirrup = dh * (2*ii + 1) + bool(Nstirrup - ii - 1)*dshift
                bStirrup = self.bRow
                xy0 = (self.clCover, self.clCover + (Nstirrup - ii - 1) * dh)
            positions.append(StirrupPositionBox(hStirrup, bStirrup, xy0))
                
        return positions
    
    def _set(self, yDir: bool, dshift) -> list[StirrupPositionBox]:
        section = self.section
        
        if not dshift:
            dshift = 0
        
        Nstirrup = len(section.stirrups)
                    
        return self._getStirrupPositions(Nstirrup, yDir, dshift)
       
    def setPosition(self, yDir: bool = True, dshift = None):      
        """
        Sets the position of stirrups.
        
        Parameters
        ----------
        Nbars : int
            The number of bars to place.
        barType : str
            The type of bar to place.
        location : RebarLocationEnum
            The location bars are placed. 1 for bottom, 2 for top, 3 for left,
            and 4 for right.

        """
        self._initPlacement(yDir)
        positions = self._set(yDir, dshift)

        for pos, stirrup in zip(positions, self.section.stirrups):
            stirrup.setPosition(pos)
            
            
        
    def _place(self, NStirrups: int, barType: str, 
               yDir: bool, spacing:float, Nleg: int,
               dshift: float) -> StirrupGroup:   
    
        self._initPlacement(yDir)
        positions = self._getStirrupPositions(NStirrups, yDir, dshift)

        stirrups = []
        for ii in range(NStirrups):
            rebar = self.factory.getRebar(barType)
            stirrup = Stirrup(rebar, Nleg = Nleg, spacing = spacing, 
                              position = positions[ii])
            stirrups.append(stirrup)

    
        return stirrups
       
    def place(self, NStirrups:int, barType:str, yDir: bool = True,
              Nleg = 2, spacing = 200, dshift = None):      
        """
        Place NStirrups of the type "barType" within the rebar section. 
        The direction
        enumeration is used to specify where the section the bars are placed,
        i.e. at the bottom, top, left or right. By default the bars are placed
        in the bottom layer.
        
        dshift must be manually set for the stirrups - it won't figure out the
        bar placement.

        Parameters
        ----------
        Nbars : int
            The number of bars to place.
        barType : str
            The type of bar to place.
        yDir : bool, optional
            A flag that specifies if the direction of interest is in the 
            sections vertical (y) direction. The default value is true, leading
            to vertical outputs, i.e. y axis outputs.
        Nleg : int, optional
            The number of legs each stirrup has. Currently only two legs are 
            supported per stirrup.
        spacing : float, optional
            The spacing between stirrups longditudinally in the section.
        dshift: float, optional
            A variable that can be used to manually shift where the stirrup
            legs are within the section. The shift will be towards the outside 
            edges of the section. This variable affects only interior bars.
        """
        
        if not self.factory:
            raise Exception('A rebar Factor has to be set to place rebar.')
        
        stirrups= self._place(NStirrups, barType, yDir, Nleg, spacing, dshift)
        self.section.setStirrups(stirrups)
     
    
