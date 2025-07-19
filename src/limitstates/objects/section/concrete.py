"""
Represents a concrete section.

"""

from abc import ABC, abstractmethod
from enum import IntEnum
from dataclasses import dataclass
import math


import numpy as np

from .section import SectionMonolithic, SectionRectangle
from .rebar import RebarFactory, RebarCollection, StirrupGroup, Rebar, RebarLayer


class SectionConcrete:
    """
    Represents a concrete section. The concrete is composed of longditudinal 
    rebar (top / bottom bars), and transverse rebar ()
    
    Special sections, such as T-beams cannot be repersented using this section.
    
    
    """
    concrete:SectionRectangle
    rebar:RebarCollection
    stirrups:StirrupGroup
    
    
    def __init__(self, concrete:SectionRectangle,
                        rebar:RebarCollection = None,
                        stirrups:StirrupGroup = None):
        self.concrete = concrete
        self.rebar = rebar
        self.stirrups = stirrups

    # TODO: DOCUMENT
    def addBars(self, rebar:RebarCollection):
        if not self.rebar:
            self.rebar = rebar
        else:
            self.rebar.addBars(rebar.groups)

    def getdMax(self, xDirection:bool=False, 
                positiveMoment:bool=True):
        
        if xDirection:
            positions = self.rebar.getxCoords()
        else:
            positions = self.rebar.getyCoords()
        return positions

    def getWidth(self, yMoment:bool = True, 
                 positiveMoment = True, lunit = 'mm'):
        lfactor = self.concrete.lConvert(lunit)
        if yMoment:
            b = self.concrete.b * lfactor
        else:
            b = self.concrete.d * lfactor
        return b

    def getDepth(self, yMoment:bool = True, 
                 positiveMoment = True, lunit = 'mm'):
        lfactor = self.concrete.lConvert(lunit)
        if yMoment:
            d = self.concrete.d * lfactor
        else:
            d = self.concrete.b * lfactor
        return d

class SectionNASolver:
    """
    Solves for the neutral axis in the section using a 
    
    
    Assumes all bars use the same material.
    
    Solves for the neutral axis within a section.
    The neutral axis is measured from the top of the section.
    """
    
    def __init__(self, section: SectionConcrete, 
                 concreteFunction, steelFunction,
                 Pf:float = 0, yMoment: bool = True, 
                 positiveMoment:bool = True,
                 tol: float = 1e-3, maxIter: float = 100,
                 logging:bool = True):
        
        self.section = section
        self.rebar = section.rebar
        
        self.compressiveFunction = concreteFunction
        self.steelFunction = steelFunction
        
        self.yMoment = yMoment
        self.positiveMoment = positiveMoment
        
        if yMoment:
            self.rebarCoords = self.rebar.getyCoords(flatten=True)
            self.d = section.concrete.d
            self.b = section.concrete.b
        else:
            self.rebarCoords = self.rebar.getxCoords(flatten=True)
            self.d = section.concrete.b
            self.b = section.concrete.d

        # If the moment isn't positive, flip the orientation of the rebar
        if not positiveMoment:
            self.rebarCoords = self.d - self.rebarCoords
        
        self.tol = tol
        self.maxIter = maxIter
        self.logging = logging

    def getCr(self, NAtrial):
        return self.compressiveFunction(self.section, NAtrial, 
                                        self.yMoment, self.positiveMoment)
    
    def getFsteel(self, NAtrial):
        return self.steelFunction(self.section, NAtrial, 
                                        self.yMoment, self.positiveMoment)

        
    def checkEqulibrium(self, NAtrial):
        """
        Checks the equlibrium at the current state.

        """
        Cr = self.getCr(NAtrial)
        Fsteel = self.getFsteel(NAtrial)        
        Fnet = np.sum(Fsteel)
        ratio = float(Fnet/Cr)

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

        NAtrial = self.d / 2
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
             Pf:float = 0, momentDirection: str = 'x', 
             positiveMoment = True,
             tol: float = 1e-3, maxIter: float = 100):
    
    
    naSolver = SectionNASolver(section, Pf, momentDirection, positiveMoment, 
                               tol, maxIter)


    return naSolver.calcNA()

class RebarPlacementStrategyEnum(IntEnum):
    Face = 1
    Perimeter = 2
    FaceWithRadius = 1

class RebarLocationEnum(IntEnum):
    Bottom = 1
    Top = 2
    Left = 3
    Right = 4
    
@dataclass
class   RebarPlacementConfig:
    clearSpacing: float
    cover: float
    dstirrup: float
    stirrupCurveRadius: float = 0

# TODO, restructure
class RebarPlacer(ABC):
    
    def __init__(self, section: SectionConcrete,
                 placementConfig: RebarPlacementConfig, 
                 rebarFactory: RebarFactory):

        self.section      = section 
        self.factory = rebarFactory
        
        self.c = placementConfig.cover
        self.s = placementConfig.clearSpacing
        self.dstir = placementConfig.dstirrup
        self.rcurve = placementConfig.stirrupCurveRadius
                
    @abstractmethod
    def place(self, Nbars:int, barType:str):
        pass



class RebarPlacerManual():
    def __init__(self, factory:RebarFactory):
        self.factory = factory
        
    def getRebarLayer(self, Nbar:int, barType:str, 
                     deff:float, width:float, offset:float = 0, 
                     yDirection:bool = True) -> RebarLayer:
        """
        Evenly distributes Nbar of the given type within a row width wide, 
        and centered around deff.
        
        deff is measured from the top of the section for the rebar placed in
        the y axis, or from the right wall for rebar placed in the x axis.
        
        """
        
        if yDirection:
            positions = self._getBarPositon(Nbar, width, offset)
            xyOut = [(x, deff) for x in positions]
        else:
            positions = self._getBarPositon(Nbar, width)
            xyOut = [(deff, y) for y in positions]
        
        bars = []
        for ii in range(Nbar):
            bars.append(self.factory.getRebar(barType, xyOut[ii]))
            
        return  RebarLayer(bars)
            
    def _getBarPositon(self, Nbar:int, width:float, offset:float):
        
        if Nbar == 1:
            return [(width - offset)/2]
        else:
            return list(np.linspace(offset, width + offset, Nbar))
        
    def place(self, Nbar:int, barType:str, deff:float, width:float, 
              offset:float = 0, direction:str='x'):
        
        
        self.section.addBars(self.getRebarLayer(Nbar, barType, 
                                                deff, width, 
                                                offset, direction))


class RebarPlacerRow(RebarPlacer):
    
    def __init__(self, section:SectionConcrete, 
                 placementConfig:RebarPlacementConfig, 
                 rebarFactory):
        super().__init__(section, placementConfig, rebarFactory)
    
    def _setDimensions(self, location):
        if location == 1 or location == 2:
            self.h = self.section.concrete.d
            self.b = self.section.concrete.b
            
        else:
            self.h = self.section.concrete.b
            self.b = self.section.concrete.h     

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
   
    def _place(self, Nbars:int, barType:str, location:RebarLocationEnum):
        if Nbars < 2:
            raise Exception('Two or more bars must be placed in the section.')        
        
        self._initPlacement(barType, location)
        
        NrowRequired  = math.ceil(Nbars / self.NbarsMax)
        barsRemaining = Nbars 
        
        layers = []
        bars   = RebarLayer()
        
        dbar = self.dbar
        
        for ii in range(NrowRequired):
            if barsRemaining > self.NbarsMax:
                NBarRow = self.NbarsMax
            else:
                NBarRow = barsRemaining                
            
            if location==1 or location==3:
                deff = (self.clearCover + dbar/2 + (dbar + self.s)*ii)
            else:
                deff = self.h - (self.clearCover + dbar/2 + (dbar + self.s)*ii)
                
            
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
    
    def place(self, Nbars:int, barType:str, location:RebarLocationEnum):                
        self.section.addBars(self._place(Nbars, barType, location))
 
def RebarPlacerFactory(placementStrategy: RebarPlacementStrategyEnum) -> RebarPlacer:
    # pass
    if placementStrategy == RebarPlacementStrategyEnum.BeamBottomBars:
        return RebarPlacerRow
    # else:
    #     raise Exception('Not implemented yet!')
    

        
class ___SectionRebarPlacer:
    

    def __init__(self, section:SectionConcrete, 
                       factory:RebarFactory, 
                       cover:float):
        
        self.section = section
        self.factory = factory
        
        self.cover = cover

        self._setClearCover()
        self.lUnit = section.lUnit

    def _setClearCover(self, direction:str='x'):
        
        self.dStirrup = self.section.stirrups.d
        self.clearCover = self.cover + self.dStirrup

        
        self.w = self.section.concrete.b
        self.wRow = self.section.concrete.b -  self.clearCover*2

    def getBarsInRow(self, Nbar:int, barType:str, 
                     deff:float, width:float, direction:str='x'):
        """
        Evenly distributes a set of bars within a row.
        """
        
        if direction == 'x':
            positions = self._getBarPositon(Nbar, self.section.b)
            xyOut = [(x, deff) for x in positions]
        else:
            positions = self._getBarPositon(Nbar, self.section.d)
            xyOut = [(deff, y) for y in positions]
        
        bars = []
        for ii in range(Nbar):
            bars.append( self.factory.getRebar(barType, xyOut[ii]))
            
        return  RebarCollection(bars)
            
    def _getBarPositon(self, Nbar:int, width:float):
        if Nbar == 1:
            return [width/2]
        else:
            return list(np.linspace(0,1, Nbar)*width)


class LayerPlacementStrategies(IntEnum):
    """
    In the 
    """
    # Strategy 1, bars are evenly distributed within a given width
    # 1: |    .    |
    # 2: | .     . |
    # 4: | . . . . |
    
    # 1: |    .    |
    # 2: | .     . |
    # 4: | ..   .. |

    centered = 1
    outterFirst = 2


def getRebarLayer(Nbar:int, 
                  barType:str, 
                  factory:RebarFactory, 
                  strategy:LayerPlacementStrategies = 1):
    """
    Creates a group of rebar at a y position in the section.
    

    Returns
    -------
    None.

    """

    factory

def getRebarLayerRow(self, Nbar:int, barType:str, 
                 deff:float, width:float, direction:str='x'):
    """
    Evenly distributes a set of bars within a row.
    """
    
    if direction == 'x':
        positions = self._getBarPositon(Nbar, self.section.b)
        xyOut = [(x, deff) for x in positions]
    else:
        positions = self._getBarPositon(Nbar, self.section.d)
        xyOut = [(deff, y) for y in positions]
    
    bars = []
    for ii in range(Nbar):
        bars.append( self.factory.getRebar(barType, xyOut[ii]))
        
    return  RebarCollection(bars)
            