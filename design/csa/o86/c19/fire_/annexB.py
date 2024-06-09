"""
Contains classes for working with fire design, and modifying sections according
to CSA o86 Annex B
"""

#TODO: add panel once it's complete
from .portection import GypusmFlatCSA19, GypusmRectangleCSA19, _findPortectionType
from ..element import GlulamBeamCSA19

import numpy as np
from numpy import ndarray



# TODO! add panel once it's complete
def AssignFirePortection(element:GlulamBeamCSA19, condition:str, portection:str):
    """
    Assigns the fire portection to an element for some typical conditions.
    These include:
        - beamColumn: exposed on 4 sides
        - beamWithPanel: exposed on all sides except it's top
        - panel: exposed only on it's bottom.
    If the desired condition isn't in the above conditions, a portection object
    will manually have to be created with GypusmRectangleCSA19 or
    GypusmFlatCSA19.

    Parameters
    ----------

    portection : str
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2".
    elementType : str
        The element type to return.
        One of "beamColumn", "beamWithSlab".
        
    Returns
    -------
    None.

    """
    port = _findPortectionType(condition, portection)
    element.designProps.firePortection = port
    
    
# =============================================================================
# 
# =============================================================================

       
def getNetBurnTime(FRR:ndarray, portection:ndarray):
    """
    Given a input FRR demand, determinds the burn time on the section

    Parameters
    ----------
    FRR : ndarray
        An array of the fire time demands in minutes.
    portection : TYPE
        An array of the fire portection times in minutes.

    Returns
    -------
    burnTime : ndarray
        The output demand on the element for each face

    """
    burnTime = FRR - portection
    burnTime[burnTime<0] = 0
    return burnTime


# TODO! add panel once it's complete
def getBurnTimes(element:GlulamBeamCSA19, FRR:list[float]):
    firePort = element.designProps.firePortection.getPortectionTime()
    return getNetBurnTime(np.array(FRR), np.array(firePort))

def getBurntSection(element:GlulamBeamCSA19, FRR:list[float]):
    pass


# TODO! add panel once it's complete
def setBurntSection(element:GlulamBeamCSA19, FRR:list[float]):
    
    if isinstance(element, GlulamBeamCSA19):
        pass
    # elif isinstance(element, BeamColumn):
    #     pass
    else:
        pass
    

def burnSection(netFireTime:ndarray[float], beta:float = 0.7) -> ndarray[float]:
    """
    Calcualtes the amount burned on each face of a section using B.4 and 
    B.5.
    The zero-strength layer is culated according to B5, and uses 7mm or a 
    linear interpolation if the burn time is less than 20min
    Time units are in minutes, length units are in mm.

    Parameters
    ----------
    netFireTime : ndarray
        An array of the input fire time per face.
    beta : TYPE, optional
        The char rate to use, review c.l. B.4.1 to choose. The default is 0.7.

    Returns
    -------
    None.

    """
    
    xn = np.array(list[7]*len(netFireTime))
    
    # if t<20, we don't have to reduce the section by the whole amount.
    xn[netFireTime<20] = netFireTime/20 * xn
    
    return netFireTime*beta + xn