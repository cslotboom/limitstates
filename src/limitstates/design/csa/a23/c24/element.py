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
    Design propreties specifically for a glulam beamcolumn element.
    Beams will either be single span or multi-span. For multi-span beams,
    Lx and Ly need to be set.
    
    Note Lx is the design length of an element. Lex is the effective design
    length, which is Lx * kx
    
    There are different design factors set for bending and compression design.
    This is because sometimes the top bracing for bending does not brace
    the full member in compression.
    

    Parameters
    ----------
    lateralSupport : bool, optional
        A flag that is set equal to true if the beamcolumn has continuous
        lateral support for bending.
        For single spans beams. For multi-segment beams.
    Lx : float, list[float]
        The beam column's unsupported length in the section's x direction, which
        is typically the strong direction.
        If the beam is mult-segment, this is a list of the beam length, multiplied
        by the factor ke from table 
    Ly : float, list[float]
        The beam column's unsupported length in the section's y direction, which
        is typically the weak direction.
    kexB : float
        A factor that converts the actual span length into the effective span
        length. See table 7.4 for guidance. 
        If the beam is multispan, it must have the same number of entries 
        as Lx and Ly. 
    kexC : float
        A factor that converts the actual span length into the effective span
        length for compression. See table A.4 for guidance. 
    keyC : float
        A factor that converts the actual span length into the effective span
        length for compression. See table A.4 for guidance. 
    """
    
    
    cover: float = None
    lam: float = 1
    shearReinforcementType: float = 1
    theta: float = radians(35)
    sectionRegions:list[list[float]] = None
    
    
    # lateralSupport:Union[bool,list[bool]] = True
    
    # Lx:Union[float,list[float]] = None
    # Ly:Union[float,list[float]] = None
    
    # kexB:Union[float,list[float]] = None
    # kexC:float = None
    # keyC:float = None
    
    # def setkexB(self, kexB):
    #     self.kexB  = kexB
    #     self.Lexb = self.Lx * self.kexB 
        
    # def setkexC(self, kexC):
    #     self.kexC  = kexC
    #     self.LexC = self.Lx * self.kexC 
        
    # def setkeyC(self, keyC):
    #     self.keyC  = keyC
    #     self.LeyC = self.Ly * self.keyC
        

@dataclass
class EleDisplayPropsConcrete24(EleDisplayProps):
    """
    The plot indicie is only needed if no section is provided. A provided
    section will overwrite the 
    """

    fillColorLines: str = MATCOLOURS['steel']
    sectionInd: int = 0
    cover: float = 0
            
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
    Design propreties for a glulam beam element.
    
    Glulam Beam columns can either be single span or multi-span. 
    The span lengths are required to be set manually
    
    
    Multi-span members with compression loads are not supported.
    
    For multi-span beams, Lx and Ly need to be set.
    
    When setting plot displays, the section.
    If a section is manually set, the index is ignored.


    Parameters
    ----------
    member : Member
        The the structural member used to represent the beam's position,
        orientation and support conditions.
    section : SectionRectangle
        The section for the beamcolumn.
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
        # self._initMain(member, section)
        
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

class SectionNASolverCsa24:
    pass