"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from .....objects import (Member, SectionRectangle, initSimplySupportedMember, 
                          SectionCLT)

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19, GypusmFlatCSA19
from limitstates import BeamColumn, DisplayProps

__all__ = ["GlulamBeamColumnCSA19", "getBeamColumnGlulamCSA19", 
           "CltBeamColumnCSA19", "DesignPropsClt19", "DesignPropsGlulam19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmRectangleCSA19 = None
    fireSection:SectionRectangle = None
    lateralSupport:bool = True
    isCurved:bool = False
    Lex:bool = None
    Ley:bool = None

class GlulamBeamColumnCSA19(BeamColumn):
    designProps:DesignPropsGlulam19
    
    def __init__(self, member:Member, section:SectionRectangle, 
                 designProps:DesignPropsGlulam19 = None, 
                 userProps:dataclass = None,
                 displayProps:dataclass = None):
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
        
        self._initMain(member, section)

        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if displayProps is None:
            displayProps = DisplayProps(self.member, self.section)

        self._initProps(designProps, userProps, displayProps)
        
    def setLex(self, Lex):
        self.designProps.Lex = Lex
        
    def setLey(self, Ley):
        self.designProps.Ley = Ley       
        
def getBeamColumnGlulamCSA19(L:float, section:SectionRectangle, lUnit:str='m', 
                             firePortection:GypusmRectangleCSA19 = None,
                             Lex:float = None, 
                             Ley:float = None) -> GlulamBeamColumnCSA19:
    """
    A function used to return a beamcolumn based on an input length.
    The beam uses a simply supported elemet by default. If a different type
    of element is required, it should be manually defined with 
    "GlulamBeamColumnCSA19" inatead.
    
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
    
    if firePortection:
        designProps = DesignPropsGlulam19(firePortection)
    else:
        designProps = DesignPropsGlulam19()
    
    if Lex:
        designProps.Lex = Lex
    else:
        designProps.Lex = L
    
    if Ley:
        designProps.Ley = Ley
    else:
        designProps.Ley = L
    
    return GlulamBeamColumnCSA19(member, section, designProps)

@dataclass
class DesignPropsClt19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmFlatCSA19 = None
    fireSection:SectionCLT = None
    Lex:bool = False
    Ley:bool = False
        
    

class CltBeamColumnCSA19(BeamColumn):
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
            displayProps = DisplayProps(self.member, self.section)            
                    
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
        