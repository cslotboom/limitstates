"""
Represents a concrete section.

"""

from abc import ABC, abstractmethod
from enum import IntEnum
from dataclasses import dataclass
import math


import numpy as np

from .section import SectionRectangle
from .rebar import RebarFactory, RebarCollection, StirrupGroup, Rebar, RebarLayer


class SectionConcrete:
    """
    Represents a concrete section. The concrete is composed of longditudinal 
    rebar (top / bottom bars), and transverse rebar ()
    
    Special sections, such as T-beams cannot be repersented using this section.
    
    
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

    # TODO: DOCUMENT
    def addBars(self, rebar:RebarCollection):
        if not self.rebar:
            self.rebar = rebar
        else:
            self.rebar.addBars(rebar.groups)

    def getdMax(self, xDirection:bool=False, 
                posForce:bool=True):
        pass
        if xDirection:
            positions = self.rebar.getxCoords()
        else:
            positions = self.rebar.getyCoords()
        return positions

    def getWidth(self, 
                 yDirection: bool = True, 
                 lunit: str = 'mm'):
        """
        The default units are mm

        Parameters
        ----------
        yForce : bool, optional
            DESCRIPTION. The default is True.
        posForce : bool, optional
            A flag that specifies if moment is positive or negative. Positive
            moment is defined as moment that creates tension at the "bottom"
            of the beam. e.g. a simply supported beam has positive bending.
            
            If set to true, then the NA will be measured from the "bottom" of the
            section, which will be assumed to be in compression.
            
            The default is True.
        lunit : str, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        b : TYPE
            The width of the beam in the input set of units.

        """          
        
        lfactor = self.concrete.lConvert(lunit)
        if yDirection:
            b = self.concrete.b * lfactor
        else:
            b = self.concrete.d * lfactor
        return b

    # TODO, rename to get section depth?
    def getDepth(self, yDirection: bool = True, 
                 lUnit: str = 'mm'):
                
        lfactor = self.concrete.lConvert(lUnit)
        if yDirection:
            d = self.concrete.d * lfactor
        else:
            d = self.concrete.b * lfactor
        return d
    
    def getRebarDepth(self, yForce: bool = True, 
                    posForce: bool = True, 
                    lUnit: str = 'mm'):
        if yForce:
            coords = self.rebar.getyCoords(lUnit, flatten=True)
        else:
            coords = self.rebar.getxCoords(lUnit, flatten=True)
        if posForce:
            dbeam = self.getDepth(posForce, lUnit)
            drebar = min(coords)
            dv = dbeam - drebar
        else:
            dv = max(coords)
        return dv
    
    
    
    def _get_rebar_depths(self, yForce: bool = True, 
                          posForce: bool = True, 
                          lUnit: str = 'mm'):
            
        d = self.getDepth(yForce, lUnit)

        if yForce:
            depths = self.rebar.getyCoords(lUnit, True)
        else:
            depths = self.rebar.getxCoords(lUnit, True)
        
        if posForce:
            depths = d - depths
            
        return depths
    
    def getBottomBarStatus(self, NAlocation:float = None, 
                            yForce: bool = True, posForce: bool = True,
                            lUnit: str = 'mm') -> float:
        """
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
        yForce : bool, optional
            DESCRIPTION. The default is True.
        posForce : bool, optional
            DESCRIPTION. The default is True.
        lUnit : str, optional
            DESCRIPTION. The default is 'mm'.

        Returns
        -------
        None.

        """
        
        d = self.getDepth(yForce, lUnit)
        depths = self._get_rebar_depths(yForce, posForce, lUnit)
        
        if not NAlocation:
            NAlocation = d / 2
    
        return depths > NAlocation
    
    

    # # TODO: test
    def getdeff(self, NAlocation:float = None, 
                yForce: bool = True, posForce: bool = True,
                lUnit: str = 'mm'):
        """
        Gets the effective depth in the input direction of interest.
        
        The NA location in the direction of interst is used to exclued bars 
        from the depth calucation. The effective depth be to the centroid of 
        the tension bar group.
        

        Parameters
        ----------
        yForce : bool, optional
            A flag that specifies if moment is applied in the y or x direction. 
            The default is True, for moment being applied about the x axis.
        posForce : bool, optional
            A flag that specifies if moment is positive or negative. Positive
            moment is defined as moment that creates tension at the "bottom"
            of the beam. e.g. a simply supported beam has positive bending.
            
            If set to true, then the NA will be measured from the "bottom" of the
            section, which will be assumed to be in compression.
            
            The default is True.
        lUnit : str, optional
            DESCRIPTION. The default is 'mm'.

        Returns
        -------
        deff : TYPE
            DESCRIPTION.

        """
        
        # Notes, this function seems like it should happen in rebar, however,
        # the rebar will not know the section depth, which is needed
        
        d = self.getDepth(yForce, lUnit)
        depths = self._get_rebar_depths(yForce, posForce, lUnit)
        areas  = np.array(self.rebar.getAreas(lUnit, True))
        
        if not NAlocation:
            NAlocation = d / 2
    
        bottomBars = depths > NAlocation
        
        depths = depths[bottomBars]
        areas  = areas[bottomBars]
        
        return sum(depths * areas) / sum(areas)





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
    yForce : bool, optional
        A flag that specifies if moment is applied in the y or x direction. 
        The default is True, for moment being applied about the x axis.
    posForce : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
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
                 Pf:float = 0, yForce: bool = True, 
                 posForce: bool = True,
                 NAtrial = None,
                 tol: float = 1e-3, maxIter: int = 100,
                 logging:bool = True):

        
        self.section = section
        self.rebar = section.rebar
        
        self.compressiveFunction = concreteFunction
        self.steelFunction = steelFunction
        
        self.yForce = yForce
        self.posForce = posForce
        
        if yForce:
            self.rebarCoords = self.rebar.getyCoords(flatten=True)
            self.d = section.concrete.d
            self.b = section.concrete.b
        else:
            self.rebarCoords = self.rebar.getxCoords(flatten=True)
            self.d = section.concrete.b
            self.b = section.concrete.d

        # If the moment isn't positive, flip the orientation of the rebar
        if not posForce:
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
                                        self.yForce, self.posForce)
    
    def getFsteel(self, NAtrial):
        return self.steelFunction(self.section, NAtrial, 
                                        self.yForce, self.posForce)

        
    def checkEqulibrium(self, NAtrial):
        """
        Checks the equlibrium at the current state.

        """
        Cr     = self.getCr(NAtrial)
        Fsteel = self.getFsteel(NAtrial)        
        Fnet = np.sum(Fsteel)
        # ratio = float(Fnet/Cr)
        ratio = abs(Fnet/Cr)

        return ratio
    
    def calcNA(self, root = 0.4):


        NAtrial, Niters = self._run_analysis(root)

        if Niters == self.maxIter:
            if self.logging:
                print(f'Analysis with root {root*2} failed to converge, attempting root {root}')
            root = root / 2
            NAtrial, Niters = self._run_analysis(root)

        # diff = np.diff(self.trials)
        # if 0.0001 < abs(diff[-1]):
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
             Pf:float = 0, yForce: bool = True, 
             posForce: bool = True,
             NAtrial: float = None,
             tol: float = 1e-3, maxIter: float = 100):
    
    
    naSolver = SectionNASolver(section, Pf, yForce, posForce, NAtrial,
                               tol, maxIter)

    return naSolver.calcNA()

class RebarPlacementStrategyEnum(IntEnum):
    Face = 1
    Perimeter = 2
    FaceWithRadius = 3

class RebarLocationEnum(IntEnum):
    Bottom = 1
    Top = 2
    Left = 3
    Right = 4
    
    
placementDict = {(True,  True):  RebarLocationEnum.Bottom, 
                 (True,  False): RebarLocationEnum.Top, 
                 (False, True):  RebarLocationEnum.Left, 
                 (False, False): RebarLocationEnum.Right }

def getRebarLocationEnum(yForce:bool = True, 
                         posForce:bool = True) -> RebarLocationEnum:
    """
    

    Parameters
    ----------
    yForce : bool, optional
        DESCRIPTION. The default is True.
    posForce : bool, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    RebarLocationEnum
        DESCRIPTION.

    """
    return placementDict[(yForce, posForce)]



@dataclass
class   RebarSpacingConfig:
    clearSpacing: float
    cover: float
    dstirrup: float
    stirrupCurveRadius: float = 0

# TODO, restructure
class RebarPlacer(ABC):
    
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
        self.dstir = spacingConfig.dstirrup
        self.rcurve = spacingConfig.stirrupCurveRadius


class RebarPlacerManual():
    def __init__(self, factory:RebarFactory):
        self.factory = factory
        
    def getRebarLayer(self, Nbar: int, barType: str, 
                     position: float, width: float, offset:float = 0, 
                     yDirection: bool = True) -> RebarLayer:
        """
        Evenly distributes Nbar of the given type within a row width wide, 
        and centered around "position".
        
        "position" is measured from the bottom of the section for the rebar 
        placed in the y axis, or from the left wall for rebar placed in the 
        x axis.

        Parameters
        ----------
        Nbar : int
            DESCRIPTION.
        barType : str
            DESCRIPTION.
        position : float
            DESCRIPTION.
        width : float
            DESCRIPTION.
        offset : float, optional
            DESCRIPTION. The default is 0.
        yDirection : bool, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        RebarLayer
            DESCRIPTION.

        """

        if yDirection:
            positions = self._getBarPositon(Nbar, width, offset)
            xyOut = [(x, position) for x in positions]
        else:
            positions = self._getBarPositon(Nbar, width)
            xyOut = [(position, y) for y in positions]
        
        bars = []
        for ii in range(Nbar):
            bars.append(self.factory.getRebar(barType, xyOut[ii]))
            
        return  RebarLayer(bars)
            
    def _getBarPositon(self, Nbar:int, width:float, offset:float):
        
        if Nbar == 1:
            return [(width - offset)/2]
        else:
            return list(np.linspace(offset, width + offset, Nbar))
        
    # def place(self, Nbar:int, barType:str, deff:float, width:float, 
    #           offset:float = 0, direction:str='x'):
        
        
    #     self.section.addBars(self.getRebarLayer(Nbar, barType, 
    #                                             deff, width, 
    #                                             offset, direction))

# TODO: document
class RebarPlacerRow(RebarPlacer):
    
    def __init__(self, section: SectionConcrete, 
                 rebarFactory,
                 placementConfig:RebarSpacingConfig = None):
        super().__init__(section, rebarFactory, placementConfig)
    
    def _setDimensions(self, location):
        if location == 1 or location == 2:
            self.h = self.section.concrete.d
            self.b = self.section.concrete.b
            
        else:
            self.h = self.section.concrete.b
            self.b = self.section.concrete.d   

    def _setClearCover(self):
        self.clearCover = self.c + self.dstir
        self.bRow = self.b - self.clearCover*2
   
       
    def getMaxBarsInRow(self):
        
        Nbar = (self.bRow - self.dbar - 2*self.rcurve)/(self.dbar + self.s)
        
        return math.ceil(Nbar)
     
    def _getBarPositon(self, Nbar:int, width:float, cover):
        if Nbar == 1:
            return [width/2 + cover]
        else:
            return list(np.linspace(0,1, Nbar)*width + cover)


    def _initPlacement(self, barType:str, location:RebarLocationEnum):
        
        try:
            self.dbar = self.factory.dbDict[barType]['d']
        except:
            raise Exception('The input bar type could not be found in the database.')
        
        self._setDimensions(location)
        self._setClearCover()
        self.NbarsMax = self.getMaxBarsInRow()
   
    def _place(self, Nbars:int, barType:str, location: RebarLocationEnum,
              depthOverwrite:float = None):
        if Nbars < 2:
            raise Exception('Two or more bars must be placed in the section.')        
        
        self._initPlacement(barType, location)
        
        NrowRequired  = math.ceil(Nbars / self.NbarsMax)
        barsRemaining = Nbars 
        
        layers = []
        # bars   = RebarLayer()
        
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
            # else:
            if location==1 or location==3:
                deff = (dbase + dRow)
            else:
                deff = self.h - (dbase + dRow)
                
            
            # if depthOverwrite:
            #     deff = depthOverwrite + dRow
            # # else:
            # elif location==1 or location==3:
            #     deff = (self.clearCover + dbar/2 + dRow)
            # else:
            #     deff = self.h - (self.clearCover + dbar/2 + dRow)
                
            positions = self._getBarPositon(NBarRow, 
                                            self.bRow - dbar, 
                                            self.clearCover + dbar/2)
            
            if location==1 or location==2:
                xyOut = [(x, deff) for x in positions]            
            else:
                xyOut = [(deff, y) for y in positions]
                
            bars = [self.factory.getRebar(barType, xy) for xy in xyOut]            
            layers.append(RebarLayer(bars))
            barsRemaining -= self.NbarsMax
    
        return RebarCollection(layers)
    
    def place(self, Nbars:int, barType:str, location:RebarLocationEnum = 1,
              depthOverwrite = None):      
        """
        Place Nbars of the type "barType" within the rebar section. The location
        enumeration is used to specify where the section the bars are placed,
        i.e. at the bottom, top, left or right. By default the bars are placed
        in the bottom layer.

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
        self.section.addBars(self._place(Nbars, barType, location, depthOverwrite))
 
    
 
    
def RebarPlacerFactory(placementStrategy: RebarPlacementStrategyEnum) -> RebarPlacer:
    # pass
    if placementStrategy == RebarPlacementStrategyEnum.BeamBottomBars:
        return RebarPlacerRow
    # else:
    #     raise Exception('Not implemented yet!')
    

        
# class ___SectionRebarPlacer:
    

#     def __init__(self, section:SectionConcrete, 
#                        factory:RebarFactory, 
#                        cover:float):
        
#         self.section = section
#         self.factory = factory
        
#         self.cover = cover

#         self._setClearCover()
#         self.lUnit = section.lUnit

#     def _setClearCover(self, direction:str='x'):
        
#         self.dStirrup = self.section.stirrups.d
#         self.clearCover = self.cover + self.dStirrup

        
#         self.w = self.section.concrete.b
#         self.wRow = self.section.concrete.b -  self.clearCover*2

#     def getBarsInRow(self, Nbar:int, barType:str, 
#                      deff:float, width:float, direction:str='x'):
#         """
#         Evenly distributes a set of bars within a row.
#         """
        
#         if direction == 'x':
#             positions = self._getBarPositon(Nbar, self.section.b)
#             xyOut = [(x, deff) for x in positions]
#         else:
#             positions = self._getBarPositon(Nbar, self.section.d)
#             xyOut = [(deff, y) for y in positions]
        
#         bars = []
#         for ii in range(Nbar):
#             bars.append( self.factory.getRebar(barType, xyOut[ii]))
            
#         return  RebarCollection(bars)
            
#     def _getBarPositon(self, Nbar:int, width:float):
#         if Nbar == 1:
#             return [width/2]
#         else:
#             return list(np.linspace(0,1, Nbar)*width)


# class LayerPlacementStrategies(IntEnum):
#     """
#     In the 
#     """
#     # Strategy 1, bars are evenly distributed within a given width
#     # 1: |    .    |
#     # 2: | .     . |
#     # 4: | . . . . |
    
#     # 1: |    .    |
#     # 2: | .     . |
#     # 4: | ..   .. |

#     centered = 1
#     outterFirst = 2


# def getRebarLayer(Nbar:int, 
#                   barType:str, 
#                   factory:RebarFactory, 
#                   strategy:LayerPlacementStrategies = 1):
#     """
#     Creates a group of rebar at a y position in the section.
    

#     Returns
#     -------
#     None.

#     """

#     factory

# def getRebarLayerRow(self, Nbar:int, barType:str, 
#                  deff:float, width:float, direction:str='x'):
#     """
#     Evenly distributes a set of bars within a row.
#     """
    
#     if direction == 'x':
#         positions = self._getBarPositon(Nbar, self.section.b)
#         xyOut = [(x, deff) for x in positions]
#     else:
#         positions = self._getBarPositon(Nbar, self.section.d)
#         xyOut = [(deff, y) for y in positions]
    
#     bars = []
#     for ii in range(Nbar):
#         bars.append( self.factory.getRebar(barType, xyOut[ii]))
        
#     return  RebarCollection(bars)
            