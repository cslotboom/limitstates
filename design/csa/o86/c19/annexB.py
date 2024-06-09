"""
Contains classes for working with fire design, and modifying sections according
to CSA o86 Annex B
"""

#TODO: add panel once it's complete
from .....objects import BeamColumn, SectionRectangle
from .....objects.fireportection import FirePortection
from .fireportection import GypusmFlatCSA19, GypusmRectangleCSA19
from .element import GlulamBeamCSA19

import numpy as np
from numpy import ndarray


__all__ = ["getGypsumFirePortection", "AssignFirePortection","getNetBurnTime",
           "getBurntRectangularDims"]


# =============================================================================
# Constants
# =============================================================================


kfi = {'timber':1.5, 'glulam':1.35, 'cltE':1.25, 'cltV':1.5, 'SCL':1.25 }
kdfi = 1.15
beta0 = 0.65
betaN = {'timber':0.8, 'glulam':0.7, 'clt':0.8,'SCL':0.7 }



_exposureConditons = ["beamColumn", "beamWithPanel", "panel"]


def getFireDemands(FRR, condition):
    """
    A helper function used to returns the fire demands for common fire 
    conditions
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

    if condition == "beamColumn":
        return [FRR, FRR, FRR, FRR]
    elif condition == "beamWithPanel":
        return [FRR, FRR, FRR, 0]
    elif condition == "panel":
        return [FRR]
    else:
        raise Exception(f'Recived condition {condition}, expected one of {_exposureConditons}')




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
        return GypusmRectangleCSA19([portection, portection, portection, 'unexposed'])
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






# TODO! add panel once it's complete
def AssignFirePortection(element:BeamColumn, condition:str, portection:str):
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

       
def getNetBurnTime(FRR:ndarray, portection:ndarray) -> ndarray[float]:
    """
    Given a input FRR demand and portection time, determines the burn 
    time on the section.
    
    Parameters
    ----------
    FRR : ndarray
        An array of the fire resistant rating demands in minutes.
    portection : ndarray
        An array of the fire portection times in minutes.

    Returns
    -------
    burnTime : ndarray
        The output demand on the element for each face

    """
    burnTime = FRR - portection
    burnTime[burnTime<0] = 0
    return burnTime


def getBurnDimensions(netFireTime:ndarray[float], Bn:float = 0.7) -> ndarray[float]:
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
    Bn : TYPE, optional
        The char rate to use, review c.l. B.4.1 to choose. The default is 0.7.

    Returns
    -------
    None.

    """
    
    xn = np.array([7]*len(netFireTime))
    
    # if t<20, we don't have to reduce the section by the whole amount.
    inds = np.where(netFireTime<20)[0]
    xn[inds] = (netFireTime/20 * xn)[inds]
    
    burnAmount = netFireTime*Bn + xn
    return burnAmount



def getBurntRectangularDims(netBurnTime, width:float, depth:float, Bn:float = 0.7):
    """
    Gets the burn dimensions for a rectangle from a inut burn time.
    
    Calcualtes the amount burned on each face of a section using B.4 and 
    B.5.
    The zero-strength layer is culated according to B5, and uses 7mm or a 
    linear interpolation if the burn time is less than 20min
    Time units are in minutes, length units are in mm.
    

    Parameters
    ----------
    netBurnTime : nd.Array
        The burn time on each face in minutes.
    width : float
        The input section width as a float.
    depth : float
        The input section depth as a float.
    Bn : float, optional
        The char rate for the section. The default is 0.7.

    Returns
    -------
    fireWidth: float
        The width of the fire section.
    fireWidth: float
        The depth of the fire section.
    """
    
    burnDimensions = getBurnDimensions(netBurnTime, Bn)
    return width - sum(burnDimensions[::2]), depth - sum(burnDimensions[1::2])




def getBurntRectangularSection(section:SectionRectangle, FRR:ndarray[float], 
                    portection:GypusmRectangleCSA19, 
                    burnRate:float = 0.7):
    
    netBurnTime = getNetBurnTime(FRR, portection)
    burnDimensions = getBurnDimensions(netBurnTime, )
    



# TODO! add panel once it's complete
def getBurnTimes(element:GlulamBeamCSA19, FRR:list[float]):
    firePort = element.designProps.firePortection.getPortectionTime()
    return getNetBurnTime(np.array(FRR), np.array(firePort))

def getBurntSectionRectangle(element:BeamColumn, FRR:list[float]):
    pass
    


# TODO! add panel once it's complete
def setBurntSection(element:BeamColumn, FRR:list[float]):
    
    if isinstance(element, GlulamBeamCSA19):
        pass
    elif isinstance(element, BeamColumn):
        pass
    else:
        pass
    







    