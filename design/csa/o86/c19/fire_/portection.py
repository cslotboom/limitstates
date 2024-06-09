"""
Contains fire portection objects that represent gypsum
"""

#TODO: add panel once it's complete
from ......objects import BeamColumn, SectionRectangle
from ......objects.fireportection import FirePortection
# from .element import GlulamBeamCSA19

import numpy as np
from numpy import ndarray


__all__ = ["GypusmFlatCSA19", "GypusmRectangleCSA19"]

# =============================================================================
# Constants
# =============================================================================

firePortectionOptions = {'exposed':0, '12.7mm':15, '15.9mm':30, '15.9mmx2':60,
                         'unexposed':1e6}
_exposureConditons = ["beamColumn", "beamWithPanel", "panel"]


class GypusmFlatCSA19(FirePortection):
    Nside:int = 1    
    portectionTypes:dict = firePortectionOptions
    
    def __init__(self, portection: list[str] | str ):
        """
        Represents fire portection that goes on a section that has only one 
        side, such as the bottom of a CLT panel, or a circular column.

        Parameters
        ----------
        portection : list[str]
            The input list of fire portection.

        Returns
        -------
        None.

        """
        if isinstance(portection, str):
            portection = [portection]
        
        self._validateInput(portection)
        self.portection = portection
        self.setPortectionTime()
    
    def __repr__(self):
        return f"<limitstates gypsum fire port. {self.portection}>"

class GypusmRectangleCSA19(FirePortection):
    Nside:int = 4
    portectionTypes:dict = firePortectionOptions

    def __init__(self, portection:list[str] | str ):
        """
        Represents fire portection that goes on a section with multiple sides.
        Each side is given it's own potection. Convention is to start at the 
        'right' side.
        For a rectangular section fire portection is input in, 
        [right, bottom, left, top]

        Parameters
        ----------
        portection : list[str]
            The input list of fire portection.

        Returns
        -------
        None.

        """        
        
        if len(portection) == 1:
            portection = portection*4
        elif isinstance(portection, str):
            portection = [portection]*4
        self._validateInput(portection)
        
        self.portection = portection
        self.setPortectionTime()

    def __repr__(self):
        return f"<limitstates gypsum fire port. {self.portection}>"
        
def _findPortectionType(condition:str, portection:str):
    """
    Parameters
    ----------
    elementType : str
        The condition of the element from a list of typical conditions.
        One of "beamColumn", "beamWithPanel", "panel".
    portection : str
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    """
    if condition == "beamColumn":
        return GypusmRectangleCSA19(portection)
    elif condition == "beamWithPanel":
        return GypusmRectangleCSA19([portection, portection, portection, 'exposed'])
    elif condition == "panel":
        return GypusmFlatCSA19(portection)
    else:
        raise Exception(f'Recived condition {condition}, expected one of {_exposureConditons}')


def getGypsumFirePortection(condition:str, 
                            portection:str) -> FirePortection:
    """
    Returns the fire portection class for some typical conditions.
    These include:
        - beamColumn: exposed on 4 sides
        - beamWithPanel: exposed on all sides except it's top
        - panel: exposed only on it's bottom.
    If the desired condition isn't in the above conditions, a portection object
    will manually have to be created with GypusmRectangleCSA19 or
    GypusmFlatCSA19.

    Parameters
    ----------
    condition : str
        The condition of the element from a list of typical conditions.
        One of "beamColumn", "beamWithPanel", "panel".
    portection : str
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    Returns
    -------
    None.

    """
    return _findPortectionType(condition, portection)
