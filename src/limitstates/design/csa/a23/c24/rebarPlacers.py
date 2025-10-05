"""
Contains functions for managing sections specific to CSAo86-19
"""

from typing import Union

from limitstates.objects.section import SectionConcrete, RebarLocationEnum
from limitstates.objects import (RebarPlacerRow, RebarPlacementStrategyEnum, 
                                 Rebar)
from .material import MaterialRebarCSA24

from .beamColumn import getSectionSpacingRules
from .section import REBARFACTORY
from .element import BeamColumnConcreteCsa24, DesignPropsConcrete24


class RebarPlacerRowCSA24(RebarPlacerRow):
        
    def __init__(self, section: SectionConcrete, 
                 designProps: DesignPropsConcrete24, 
                 rebarMat: Union[MaterialRebarCSA24, None] = None, 
                 lUnit: str = None):
        
        rebarFactory = REBARFACTORY
        if lUnit != None:
            rebarFactory.setLunit(lUnit)
        
        if rebarMat is None:
            pass
        else:
            rebarFactory.setMaterial(rebarMat)
        
        self.c = designProps.cover
        super().__init__(section, rebarFactory)
        
    def _getBar(self, barType):
        return self.factory.getRebar(barType, lUnit='mm')
               
        
    def place(self, Nbars: int, barType: str, 
              location: RebarLocationEnum, depthOverwrite: float = None): 
        
        # config = self.getSpacingRules(barType)
        bar = self._getBar(barType)
        config = getSectionSpacingRules(bar, self.section, self.c, lUnit = 'mm')
        self.setSpacingConfig(config)

        self.section.addBars(self._place(Nbars, barType, location, depthOverwrite))
         
        
    
    
def placeRebarInElement(element: BeamColumnConcreteCsa24,
                        Nbars: int, barType: str,
                        sectionInd: int = 0,
                        placementStrategy: RebarPlacementStrategyEnum = 1,
                        placementKwargs: dict = None,
                        rebarMat: Union[MaterialRebarCSA24, None] = None, 
                        lUnit: str = 'mm'):
    """
    Places lognditudinal rebar in a concerete Element according to a strategy.
    The number and type of bars is placed in the section specified by 
    sectionInd, according to the strategy used.
    
    Currently only one strategy is supported, RebarPlacementStrategyEnum = 1.
    See RebarPlacementStrategyEnum for a more detailed review of what each 
    strategy reqires


    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to place rebar in.
    Nbars : int
        The number of bars to place, e.g. 10M.
    barType : str
        The type of bar to place.
    sectionInd : TYPE, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    placementStrategy : RebarPlacementStrategyEnum, optional
        The placement strategy to use.
            - strategy 1: Face. Rebar is placed in rows along one of the faces 
            of the concrete element.
                - Kwargs requries a "RebarLocationEnum" enumeration
            - strategy 2: Face with Radius. Rebar is placed in rows along one 
            of the faces of the concrete element, and rebar will respect the
            radius of the stirrups
            - strategy 3: Perimeter. Rebar is placed evenly around the 
            perimeter of the section.
    placementKwargs : dict, optional
        Additional keyword arguments required for each stategy. 
        The default is None.
    rebarMat : Union[MaterialRebarCSA24, None], optional
        The rebar material to use, if specified this will overwrite the default
        material specified.


    """
    if placementStrategy != 1:
        raise Exception('Unsupported placement strategy used. Only strategies [1] are currently supported')
        
    if placementStrategy != 1:
        raise Exception('Unsupported placement strategy used.')

    if isinstance(element.section, list):
        raise Exception('Multiple sections in a concrete element is not supported.')
    section = element.section
    
    if placementStrategy == 1:
        placer   = RebarPlacerRowCSA24(section, element.designProps, 
                                       rebarMat, lUnit)
        location = placementKwargs['location']
        placer.place(Nbars, barType, location)


def placeRebarRowInElement(element: BeamColumnConcreteCsa24,
                            Nbars: int, barType: str,
                            sectionInd: int = 0,
                            location: RebarLocationEnum = 1,
                            rebarMat: Union[MaterialRebarCSA24, None] = None, 
                            lUnit: str = 'mm'):
    """
    Places lognditudinal rebar in a concerete Element by row. The number and 
    type of bars is placed in the section in rows, until the row is filled up.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to place rebar in.
    Nbars : int
        The number of bars to place.
    barType : str
        The type of bar to place, e.g. 10M.
    sectionInd : TYPE, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    location : RebarLocationEnum, optional
        The face to place the rebar on: Bottom = 1, Top = 2, Left = 3, 
        Right = 4
    rebarMat : Union[MaterialRebarCSA24, None], optional
        The rebar material to use, if specified this will overwrite the default
        material specified.

    """

    if isinstance(element.section, list):
        raise Exception('Multiple sections in a concrete element is not supported.')
    section = element.section
    
    placer = RebarPlacerRowCSA24(section, element.designProps, rebarMat, lUnit)

    placer.place(Nbars, barType, location)
        
