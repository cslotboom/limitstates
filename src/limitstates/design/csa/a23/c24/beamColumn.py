"""
Contains the code designc clauses
"""
from numpy import pi, diff, cumsum
from enum import IntEnum

import numpy as np

from .element import BeamColumnConcreteCsa24  
from limitstates import DesignDiagram, SectionConcrete


phiC = 0.65
phiS = 0.85


    
def getEndStrain(d:float, NAtrial:float, eConc:float):

    """    
    Returns the strain at the "bottom" of the section, assuming a linear strain
    distribution. Linear interpolation is used to calculate strain at the 
    bottom position (d).
    The section is assume to have a strain of eConc at it's top
    The bottom strain is assumed to have the opposite sign as eConc, i.e. it
    is in tension.

    Parameters
    ----------
    d : float
        The distance to the end of the beam, which is the bottom if positive
        moments are used.
    NAtrial : float
        The position of the neutral axis from the "top" of the beam.
    eConc : float
        The assumed strain in the concrete tat the top of the beam.

    Returns
    -------
    float
        The strain in the beam at position d.

    """

    
    return eConc * (d / NAtrial - 1)
    

    
def getSteelStrains(d:float, y:float|np.ndarray, NA:float, eConc:float):
    """
    Returns the strain at a set if input positions y, given the neutral axis
    position.
    
    d and NA area measured from the top of the beam for positive moments, and
    bottom of the beam for negative moments.
    The section is assume to have a strain of eConc at it's "top"
    
    
    """
    eEnd = getEndStrain(d, NA, eConc)
    
    return y * (eEnd + eConc) / d - eConc
    
    
def getSectionSr(section:SectionConcrete, NAlocation:float, 
                 yMoment:bool = True,
                 positiveMoment = True):
    """
    Gets gets an array with the force in each rebar. By default assumes
    that the rebars have yielded.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the "start" of the beam in mm.
    yMoment : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    positiveMoment : TYPE, optional
        A flog that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        The default is True.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    T : TYPE
        DESCRIPTION.

    """
    
    lunit = 'mm'    
    rebar = section.rebar
    # rebar[0][0].

    lfactor = section.concrete.lConvert(lunit)
    if yMoment:
        h = section.concrete.d * lfactor
        coords = section.rebar.getyCoords(lunit, True)
    else:
        h = section.concrete.b * lfactor
        coords = section.rebar.getxCoords(lunit, True)

    # Reverse the coordinates if the moment is negative
    if not positiveMoment:
        coords = coords[::-1]
    
    eConc = section.concrete.mat.ey
    strains = getSteelStrains(h, coords, NAlocation, eConc)  
    
    # Check to make sure that the correct input has been provided.
    if len(strains) != rebar.Nbars:
        raise Exception('A strain value must be given for each rebar.')
    
    ey = rebar.mat.ey
    
    
    Asteel = np.concatenate(rebar.getAttr('A'))
    overInd  = np.where(ey < strains)
    underInd = np.where(strains < -ey)
    strains[overInd]  =  ey
    strains[underInd] = -ey
    
    T = strains * Asteel * rebar.mat.E * phiS
                
    return T

    
def getSectionCr(section:SectionConcrete, NAlocation:float, 
                 yMoment:bool = True,
                 positiveMoment = True):
    """
    Gets the concrete compressive force at a section, given a NA location.
    Alpha and beta for the concrete are set at at the material.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the "start" of the beam in mm.
    yMoment : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    positiveMoment : TYPE, optional
        A flog that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        The default is True.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    T : TYPE
        DESCRIPTION.

    """
    
    lunit = 'mm'
    sunit = 'MPa'    
    
    b = section.getWidth(yMoment, positiveMoment, lunit)

    sconvert =section.concrete.mat.sConvert(sunit)
    fc = section.concrete.mat.fc * sconvert
    alpha = section.concrete.mat.alpha
    beta = section.concrete.mat.beta

                
    return phiC * alpha * beta * NAlocation * fc * b













def checkTr():
    
    pass

def checkSteelStrain(epsCmax:float, d:float, c:float):
    
    return epsCmax*(d/c - 1)



def checkSectionYield(fy, fc, As, d, b, alpha, beta, epsCmax, epsyLim = 0.02):
    
    Tr = checkYieldTr(fy, As)
    a = getCompressionDepth(Tr, alpha, fc, b)
    c = a / beta
    checkSteelStrain(epsCmax, d, c)




def checkSectionYield(c:float, d:float, epsCmax:float, epsyLim = 0.02):
    
    """
    A23.3 C1.10.5.2|
    """
    
    
    return c
    
    

def getCompressionDepth(Tr, alpha, fc, b):
    
    return Tr / (alpha * phiC * fc * b)
    
    
    


def getAsmin(fc:float, fy:float, bt:float, h:float):
    """
    CSA A23.3 Cl.10.5.1.2
    Expects outputs in units of mm and MPa
    
    Parameters
    ----------
    fc : float
        The concrete strength in MPa.
    fy : float
        The steel yield strength in MPa.
    bt : float
        The with of the beam in it's tension zone.
    h : float
        The total depth of the beam.

    Returns
    -------
    float
        The minimum required steel in mm..

    """

    
    return 0.2 * (fc)**2 / fy * bt * h
    
    
    
    
def checkYieldTr(fy:float, As:float):
    
    return phiS * fy * As


