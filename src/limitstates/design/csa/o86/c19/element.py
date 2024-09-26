"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from limitstates.objects import (Member, SectionRectangle, initSimplySupportedMember, 
                          SectionCLT)

from limitstates.objects.display import MATCOLOURS

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19, GypusmFlatCSA19
from limitstates import BeamColumn, DisplayProps

__all__ = ["BeamColumnGlulamCsa19", "getBeamColumnGlulamCsa19", 
           "BeamColumnCltCsa19", "DesignPropsClt19", "DesignPropsGlulam19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element

    Parameters
    ----------
    firePortection : GypusmRectangleCSA19
        The the structural member used to represent the beam's position,
        orientation and support conditions.
    fireSection : SectionRectangle
        The fire section for the beamcolumn member.
    lateralSupport : bool, optional
        A flag that is set equal to true if the beamcolumn has continuous
        lateral support for beidng
    isCurved : bool
        A flag that specifies if the beam is curved. Curved members are 
        not currently supported.
    Lex : float
        The beam column's unsupported length in the section's x direction, which
        is typically the strong direction.
    Ley : float
        The beam column's unsupported length in the section's x direction, which
        is typically the strong direction.        


    """
    firePortection:GypusmRectangleCSA19 = None
    fireSection:SectionRectangle = None
    lateralSupport:bool = True
    isCurved:bool = False
    Lex:bool = None
    Ley:bool = None

@dataclass
class DisplayPropsGlulam19(DisplayProps):
    """
    Design propreties specifically for a glulam beamcolumn element

    """
    section:SectionRectangle
    member:Member
    
    c:float = MATCOLOURS['glulam']
    cBurnt:str = MATCOLOURS['glulamBurnt']


class BeamColumnGlulamCsa19(BeamColumn):
    """
    Design propreties for a glulam beam element.

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
    displayProps : dataclass
        Propreties used to display the section.

    Returns
    -------
    None.

    """
    designProps:DesignPropsGlulam19
    
    def __init__(self, member:Member, section:SectionRectangle,
                 designProps:DesignPropsGlulam19 = None, 
                 userProps:dataclass = None,
                 displayProps:dataclass = None):

        
        self._initMain(member, section)
        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if displayProps is None:
            displayProps = DisplayPropsGlulam19(self.section, self.member)

        self._initProps(designProps, userProps, displayProps)
        
    def setLex(self, Lex):
        self.designProps.Lex = Lex
        
    def setLey(self, Ley):
        self.designProps.Ley = Ley       
        
def getBeamColumnGlulamCsa19(L:float, section:SectionRectangle, lUnit:str='m', 
                             firePortection:GypusmRectangleCSA19 = None,
                             Lex:float = None, 
                             Ley:float = None) -> BeamColumnGlulamCsa19:
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
    lunit : str
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
    
    if Ley:
        designProps.Ley = Ley
    else:
        designProps.Ley = L
    
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
                 displayProps:dataclass = None):
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
        if displayProps is None:
            displayProps = DisplayProps(self.section, self.member)            
                    
        self._initProps(designProps, userProps, displayProps)
      
        
def _getSection(element, useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return element.designProps.fireSection
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
        