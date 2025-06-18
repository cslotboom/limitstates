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




# class RebarPlacer:
#     def __init__(self, ):
#         pass


        
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
            