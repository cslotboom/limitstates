"""
Represents a concrete section.

"""

from abc import ABC
from enum import IntEnum

import numpy as np

from .section import SectionMonolithic, SectionRectangle
from .rebar import RebarFactory, RebarCollection, StirrupGroup


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


    def getdMax(self, xDirection:bool=False, positiveMoment:bool=True):
        
        if xDirection:
            positions = self.rebar.getxCoords()
        else:
            positions = self.rebar.getyCoords()

    def getWidth(self, yMoment:bool = True, 
                 positiveMoment = True, lunit = 'mm'):
        lfactor = self.concrete.lConvert(lunit)
        if yMoment:
            b = self.concrete.b * lfactor
        else:
            b = self.concrete.d * lfactor
        return b



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
                 tol: float = 1e-3, maxIter: float = 100):
        
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
            self.rebarCoords = self.rebarCoords[::-1]


        # self.eConc  = section.concrete.mat.ey
        # self.concMat = section.concrete.mat
                
        self.trials = []
        self.residual = []
        
        self.tol = tol
        self.maxIter = maxIter
    

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
    
    def calcNA(self, root = 0.5):
        NAtrial = self.d / 2
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

        # diff = np.diff(self.trials)
        # if 0.0001 < abs(diff[-1]):
        #     raise Exception('Convergence not reached. Try a smaller root in the solver.')
        
        self.Niters = nn
        self.section.NA = NAtrial
        
        return NAtrial    

    

def solveForNA(section: SectionConcrete, 
             Pf:float = 0, momentDirection: str = 'x', 
             positiveMoment = True,
             tol: float = 1e-3, maxIter: float = 100):
    
    
    naSolver = SectionNASolver(section, Pf, momentDirection, positiveMoment, 
                               tol, maxIter)


    return naSolver.calcNA()
# class RebarPlacer:
#     def __init__(self, ):
#         pass


        
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
            