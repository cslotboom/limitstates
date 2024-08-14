"""
Contains functions for managing sections specific to CSAo86-19

Note, right now all limits are calculated at once BEFORE the 
"""

from .element import BeamColumnSteelCSA19, SectionSteel

from typing import Callable


# def _sectionFactory():
"""
!!!
Consider a refactor of the steel design using a factory and intermediate 
design classes.
This can simplify complicated if statements that might develop within functions


"""
class DesignSectionSteel:
    classify:Callable
    checkMrSupported:Callable
    checkMrUnsupported:Callable
    checkPrUnsupported:Callable
    checkInterCaseA:Callable
    checkInterCaseB:Callable
    checkInterCaseC:Callable



def _checkType(sectionType:str):
    SUPPORTEDTYPES = ['W', 'HSS']

    if sectionType.Type not in SUPPORTEDTYPES:
        raise Exception(f'Section of type {sectionType.Type} not supported, expected one of {SUPPORTEDTYPES}')



# =============================================================================
# 
# =============================================================================


def classifySection(section, useX=True, Cf = 0):

    _checkType(section)

    isW = section.Type == 'W'    
    if isW:
        
        cflange = classifyFlangeWSection(section, useX)
        cweb    = classifyWebWSection(section, useX, Cf)
        return max(cflange, cweb)


def classifyFlangeWSection(section:SectionSteel, useX = True):
    
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')
    t   = section.tf
    bel = section.bf / 2
    
    if useX:
        return classifyFlangeW(bel, t, Fy)
    else:
        return classifyFlangeWMinor(bel, t, Fy)
    
def classifyWebWSection(section:SectionSteel, useX = True, Cf:float= 0):
    """
    Classifys a W section web
    
    see #11.3.2.c.
    """
    
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')
    t   = section.tw
    h   = section.d -  section.tf*2
    Cy  = section.Cy
    
    if useX:
        return classifyWebWMajor(h, t, Fy, Cf, Cy)
    else:
        return classifyWebWMinor(h, t, Fy, Cf, Cy)
        
def _categorize(ratio:float, lims:list[float]):

    if ratio <= lims[0]:
        return 1
    elif ratio <= lims[1]:
        return 2
    elif ratio <= lims[2]:
        return 3    
    else:
        return 4

def classifyFlangeW(bel, t, Fy):
    """
    Classify a W section for bending about it's major axis.
    Assumes that the section is supported along one edge.
    """
    
    lim  = 1/Fy**0.5
    lim1 = 145*lim
    lim2 = 170*lim
    lim3 = 250*lim
    ratio = bel / t

    return _categorize(ratio, [lim1, lim2, lim3])

def classifyFlangeWMinor(bel, t, Fy):
    """
    Classify a W section for bending about it's major axis.
    Assumes that the section is supported along one edge.
    """
    
    lim  = 1/Fy**0.5
    lim1 = 145*lim
    lim2 = 170*lim
    lim3 = 340*lim
    ratio = bel / t

    return _categorize(ratio, [lim1, lim2, lim3])

def classifyWebWMajor(h, w, Fy, Cf, Cy):
    """
    Classify a W section for bending about it's major axis.
    Assumes that the section is supported along one edge.
    """
    phi     = 0.9
    ratio   = Cf / (phi*Cy)
    lim     = 1/Fy**0.5

    lim1 = 1100*lim*(1 - 0.39 * ratio)
    lim2 = 1700*lim*(1 - 0.61 * ratio)
    lim3 = 1900*lim*(1 - 0.65 * ratio)

    return _categorize(h/w, [lim1, lim2, lim3])


def classifyWebWMinor(h, w, Fy, Cf, Cy):
    """
    Classify a W section for bending about it's major axis.
    Assumes that the section is supported along one edge.
    """
    phi     = 0.9
    ratio   = Cf / (phi*Cy)

    if Cf == 0:
        useCaseA = False
    else:
        # Rearrange 0.4*phi*Cy < Cf
        useCaseA = 0.4*ratio**-1 < 1    
    
    lim  = 1/Fy**0.5
    if useCaseA:
        lim1 = 525*lim
        lim2 = 525*lim
        lim3 = 1900*lim*(1 - 0.65 * ratio)
    else:
        lim1 = 1100*lim*(1 - 1.31 * ratio)
        lim2 = 1700*lim*(1 - 1.73 * ratio)
        lim3 = 1900*lim*(1 - 0.65 * ratio)

    return _categorize(h/w, [lim1, lim2, lim3])


def classifyHSSRect(bel, t, Fy):
    """
    Classify a W section for bending about it's major axis.
    Assumes that the section is supported along one edge.
    """
    
    lim = 1/Fy**0.5
    lim1 = 420*lim
    lim2 = 525*lim
    lim3 = 670*lim
    
    ratio = bel / t

    return _categorize(ratio, [lim1, lim2, lim3])
    



# =============================================================================
# Moment
# =============================================================================

def getMpSupported(Z, Fy):
    """
    Assumes Z and Fy are in mm3 and MPa
    Returns in Nmm
    """
    
    phi = 0.9
    return Z*Fy*phi
    
def getMySupported(S, Fy):
    """
    Assumes Z and Fy are in mm3 and MPa
    Returns in Nmm
    """
    
    phi = 0.9
    return S*Fy*phi
    
def getSectionMrSupported(section:SectionSteel, useX=True, Cf = 0):
    """
    Calcualtes Mr for a supported member in Nm
    """
    _checkType(section)
    
    sectionClass = classifySection(section, useX, Cf)
    Fy = section.mat.Fy * section.mat.sConvert('MPa')
    
    if sectionClass <=2:
        Z = section.getZ(useX, 'mm')
        return getMpSupported(Z, Fy) / 1000
    elif sectionClass <=3:
        S = section.getS(useX, 'mm')
        return getMySupported(S, Fy) / 1000
    else:
        raise Exception(f'{section} recieved is class 4, limitstates currently cannot design class 4 sections.')
    
    

