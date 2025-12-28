"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""
from typing import Union
from dataclasses import dataclass
from enum import IntEnum
from math import radians

from limitstates.objects import (Member, SectionConcrete, initSimplySupportedMember)
from limitstates.objects.display import MATCOLOURS, PlotConfigCanvas,  PlotConfigObject
from limitstates import BeamColumn, EleDisplayProps, PlotOriginPositionEnum



#need to input GypusmRectangleCSA19 directly to avoid circular import errors

__all__ = ["DesignPropsConcrete24", "EleDisplayPropsConcrete24",
           "BeamColumnConcreteCsa24"]



phiC = 0.65
phiS = 0.85

class ShearConfigurations(IntEnum):
    MinTransverse = 1
    NoTransverse = 2
    NoTransverseAmax20 = 3


@dataclass
class DesignPropsConcrete24:
    """
    Design propreties specifically for a concrete beamcolumn element.   

    Parameters
    ----------
    cover : bool, optional
        The cover to use in the concrete element. Units will match the section
        units
    lam : float, optional
        The concrete density factor. Taken as 1 for normal density concrete.
        See c.l. 8.6.5
    shearReinforcementType : ShearConfigurations, list[float]
        The condition used for shear reinforcement, this affects the beta value
        that gets set by the user. See cl 11.3.6.3
    theta : float
        The angle of diagonal compressive stress along the cross section, 
        taken as 35 degrees by default. See cl 11.3.6.3
    sectionRegions : None
        A list of regions each section will apply to, set in units of the 
        concrete elment. This only applys to concrete elements that have 
        multiple sectons. 

    """
    
    
    cover: float = None
    lam: float = 1
    shearReinforcementType: ShearConfigurations = 1
    theta: float = radians(35)
    sectionRegions:list[list[float]] = None
            

@dataclass
class EleDisplayPropsConcrete24(EleDisplayProps):
    """
    A class that aggregates all propreties which will be used to visualize
    outputs from elements.

    The plot indicie is only needed if no section is provided. If a section 
    has been set, the plot index will be ingored. 
    
    Parameters
    ----------
    section : str, SectionAbstract
        The section that will be used for plotting/display. 
        This can be different than design section.
    member : str, SectionAbstract
        The member used for plotting/display. This can be different than the
        design section..
    configCanvas : str, PlotConfigCanvas
        A configuration object that stores the canvas's . 
    configObject : str, PlotConfigObject
        A configuration object that stores the objects display propreties,
        i.e. colour linestyle etc. 
    fillColorLines : str, SectionAbstract
        The colour used for internal fill objects, in this case stee.
    sectionInd : str, PlotConfigCanvas
        The index of the section to plot. If a section has been set, the plot 
        index will be ingored. 
    cover : str, PlotConfigObject
        The cover to be used in the plots. When not set, this defaults to the
        cover defined in DesignPropsConcrete24.
        
    """


    fillColorLines: str = MATCOLOURS['steel']
    sectionInd: int = 0
    cover: float = None
            
    def __post_init__(self):
        if self.configCanvas == None:
            self.configCanvas = PlotConfigCanvas()
 
        if self.configObject == None:
            self.configObject = PlotConfigObject(MATCOLOURS['concrete'],
                                                 cFillLines = MATCOLOURS['black'],
                                                 cFillPatch = MATCOLOURS['steel'],
                                                 originLocation = 2,
                                                 patchType = 2)
    
        
class BeamColumnConcreteCsa24(BeamColumn):
    """
    Design propreties for a A23.3 concrete beam element. The element can
    have multiple sections assigned to it, with different rebar configurations
    in each.
    
    Multispan beams are currently not supported.

    Parameters
    ----------
    member : Member
        The the structural member used to represent the beam's position,
        orientation and support conditions.
    section : Union[SectionConcrete, list[SectionConcrete]]
        The section, or section group for the beamcolumn.
    designProps : DesignPropsGlulam19, optional
        The inital design propreties. The default is None, which creates 
        a empty DesignPropsGlulam19 object.
    userProps : dataclass, optional
        The user design propeties. The default is None, which creates an
        empty dataclass.
    eleDisplayProps : dataclass
        Propreties used to display the element.

    Returns
    -------
    None.

    """
    designProps: DesignPropsConcrete24
    section: SectionConcrete
    
    def __init__(self, 
                 member: Member, 
                 section: Union[SectionConcrete, list[SectionConcrete]],
                 designProps: DesignPropsConcrete24 = None, 
                 userProps: dataclass = None,
                 eleDisplayProps: EleDisplayPropsConcrete24 = None):

        if isinstance(section, list):
            raise Exception('MultiSection Elements are not supported yet.')
        
        self.member = member
        self.section = section
        
        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsConcrete24()

        eleDisplayProps = self._initDispProps(eleDisplayProps, designProps)

        self._initProps(designProps, userProps, eleDisplayProps)
        
    def setLx(self, Lx):
        self.designProps.Lx = Lx
        
    def setLy(self, Ly):
        self.designProps.Ly = Ly       
    
    def getSection(self, ind: int = 0):
        if isinstance(self.section, list):
            return self.section[ind]
        else:
            return self.section

    def _initDispProps(self, eleDisplayProps: EleDisplayPropsConcrete24,
                       designProps: DesignPropsConcrete24):

        # Extract cover        
        cover = designProps.cover
        
        # Nothing is provided, use default propreties.
        if eleDisplayProps is None:
            ind = 0
            plotSection = self.getSection(ind)
            plotMember  = self.member
            return EleDisplayPropsConcrete24(plotSection, 
                                             plotMember,
                                             sectionInd = ind,
                                             cover = cover)
        
        if not eleDisplayProps.cover:
            eleDisplayProps.cover = cover

        # Initialize the design propreties if none are given.
        if eleDisplayProps.section:
            pass
        elif (eleDisplayProps.sectionInd):
            eleDisplayProps.section = self.getSection(eleDisplayProps.sectionInd)    
        else:
            ind = 0
            eleDisplayProps.sectionInd = ind
            eleDisplayProps.section = self.getSection(ind)    

        # Initialize the design propreties if none are given.
        if not eleDisplayProps.member:
           eleDisplayProps.member  = self.member
        
        return eleDisplayProps
