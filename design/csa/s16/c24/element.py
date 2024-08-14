"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass
from .....objects import (Member, SectionRectangle, initSimplySupportedMember, SectionSteel)

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from limitstates import BeamColumn, DisplayProps

__all__ = ["DesignPropsSteel24", "BeamColumnSteelCSA19"]

@dataclass
class DesignPropsSteel24:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    lateralSupport:bool = True
    Lex:bool = None
    Ley:bool = None

class BeamColumnSteelCSA19(BeamColumn):
    designProps:DesignPropsSteel24
    
    def __init__(self, member:Member, section:SectionSteel, 
                 designProps:DesignPropsSteel24 = None, 
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
            designProps = DesignPropsSteel24()

        # Initialize the design propreties if none are given.        
        if displayProps is None:
            displayProps = DisplayProps(self.member, self.section)

        self._initProps(designProps, userProps, displayProps)
        
    def setLex(self, Lex):
        self.designProps.Lex = Lex
        
    def setLey(self, Ley):
        self.designProps.Ley = Ley       
        
def getBeamColumnSteelCSA19(L:float, section:SectionRectangle, lUnit:str='m', 
                             Lex:float = None, 
                             Ley:float = None) -> BeamColumnSteelCSA19:
    """
    A function used to return a beamcolumn based on an input length.
    The beam uses a simply supported elemet by default. If a different type
    of element is required, it should be manually defined with 
    "BeamColumnGlulamCSA19" inatead.
    
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
    designProps = DesignPropsSteel24()
    
    if Lex:
        designProps.Lex = Lex
    else:
        designProps.Lex = L
    
    if Ley:
        designProps.Ley = Ley
    else:
        designProps.Ley = L
    
    return BeamColumnSteelCSA19(member, section, designProps)
