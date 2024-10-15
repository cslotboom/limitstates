"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from limitstates.objects import (Member, SectionRectangle, initSimplySupportedMember, 
                          SectionCLT)
from limitstates.objects.display import MATCOLOURS, PlotConfigCanvas,  PlotConfigObject

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19, GypusmFlatCSA19
from limitstates import BeamColumn, EleDisplayProps

__all__ = ["BeamColumnGlulamCsa19", "getBeamColumnGlulamCsa19", 
           "BeamColumnCltCsa19", "DesignPropsClt19", "DesignPropsGlulam19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element.
    Beams will either be single span or multi-span. For multi-span beams,
    Lex and Ley need to be set.

    Parameters
    ----------
    firePortection : GypusmRectangleCSA19
        The the structural member used to represent the beam's position,
        orientation and support conditions.
    sectionFire : SectionRectangle
        The fire section for the beamcolumn member.
    lateralSupport : bool, optional
        A flag that is set equal to true if the beamcolumn has continuous
        lateral support for bending.
        For single spans beams. For multi-segment beams.
    isCurved : bool
        A flag that specifies if the beam is curved. Curved members are 
        not currently supported.
    Lex : float|list[float]
        The beam column's unsupported length in the section's x direction, which
        is typically the strong direction.
        If the beam is mult-segment, this is a list of the beam length, multiplied
        by the factor ke from table 
    Ley : float|list[float]
        The beam column's unsupported length in the section's y direction, which
        is typically the weak direction.
    keBending : float
        A factor that converts the actual span length into the effective span
        length. See table 7.4 for guidance. 
        If the beam is multispan, it must have the same number of entries 
        as Lex and Ley. 
    keCompression : float
        A factor that converts the actual span length into the effective span
        length for compression. See table A.4 for guidance. 

    """
    firePortection:GypusmRectangleCSA19 = None
    sectionFire:SectionRectangle = None
    lateralSupport:bool|list[bool] = True
    isCurved:bool = False
    Lex:float|list[float] = None
    Ley:float|list[float] = None
    
    kexB:float|list[float] = None
    kexC:float = None
    keyC:float = None
    
    burnDimensions:list[float] = None

@dataclass
class EleDisplayPropsGlulam19(EleDisplayProps):
    """
    Design propreties specifically for a glulam beamcolumn element

    """
    section:SectionRectangle
    member:Member
    
    sectionFire:SectionRectangle = None
    displayColor:str      = MATCOLOURS['glulam']
    displayColorBurnt:str = MATCOLOURS['glulamBurnt']
    displayColorLines:str = MATCOLOURS['glulamBurnt']
    
    configCanvas: PlotConfigCanvas = PlotConfigCanvas()
    configObject: PlotConfigObject = PlotConfigObject(displayColor)
    configObjectBurnt: PlotConfigObject = PlotConfigObject(displayColorBurnt)

    burnDimensions:list[float] = None
    displayLamHeight = 38
    
    


class BeamColumnGlulamCsa19(BeamColumn):
    """
    Design propreties for a glulam beam element.
    
    Glulam Beam columns can either be single span or multi-span. 
    The span lengths are required to be set manually
    
    
    Multi-span members with compression loads are not supported.
    
    For multi-span beams, Lex and Ley need to be set.


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
    designProps:DesignPropsGlulam19
    
    def __init__(self, member:Member, section:SectionRectangle,
                 designProps:DesignPropsGlulam19 = None, 
                 userProps:dataclass = None,
                 eleDisplayProps:dataclass = None):

        
        self._initMain(member, section)
        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if eleDisplayProps is None:
            eleDisplayProps = EleDisplayPropsGlulam19(self.section, 
                                                   self.member,
                                                   designProps.sectionFire)

        self._initProps(designProps, userProps, eleDisplayProps)
        
    def setLex(self, Lex):
        self.designProps.Lex = Lex
        
    def setLey(self, Ley):
        self.designProps.Ley = Ley       
    
    def setSectionFire(self, sectionFire, burnDims = None):
        self.designProps.sectionFire = sectionFire
        self.eleDisplayProps.sectionFire = sectionFire
        
        if burnDims is not None:
            self.designProps.burnDims = burnDims
            self.eleDisplayProps.burnDims = burnDims

    
def getBeamColumnGlulamCsa19(L:float, section:SectionRectangle, lUnit:str='m', 
                             firePortection:GypusmRectangleCSA19 = None,
                             Lex:float = None, 
                             Ley:float = None,
                             kexB:float = 1,
                             kexC:float = 1,
                             keyC:float = 1) -> BeamColumnGlulamCsa19:
    """
    A function used to return a beamcolumn based on an input length.
    The beam uses a simply supported elemet. If a different type
    of element is required, it should be manually defined with 
    "BeamColumnGlulamCsa19" instead.
    
    Default values are assigned to design propreties.

    Parameters
    ----------
    L : float
        The input length for the beamcolumn.
    section : SectionAbstract
        The section the beamcolumn ises.
    lUnit : str
        The units for the input length of the member.

    Returns
    -------
    BeamColumn
        The output beamcolumn object.

    """
    member = initSimplySupportedMember(L, lUnit)
    designProps = DesignPropsGlulam19()

    
    if firePortection:
        designProps.firePortection = firePortection
        
    if Lex:
        designProps.Lex = Lex
    else:
        designProps.Lex = L
    designProps.kexB = kexB
    designProps.kexC = kexC

    if Ley:
        designProps.Ley = Ley
    else:
        designProps.Ley = L
    designProps.keyC = keyC
    
    return BeamColumnGlulamCsa19(member, section, designProps)




@dataclass
class DesignPropsClt19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmFlatCSA19 = None
    fireSection:SectionCLT = None
    Lex:bool = False
    Ley:bool = False
        
    

class BeamColumnCltCsa19(BeamColumn):
    designProps:DesignPropsClt19
    section:SectionCLT
    
    def __init__(self, member:Member, section:SectionCLT, 
                 sectionOrientation:float = 0,
                 designProps:DesignPropsClt19 = None, 
                 userProps:dataclass = None,
                 eleDisplayProps:dataclass = None):
        """
        This design element treats the CLT panel as a beamcolumn.
        
        It is appropriate for modeling clt that acts in a one-way system,
        examples include line supported panels, or walls acting as columns.
        
        
        Parameters
        ----------
        member : Member
            The the structural member used to represent the beam's position,
            orientation and support conditions.
        section : SectionRectangle
            The section used.
        lUnit : str, optional
            the units used. The default is 'm'.
        designProps : DesignPropsGlulam19, optional
            The inital design propreties. The default is None, which creates 
            a empty DesignPropsGlulam19 object.
        userProps : dataclass, optional
            The user design propeties. The default is None, which creates an
            empty dataclass.

        Returns
        -------
        None.

        """
        
        self._initMain(member, section)
        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if eleDisplayProps is None:
            eleDisplayProps = EleDisplayProps(self.section, self.member)            
                    
        self._initProps(designProps, userProps, eleDisplayProps)
      
          
    def setSectionFire(self, sectionFire):
        self.designProps.sectionFire = sectionFire
        self.eleDisplayProps.sectionFire = sectionFire

        
def _getSection(element, useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return element.designProps.sectionFire
    else:
        return element.section

        
def _getphi(useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return 1
    else:
        return 0.9

        
def _getphiCr(useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return 1
    else:
        return 0.8

        
def _isGlulam(element:BeamColumn):
    """
    Checks if an element is timber or glulam.
    There may be better ways of checking if a element is of a certain type,
    for example we could add it to the design propreties.
    """
    if isinstance(element, BeamColumnGlulamCsa19):
        return True
    else:
        return False
        