"""
Contains functions for managing sections specific to CSAo86-19
"""

from typing import Union

from limitstates.objects.section import SectionConcrete, RebarLocationEnum
from limitstates.objects import (RebarPlacerRow, RebarSpacingConfig, 
                                 RebarPlacementStrategyEnum,
                                    SectionConcrete, RebarLocationEnum)
from .material import MaterialRebarCSA24

from .beamColumn import getSectionCr, getSectionSr, getSmin
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
        
    
    def getSpacingRules(self, 
                        barType: str, 
                        includeRadius = False) -> RebarSpacingConfig:
        
        archetypeBar = self.factory.getRebar(barType, lUnit='mm')
        d = archetypeBar.d

        # TODO review this material
        lFactor = self.section.concrete.mat.lConvert('mm')
        amax    = self.section.concrete.mat.amax * lFactor
        
        s = getSmin(d, amax)
        c = self.c
        
        # TODO: guarentee this is in mm
        if self.section.stirrups:
            dstirrup = self.section.stirrups.rebar.d
        else:
            dstirrup = 0
            
        if self.section.stirrups and includeRadius:
            rcurve = archetypeBar.rcurve
        else:
            rcurve = 0
        
        return RebarSpacingConfig(s, c, dstirrup, rcurve)
        
        
    def place(self, Nbars: int, barType: str, location: RebarLocationEnum): 
        
        config = self.getSpacingRules(barType)
        self.setSpacingConfig(config)

               
        self.section.addBars(self._place(Nbars, barType, location))
         
        
    
    
def placeRebarInElement(element: BeamColumnConcreteCsa24,
                        Nbars: int, barType: str,
                        sectionInd: int = 0,
                        placementStrategy: RebarPlacementStrategyEnum = 1,
                        placementKwargs: dict = None,
                        rebarMat: Union[MaterialRebarCSA24, None] = None, 
                        lUnit: str = 'mm'):
    """
    
    

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        DESCRIPTION.
    Nbars : int
        DESCRIPTION.
    barType : str
        DESCRIPTION.
    sectionInd : TYPE, optional
        DESCRIPTION. The default is 0.
    placementStrategy : RebarPlacementStrategyEnum, optional
        DESCRIPTION. The default is 1.
    placementKwargs : dict, optional
        DESCRIPTION. The default is None.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if placementStrategy != 1:
        raise Exception('Unsupported placement strategy used. Only strategies [1] are currently supported')
        
    if placementStrategy != 1:
        raise Exception('Unsupported placement strategy used.')

    if isinstance(element.section, list):
        raise Exception('Multiple sections in a concrete element is not supported.')
    section = element.section
    
    if placementStrategy == 1:
        placer = RebarPlacerRowCSA24(section, element.designProps, rebarMat, lUnit)
        location = placementKwargs['location']
        placer.place(Nbars, barType, location)
        
    
def placeRebarRowInElement(element: BeamColumnConcreteCsa24,
                            Nbars: int, barType: str,
                            sectionInd: int = 0,
                            location: RebarLocationEnum = 1,
                            rebarMat: Union[MaterialRebarCSA24, None] = None, 
                            lUnit: str = 'mm'):
    """
    
    

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        DESCRIPTION.
    Nbars : int
        DESCRIPTION.
    barType : str
        DESCRIPTION.
    sectionInd : TYPE, optional
        DESCRIPTION. The default is 0.
    placementStrategy : RebarPlacementStrategyEnum, optional
        DESCRIPTION. The default is 1.
    placementKwargs : dict, optional
        DESCRIPTION. The default is None.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    None.

    """

    if isinstance(element.section, list):
        raise Exception('Multiple sections in a concrete element is not supported.')
    section = element.section
    
    placer = RebarPlacerRowCSA24(section, element.designProps, rebarMat, lUnit)

    placer.place(Nbars, barType, location)
        
