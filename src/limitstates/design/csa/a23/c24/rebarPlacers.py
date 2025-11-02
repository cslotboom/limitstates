"""
Contains functions for managing sections specific to CSAo86-19
"""

from typing import Union

from limitstates.objects.section import SectionConcrete, RebarLocationEnum
from limitstates.objects import (RebarPlacerRow, RebarPlacementStrategyEnum, 
                                 Rebar, StirrupPlacerRow, Stirrup, 
                                 RebarFactory, StirrupGroup)
from .material import MaterialRebarCSA24

from .beamColumn import getSectionSpacingRules
from .section import REBARFACTORY
from .element import BeamColumnConcreteCsa24, DesignPropsConcrete24



def _initRebarFactory(rebarMat, lUnit) -> RebarFactory:
    rebarFactory = REBARFACTORY
    
    if lUnit != None:
        rebarFactory.setLunit(lUnit)
    
    if rebarMat is None:
        pass
    else:
        rebarFactory.setMaterial(rebarMat)
    
    return  rebarFactory

class RebarPlacerRowCSA24(RebarPlacerRow):
        
    def __init__(self, section: SectionConcrete, 
                 designProps: DesignPropsConcrete24, 
                 rebarMat: Union[MaterialRebarCSA24, None] = None, 
                 lUnit: str = None):
        
        rebarFactory =  _initRebarFactory(rebarMat, lUnit)
        
        self.c = designProps.cover
        super().__init__(section, rebarFactory)
        
    def _getBar(self, barType):
        return self.factory.getRebar(barType, lUnit='mm')
               
        
    def place(self, Nbars: int, barType: str, 
              location: RebarLocationEnum, depthOverwrite: float = None,
              dstirOverwrite:float = None, includeRadius:bool = True): 
        
        bar = self._getBar(barType)
        config = getSectionSpacingRules(bar, self.section, self.c, includeRadius,
                                        lUnit = 'mm')
        self.setSpacingConfig(config)

        self.section.addBars(self._place(Nbars, barType, location, 
                                         depthOverwrite, dstirOverwrite))
         
        
    
    
def placeRebarInElement(element: BeamColumnConcreteCsa24,
                        Nbars: int, barType: str,
                        sectionInd: int = 0,
                        placementStrategy: RebarPlacementStrategyEnum = 1,
                        includeRadius:bool = False,
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
        The number of bars to place,in the section.
    barType : str
        The type of bar to place e.g. 10M..
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
    includeRadius : bool
        A flag that specifies whether or not the curve diameter of the stirrup
        rebar should be considered when placing the row.
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
        placer.place(Nbars, barType, location, includeRadius = includeRadius)


def placeRebarRowInElement(element: BeamColumnConcreteCsa24,
                            Nbars: int, barType: str,
                            sectionInd: int = 0,
                            includeRadius:bool = False,
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
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    includeRadius : bool
        A flag that specifies whether or not the curve diameter of the stirrup
        rebar should be considered when placing the row.
    location : RebarLocationEnum, optional
        The face to place the rebar on: Bottom = 1, Top = 2, Left = 3, 
        Right = 4
    rebarMat : Union[MaterialRebarCSA24, None], optional
        The rebar material to use, if specified this will overwrite the default
        material specified.

    """

    if sectionInd != 0:
        raise Exception('Multiple sections in a concrete element is not supported.')
    section = element.section
    
    placer = RebarPlacerRowCSA24(section, element.designProps, rebarMat, lUnit)

    placer.place(Nbars, barType, location, includeRadius = includeRadius)
        




class StirrupPlacerRowCSA24(StirrupPlacerRow):
        
    def __init__(self, section: SectionConcrete, 
                 designProps: DesignPropsConcrete24, 
                 rebarMat: Union[MaterialRebarCSA24, None] = None, 
                 lUnit: str = None):
        
        self.c = designProps.cover
        rebarFactory =  _initRebarFactory(rebarMat, lUnit)
        
        super().__init__(section, rebarFactory = rebarFactory)
        
        
    def _getBar(self, barType):
        return self.factory.getRebar(barType, lUnit='mm')
               
    
            
    def _place(self, NStirrups: int, barType: str, 
               yDir: bool, spacing:float, Nleg: int,
               dshift) -> StirrupGroup:   
    
        self._initPlacement(barType, yDir)
        positions = self._getStirrupPositions(NStirrups, yDir, dshift)

        stirrups = []
        for ii in range(NStirrups):
            rebar = self.factory.getRebar(barType)
            stirrup = Stirrup(rebar, Nleg = Nleg, spacing = spacing, 
                              position = positions[ii])
            stirrups.append(stirrup)
        return stirrups


    def place(self,  NStirrups:int, barType:str, yDir: bool = True,
              Nleg: int = 2, spacing: float = 200, dshift:float = None): 
                
        if not self.factory:
            raise Exception('A rebar Factor has to be set to place rebar.')
        
        stirrups= self._place(NStirrups, barType, yDir, Nleg, spacing, dshift)
        self.section.setStirrups(stirrups)
       
     
    def _initPlacement(self, barType, yDir:bool):
        try:
            self.dstir = self.factory.dbDict[barType]['d']
        except:
            raise Exception('The input bar type could not be found in the database.')
        
        self._setDimensions(yDir)
        self._setCenterLineCover()
    
    
    def setPosition(self,  yDir: bool = True, dshift:float = None): 
        
        barType  = self.section.stirrups[0].rebar.name
        self._initPlacement(barType, yDir)
        
        positions = self._set(yDir, dshift)
        for pos, stirrup in zip(positions, self.section.stirrups):
            stirrup.setPosition(pos)
            
            
            
            
   
def placeStirrupRowInElement(element: BeamColumnConcreteCsa24,
                            NStirrups: int, barType: str,
                            sectionInd: int = 0,
                            yDir: bool = True,
                            Nleg: int = 2, spacing: float = 200,
                            dshift:float = None,
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

    if sectionInd != 0:
        raise Exception('Multiple sections in a concrete element is not supported.')
    
    section = element.getSection(sectionInd)
    
    placer = StirrupPlacerRowCSA24(section, element.designProps, rebarMat, lUnit)

    placer.place(NStirrups, barType, yDir, Nleg, spacing, dshift)
                 
            
            