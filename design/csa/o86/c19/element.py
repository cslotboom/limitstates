"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from .....objects import Member, SectionRectangle, initSimplySupportedMember
#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19 
from limitstates import BeamColumn

__all__ = ["GlulamBeamColumnCSA19", "getBeamColumnGlulamCSA19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmRectangleCSA19 = None
    fireSection:SectionRectangle = None
    lateralSupport:bool = True
    isCurved:bool = False
    Lex:bool = False
    Ley:bool = False
    

class GlulamBeamColumnCSA19(BeamColumn):
    designProps:DesignPropsGlulam19
    
    def __init__(self, member:Member, section:SectionRectangle, lUnit:str='m', 
                 designProps:DesignPropsGlulam19 = None, 
                 userProps:dataclass = None):
        """
        Design propreties for a glulam beam element.

        Parameters
        ----------
        line : Line
            The line used.
        section : SectionRectangle
            The section used.
        lUnit : str, optional
            the units used. The default is 'm'.
        designProps : DesignPropsGlulam19, optional
            The inital design propreties. The default is None, which creates 
            a empty DesignPropsGlulam19 object.
        userProps : dataclass, optional
            The user design opreties. The default is None, which creates an
            empty dataclass by default.

        Returns
        -------
        None.

        """
        
        
        self._initMain(member, section)
        self._initUserProps(userProps)
        
        if designProps is None:
            designProps = DesignPropsGlulam19()
        self.designProps = designProps
        
        
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
    default values are assigned to design propreties.

    Parameters
    ----------
    L : float
        The input length for the beamcolumn.
    section : SectionAbstract
        The section the beamcolumn ises.
    lunit : str
        the units for the input length.
    designProps : dict, optional
        Additional design propreties the section will use. The default is None.

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
    
    return GlulamBeamColumnCSA19(member, section, lUnit, designProps)
