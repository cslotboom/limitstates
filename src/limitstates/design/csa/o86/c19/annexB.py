"""
Contains classes for working with fire design, and modifying sections according
to CSA o86 Annex B.
"""

#TODO: add panel once it's complete
from .....objects import BeamColumn, SectionRectangle, SectionCLT, LayerClt, LayerGroupClt
from .....objects.fireportection import FirePortection
from .fireportection import GypusmFlatCSA19, GypusmRectangleCSA19
from .element import BeamColumnGlulamCsa19, BeamColumnCltCsa19
from enum import IntEnum

import numpy as np
from numpy import ndarray
from copy import deepcopy

# __all__ = ["FireConditions", "getFireDemands", "getGypsumFirePortection", "AssignFirePortection","getNetBurnTime",
#            "getBurntRectangularDims", "getBurntRectangularSection", "setFireSectionGlulamCSA"]

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

def getBurntRectangularDims(burnAmount, width:float, 
                            depth:float):
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
    burnAmount : nd.Array
        The amount each face is burned.
    width : float
        The input section width as a float.
    depth : float
        The input section depth as a float.

    Returns
    -------
    fireWidth: float
        The width of the fire section.
    fireWidth: float
        The depth of the fire section.
    """
    
    wfire = max(width - sum(burnAmount[1::2]),0)
    dfire = max(depth - sum(burnAmount[0::2]),0)
    return wfire, dfire

def getCLTBurnDims(netBurnTime:ndarray[float], sectionCLT:SectionCLT, Bn:float = 0.8):
    """
    Gets the burn dimensions for a CLTSection. 
    The CLT section MUST have units of mm.
    
    Calculates the amount burned on each face of a section using clauses B.4 
    and B.5.
    
    The zero-strength layer is culated according to B5, and uses 7mm or a 
    linear interpolation if the burn time is less than 20min
    Time units are in minutes, length units are in mm.
    

    Parameters
    ----------
    netBurnTime : float
        The burn time on each face in minutes.
        This is a ndarray with one entry in it for compatibility purposes.
    width : float
        The input section width as a float.
    depth : float
        The input section depth as a float.
    Bn : float, optional
        The char rate for the section. The default is 0.8.

    Returns
    -------
    fireWidth: float
        The width of the fire section.
    fireWidth: float
        The depth of the fire section.
    """
    
    burnAmount = float(getBurnDimensions(netBurnTime, Bn))
    burntLayers = _getRemainingCLTLayers(sectionCLT, burnAmount)

    return burntLayers



def _getRemainingCLTLayers(sectionCLT:SectionCLT, burnAmount):
    """
    Creates a set of burnt CLT layers. Assumes the section and burnt amount
    have the same units.
    """
    
    ii = 0
    # !!!: assumes that the strong axis layers are alwyas the full layer group.
    layers = sectionCLT.sLayers
    Nlayer = len(layers)
    intLayer = None
    
    # Iterate through layers starting at the bottom.
    for layer in layers[::-1]:
        burnAmount -= layer.t
        if burnAmount <= 0:
            t = abs(burnAmount)
            intLayer = LayerClt(t, layer.mat, layer.parallelToStrong, layer.lUnit)
            ii += 1
            break
        else:
            ii += 1
    end = Nlayer - ii
    outputLayers = deepcopy(layers[:end])
    
    # If there are no layers, add on empty layer so the layer group can still do stuff
    if end == 0:
        layer = layers[0]
        outputLayers = [LayerClt(0, layer.mat, layer.parallelToStrong, layer.lUnit)]
    
    # If there is an intermediate layer, return a 
    if intLayer:
        outputLayers.append(intLayer) 
            
    return LayerGroupClt(outputLayers)


# =============================================================================
# 
# =============================================================================

def _convertUnits(section):
    convertBack = False
    oldUnits = 'mm'
    if section.lUnit != 'mm':
        convertBack = True
        oldUnits = section.lUnit
        section.convertUnits('mm')
    return convertBack, oldUnits

def _convertBack(section, burnSection,  oldUnits):
    section.convertUnits(oldUnits)
    burnSection.convertUnits(oldUnits)

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
    burnAmount: list[float]
        An array of what is burned on each face.
    """
    portectionTime = portection.getPortectionTime()
    netBurnTime = getNetBurnTime(FRR, portectionTime)
    
    # If section not in mm, convert to mm then convert back later.
    convertBack, oldUnits = _convertUnits(section)
    
    burnAmount = getBurnDimensions(netBurnTime, Bn)
    burnDimensions = getBurntRectangularDims(burnAmount, section.b, section.d)
    burnSection = SectionRectangle(section.mat, *burnDimensions, section.lUnit)
    
    # Convert the section back to mm.
    if convertBack:
        _convertBack(section, burnSection, oldUnits)
    
    return burnSection, burnAmount

def getBurntCLTSection(section:SectionCLT, FRR:ndarray[float], 
                       portection:GypusmFlatCSA19, 
                       Bn:float = 0.8) -> SectionCLT:
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
    convertBack, oldUnits = _convertUnits(section)

    # make the new section and convert it to 
    burnLayers = getCLTBurnDims(netBurnTime, section, Bn)
    burnSection = SectionCLT(burnLayers, section.w, section.wWeak, 
                             section.lUnit, section.NlayerTotal)
    
    # Convert the section back to mm.
    if convertBack:
        _convertBack(section, burnSection, oldUnits)
    
    return burnSection


# =============================================================================
# User functions
# =============================================================================
"""
The majority of functions exposed to the user are in this section.
"""

def getFRRfromFireConditions(FRR:float, fireCon:FireConditions = 2):
    """
    A helper function used to get the appropriate FRR list from a set of 
    typical conditions.
    """
    
    if fireCon == FireConditions.beamWithPanel:
        FRR = np.array([0,FRR,FRR,FRR])
    elif fireCon == FireConditions.beamColumn:
        FRR = np.array([FRR,FRR,FRR,FRR])
    else:
        vals = [e.value for e in FireConditions]
        raise Exception(f'recieved {fireCon}, expected one of {vals} from FireConditions Enum')
        
    return FRR

def setFireSectionGlulamCSA(element:BeamColumnGlulamCsa19, 
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
    element : BeamColumnGlulamCsa19
        The Glulam element to burn.
    FRR : list[float]|ndarray[float]
        For a rectangular section fire portection is input 
        in: [top, right, bottom, left]  
    Bn : float, optional
        The burn rate for the section. 
        The default is 0.7, which is the notional char rate.
    fireCondition : FireConditions
        The fire condition used. See the FireConditions enumeration for 
        possible values

    """
    
    section = element.section
    firePort = element.designProps.firePortection
    
    if isinstance(FRR, list):
        FRR = np.array(FRR)
    
    # If the section is not set, assume the beam is exposed.
    if not firePort:
        firePort = GypusmRectangleCSA19('exposed')
            
    sectionFire, burnDims = getBurntRectangularSection(section, FRR, firePort)
    element.setSectionFire(sectionFire, burnDims)    

def setFireSectionCltCSA(element:BeamColumnGlulamCsa19, 
                         FRR:float|list[float]|ndarray[float],
                         Bn:float = 0.8):
    """
    Sets the burnt section for a clt element.
    By default Bn = 0.8, which assumes that the first CLT layer has been 
    burnt through. Set Bn = 0.65 if the bottom layer isn't burnt through. 
    
    Calculates the amount burned on each face of a section using clauses B.4 and 
    B.5.
    The zero-strength layer is calculated according to B5, and uses 7mm or a 
    linear interpolation if the exposed time is less than 20min.
    
    Time units is in minutes.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
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
        firePort = GypusmFlatCSA19('exposed')
    
    if isinstance(FRR, int) or isinstance(FRR, float):
        FRR = np.array([FRR])
    
    sectionFire = getBurntCLTSection(section, FRR, firePort, Bn)    
    # fireSection.NlayerTotal = len(section.sLayers)
    # element.designProps.sectionFire = sectionFire
    element.setSectionFire(sectionFire)    





# TODO! add panel once it's complete
def setBurntSection(element:BeamColumnGlulamCsa19, 
                    FRR:float|list[float]|ndarray[float], 
                    Bn:float = 0.7):
    
    if isinstance(element, BeamColumnGlulamCsa19):
        setFireSectionGlulamCSA(element, FRR, Bn)
    elif isinstance(element, BeamColumn):
        setFireSectionGlulamCSA(element, FRR, Bn)
    elif isinstance(element, BeamColumnCltCsa19):
        setFireSectionCltCSA(element, FRR, Bn)
    





    