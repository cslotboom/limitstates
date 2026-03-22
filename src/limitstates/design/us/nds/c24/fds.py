"""
Contains classes for working with fire design, and modifying sections according
to CSA o86 Annex B.
"""

from typing import Union
import numpy as np
from numpy import ndarray
from copy import deepcopy

from limitstates.design.common.fire import exposureConditons, FireConditions, getFireDemands

from .....objects import BeamColumn, SectionRectangle, SectionCLT, LayerClt, LayerGroupClt
from .....objects.fireportection import FirePortection
from .fireportection import GypusmFlatNds24, GypusmRectangleNds24
from .element import BeamColumnGlulamNds24, BeamColumnCltCsa19


# =============================================================================
# Constants
# =============================================================================

kfi = {'timber':1.5, 'glulam':1.35, 'cltE':1.25, 'cltV':1.5, 'SCL':1.25 }
kdfi = 1.15
beta0 = 0.65
betaN = 1.5  # Char rate in mm

def _findPortectionType(condition: FireConditions, portection: str):
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
        return GypusmRectangleNds24(portection)
    elif condition == FireConditions.beamWithPanel:
        return GypusmRectangleNds24(['exposed', portection, portection, portection])
    elif condition == FireConditions.panel:
        return GypusmFlatNds24(portection)
    else:
        raise Exception(f'Recived condition {condition}, expected one of {exposureConditons}')


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
    portection : FireConditions, str
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    Returns
    -------
    None.

    """
    return _findPortectionType(condition, portection)

def AssignFirePortection(element: BeamColumn, condition: FireConditions, portection: str):
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
    
def getNetBurnTime(FRR: ndarray, portection: ndarray) -> ndarray[float]:
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

def getBurnDimensions(netFireTime: ndarray[float], 
                      Bn0: float = 1.5) -> ndarray[float]:
    """
    Calcualtes the amount burned on each face of a section using c.l. 3.2.

    Time units are in minutes, length units are in inch.

    For a rectangular section fire portection is input 
    in: [top, right, bottom, left]  

    Parameters
    ----------
    netFireTime : ndarray
        An array of the input fire time per face in minutes.
    Bn : float, optional
        The 1hr nominal char rate to use in in/hour. 
        Has default value of 1.5 inch/hour, see FDS c.l. 3.2.1

    Returns
    -------
    faceBurn : ndarray
        An array storing the amount of burn on each face of the element.
    .

    """
    
    netFireTimeHours = (netFireTime / 60)
    return 1.2*netFireTimeHours**0.813*Bn0

def getBurntRectangularDims(burnAmount, width:float, 
                            depth:float):
    """
    Gets the burn dimensions for a rectangle from a input burn time. Burn time
    is input in: [top, right, bottom, left]  
    
    Calcualtes the amount burned on each face of a section using c.l. 3.2.

    Time units are in minutes, length units are in inch.

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

def getCLTBurnDims(netBurnTime: ndarray[float], 
                   sectionCLT: SectionCLT, 
                   Bn:float = 0.8) -> LayerGroupClt:
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
    burnLayers: float
        The width of the fire section.
    fireWidth: float
        The depth of the fire section.
    """
    
    burnAmount = getBurnDimensions(netBurnTime, Bn)
    burnLayers = _getRemainingCLTLayers(sectionCLT, float(burnAmount))

    # burnSection = SectionCLT(burnLayers, section.w, section.wWeak, 
    #                          section.lUnit, section.NlayerTotal)
    return burnLayers



def _getRemainingCLTLayers(sectionCLT:SectionCLT, burnAmount):
    """
    Creates a set of burnt CLT layers. Assumes the section and burnt amount
    have the same units.
    """
    
    ii = 0
    # !!!: assumes that the strong axis layers are always the full layer group.
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
    oldUnits = 'in'
    if section.lUnit != 'in':
        convertBack = True
        oldUnits = section.lUnit
        section.convertUnits('in')
    return convertBack, oldUnits

def _convertBack(section, burnSection,  oldUnits):
    section.convertUnits(oldUnits)
    burnSection.convertUnits(oldUnits)

def getBurntRectangularSection(section:SectionRectangle, FRR:ndarray[float], 
                               portection:GypusmRectangleNds24, 
                               Bn:float = 1.5) -> SectionRectangle:
    """
    Returns a burnt rectangular section, with burn dimensions for a rectangle 
    from a input burn time.
    
    Calcualtes the amount burned on each face of a section using c.l. 3.2.

    Time units are in minutes, length units are in inch.

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
        The 1hr nominal char rate to use in in/hour. 
        Has default value of 1.5 inch/hour, see FDS c.l. 3.2.1

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
        cfactor = section.lConvert('mm')
        burnAmount *= cfactor
    
    return burnSection, burnAmount

def getBurntCLTSection(section:SectionCLT, FRR:ndarray[float], 
                       portection:GypusmFlatNds24, 
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
    burnAmount = getBurnDimensions(netBurnTime, Bn)
    burnLayers = _getRemainingCLTLayers(section, float(burnAmount))

    burnSection = SectionCLT(burnLayers, section.w, section.wWeak, 
                             section.lUnit, section.NlayerTotal)
    
    # Convert the section back to mm.
    
    if convertBack:
        _convertBack(section, burnSection, oldUnits)
        cfactor = section.lConvert('mm')
        burnAmount *= cfactor

    return burnSection, burnAmount


# =============================================================================
# User functions
# =============================================================================
"""
The majority of functions exposed to the user are in this section.
"""

def setFireSectionGlulamNDS(element:BeamColumnGlulamNds24, 
                            FRR:Union[list[float],ndarray[float]],
                            Bn:float = 1.5):
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
    FRR : list[float], ndarray[float]
        For a rectangular section fire portection is input 
        in: [top, right, bottom, left]  
    Bn : float, optional
        The 1hr nominal char rate to use in in/hour. 
        Has default value of 1.5 inch/hour, see FDS c.l. 3.2.1
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
        firePort = GypusmRectangleNds24('exposed')
            
    sectionFire, burnDims = getBurntRectangularSection(section, FRR, firePort)
    element.setSectionFire(sectionFire, burnDims)    


# TODO: this needs to updated when we do walls.
def setFireSectionCltCSA(element:BeamColumnCltCsa19, 
                         FRR:Union[float, list[float], ndarray[float]],
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
    FRR : list[float],ndarray[float]
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
        firePort = GypusmFlatNds24('exposed')
    
    if isinstance(FRR, int) or isinstance(FRR, float):
        FRR = np.array([FRR])
    
    sectionFire, burnAmount = getBurntCLTSection(section, FRR, firePort, Bn)    
    # fireSection.NlayerTotal = len(section.sLayers)
    # element.designProps.sectionFire = sectionFire
    element.setSectionFire(sectionFire, burnAmount)    





    