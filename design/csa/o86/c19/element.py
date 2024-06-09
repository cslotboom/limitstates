"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from .....objects import Line, SectionRectangle, getLineFromLength
from .material import MaterialGlulamCSA19
from limitstates import BeamColumn
#need to input directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19 

__all__ = ["GlulamBeamCSA19", "getBeamColumnGlulamCSA19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmRectangleCSA19 = None
    fireSection:SectionRectangle = None
    

class GlulamBeamCSA19(BeamColumn):
    designProps:DesignPropsGlulam19
    
    def __init__(self, line:Line, section:SectionRectangle, lUnit:str='m', 
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
            a empty DesignPropsGlulam19 object
        userProps : dataclass, optional
            The user design opreties. The default is None, which creates an
            empty dataclass by default.

        Returns
        -------
        None.

        """
        
        
        self._initMain(line, section, lUnit)
        self._initUserProps(userProps)
        
        if designProps is None:
            designProps = DesignPropsGlulam19()
        self.designProps = designProps
        
def getBeamColumnGlulamCSA19(L:float, section:SectionRectangle, lunit:str, 
                             FRR = None, firePortection = None) -> BeamColumn:
    """
    A function used to return a beamcolumn based on an input length

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
    line = getLineFromLength(L, lunit)

    
    return GlulamBeamCSA19(line, section, lunit)
