"""
Contains classes for working with fire design, and modifying sections according
to CSA o86 Annex B.
"""

#TODO: add panel once it's complete
from .....objects import BeamColumn, SectionRectangle
from .....objects.fireportection import FirePortection
from .fireportection import GypusmFlatCSA19, GypusmRectangleCSA19
from .element import GlulamBeamColumnCSA19
from enum import IntEnum

import numpy as np
from numpy import ndarray


__all__ = ["FireConditions", "getFireDemands", "getGypsumFirePortection", "AssignFirePortection","getNetBurnTime",
           "getBurntRectangularDims", "getBurntRectangularSection", "setFireSectionGlulamCSA"]

# =============================================================================
# Constants
# =============================================================================

kfi = {'timber':1.5, 'glulam':1.35, 'cltE':1.25, 'cltV':1.5, 'SCL':1.25 }
kdfi = 1.15
beta0 = 0.65
betaN = {'timber':0.8, 'glulam':0.7, 'clt':0.8,'SCL':0.7 }

_exposureConditons = ["beamColumn", "beamWithPanel", "panel"]
class FireConditions(IntEnum):
    """
    A class that shows all possible options for fire conditions.
    These include:
        - 1 = beamColumn: exposed on 4 sides
        - 2 = beamWithPanel: exposed on all sides except it's top
        - 3 = panel: exposed only on it's bottom.
    """
    beamColumn = 1
    beamWithPanel = 2
    panel = 3


def getFireDemands(FRR:float, condition:FireConditions|int) :
    """
    A helper function used to returns the fire demands for common fire 
    conditions. These include:
        - 1 = beamColumn: exposed on 4 sides
        - 2 = beamWithPanel: exposed on all sides except it's top
        - 3 = panel: exposed only on it's bottom.
    
    A list can manually be created for the the FRR if the above options do not
    match the input conditions above.
    
    Parameters
    ----------
    condition : str
        The condition of the element from a list of typical conditions.
        The FireCondition Enumeration class can be used, or an integer.
    portection : FireConditions, int
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    Returns
    -------
    FRR : list
        The output FRR. For a rectangular section fire portection is input 
        in: [top, right, bottom, left]    

    
    """

    if condition == FireConditions.beamColumn:
        return [FRR, FRR, FRR, FRR]
    elif condition == FireConditions.beamWithPanel:
        return [0, FRR, FRR, FRR]
    elif condition == FireConditions.panel:
        return [FRR]
    else:
        raise Exception(f'Recived condition {condition}, expected one of {_exposureConditons}')


def _findPortectionType(condition:FireConditions, portection:str):
    """
    Parameters
    ----------
    condition : str
        The condition of the element from a list of typical conditions.
        The FireCondition Enumeration class can be used, or an integer.
    portection : FireConditions, int
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    """
    if condition == FireConditions.beamColumn:
        return GypusmRectangleCSA19(portection)
    elif condition == FireConditions.beamWithPanel:
        return GypusmRectangleCSA19(['exposed', portection, portection, portection])
    elif condition == FireConditions.panel:
        return GypusmFlatCSA19(portection)
    else:
        raise Exception(f'Recived condition {condition}, expected one of {_exposureConditons}')


def getGypsumFirePortection(condition:FireConditions, 
                            portection:str) -> FirePortection:
    """
    Returns the fire portection class for some typical conditions.
    These include:
        - 1 = beamColumn: exposed on 4 sides
        - 2 = beamWithPanel: exposed on all sides except it's top
        - 3 = panel: exposed only on it's bottom.
    If the desired condition isn't in the above conditions, a portection object
    will manually have to be created with GypusmRectangleCSA19 or
    GypusmFlatCSA19.

    Parameters
    ----------
    condition : str
        The condition of the element from a list of typical conditions.
        The FireCondition Enumeration class can be used, or an integer.
    portection : FireConditions, int
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    Returns
    -------
    None.

    """
    return _findPortectionType(condition, portection)

# TODO! add panel once it's complete
def AssignFirePortection(element:BeamColumn, condition:FireConditions, portection:str):
    """
    Assigns the fire portection to an element for some typical conditions.
    These include:
        - 1 = beamColumn: exposed on 4 sides
        - 2 = beamWithPanel: exposed on all sides except it's top
        - 3 = panel: exposed only on it's bottom.
    If the desired condition isn't in the above conditions, a portection object
    will manually have to be created with GypusmRectangleCSA19 or
    GypusmFlatCSA19.

    Parameters
    ----------
    element : object
        The element to assign fire portection to.
    condition : str
        The condition of the element from a list of typical conditions.
        The FireCondition Enumeration class can be used, or an integer.
    portection : str
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2".
        
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
    
    For a rectangular section fire portection is input 
    in: [top, right, bottom, left]  
    
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

def getBurnDimensions(netFireTime:ndarray[float], 
                      Bn:float = 0.7) -> ndarray[float]:
    """
    Calcualtes the amount burned on each face of a section using B.4 and 
    B.5.
    The zero-strength layer is culated according to B5, and uses 7mm or a 
    linear interpolation if the burn time is less than 20min
    Time units are in minutes, length units are in mm.

    For a rectangular section fire portection is input 
    in: [top, right, bottom, left]  

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

def getBurntRectangularDims(netBurnTime:ndarray[float], width:float, 
                            depth:float, Bn:float = 0.7):
    """
    Gets the burn dimensions for a rectangle from a input burn time. Burn time
    is input in: [top, right, bottom, left]  
    
    Calculates the amount burned on each face of a section using clauses B.4 
    and B.5.
    
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
    wfire = max(width - sum(burnDimensions[1::2]),0)
    dfire = max(depth - sum(burnDimensions[0::2]),0)
    return wfire, dfire

def getBurntRectangularSection(section:SectionRectangle, FRR:ndarray[float], 
                               portection:GypusmRectangleCSA19, 
                               Bn:float = 0.7) -> SectionRectangle:
    """
    Returns a burnt rectangular section, with burn dimensions for a rectangle 
    from a input burn time.
    
    Calculates the amount burned on each face of a section using clauses B.4 
    and B.5.
    The zero-strength layer is calculated according to B5, and uses 7mm or a 
    linear interpolation if the exposed time is less than 20min
    Time units are in minutes.
    

    Parameters
    ----------
    section : SectionRectangle
        The input rectangular section to burn.
    FRR : ndarray[float]
        The burn demands in FRR in minutes on each face. For a rectangular 
        section fire portection is input in: [top, right, bottom, left]    
    portection : GypusmRectangleCSA19
        The fire portection object applied to the section.
    Bn : float, optional
        The char rate for the section. 
        The default is 0.7, which is the notional char rate.

    Returns
    -------
    SectionRectangle
        The burn section with dimensions equal to the output section.
    """
    portectionTime = portection.getPortectionTime()
    netBurnTime = getNetBurnTime(FRR, portectionTime)
    
    # If section not in mm, convert to mm then convert back later.
    
    convertBack = False
    if section.lUnit != 'mm':
        convertBack = True
        oldUnits = section.lUnit
        section.convertUnits('mm')
    
    burnDimensions = getBurntRectangularDims(netBurnTime, section.b, section.d, Bn)
    burnSection = SectionRectangle(section.mat, *burnDimensions, section.lUnit)
    burnSection.designProps = section.designProps
    
    # Convert the section back to mm.
    if convertBack:
        section.convertUnits(oldUnits)
        burnSection.convertUnits(oldUnits)
    
    return burnSection


# =============================================================================
# User functions
# =============================================================================
"""
The majority of functions exposed to the user are in this section.
"""

def setFireSectionGlulamCSA(element:GlulamBeamColumnCSA19, 
                            FRR:list[float]|ndarray[float],
                            Bn:float = 0.7):
    """
    Sets the burnt section for a glulam element.
    If the element does not have fire portection assigned to it, it is assumed
    that the section has no fire portection on all sides.
    
    Calculates the amount burned on each face of a section using clauses B.4 and 
    B.5.
    The zero-strength layer is calculated according to B5, and uses 7mm or a 
    linear interpolation if the exposed time is less than 20min.
    
    Time units is in minutes.

    Parameters
    ----------
    element : GlulamBeamColumnCSA19
        The Glulam element to burn.
    FRR : list[float]|ndarray[float]
        For a rectangular section fire portection is input 
        in: [top, right, bottom, left]  
    Bn : float, optional
        The burn rate for the section. 
        The default is 0.7, which is the notional char rate.

    Returns
    -------
    None.

    """
    
    section = element.section
    firePort = element.designProps.firePortection
    
    # If the section is not set, assume the beam is exposed.
    if not firePort:
        firePort = GypusmRectangleCSA19(0)
    
    fireSection = getBurntRectangularSection(section, FRR, firePort)    
    firePort = element.designProps.fireSection = fireSection



# TODO! add panel once it's complete
def setBurntSection(element:GlulamBeamColumnCSA19, FRR:list[float], ):
    
    if isinstance(element, GlulamBeamColumnCSA19):
        pass
    elif isinstance(element, BeamColumn):
        pass
    else:
        pass
    





    