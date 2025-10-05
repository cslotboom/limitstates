"""
Author: CS
Date: 202050913
Description:
    Contains functions that can solve the section for internal forces or
    the neutral axis location.

"""

from typing import Union

import numpy as np

# from .material import MaterialRebarCSA24
from .element import phiC, phiS

from limitstates import SectionConcrete
from limitstates.objects.section.concrete import SectionNASolver

def getEndStrain(d: float, NAtrial: float, eConc: float):

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
     
def getSteelStrains(d:float, y:Union[float, np.ndarray], 
                    NA:float, eConc:float):
    """
    Returns the strain at a set if input positions y, given the neutral axis
    position.
    
    y, d and NA area measured from the compression face of the beam.
    The section is assume to have a strain of eConc at it's "top"
    
    
    """
    eEnd = getEndStrain(d, NA, eConc)
    
    return y * (eEnd + eConc) / d - eConc
    
def getSectionSr(section: SectionConcrete, NAlocation: float, 
                 yForce: bool = True,
                 posForce: bool = True):
    """
    Gets gets an array with the force in each rebar. By default assumes
    that the rebars have yielded.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the tension edge of the beam in mm.
    yForce : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    posForce : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    T : list[float]
        The force in each longditudinal rebar.

    """
    
    lunit = 'mm'    
    rebar = section.rebar

    lfactor = section.concrete.lConvert(lunit)
    if yForce:
        h = section.concrete.d * lfactor
        coords = section.rebar.getyCoords(lunit, True)
    else:
        h = section.concrete.b * lfactor
        coords = section.rebar.getxCoords(lunit, True)

    # the strains are measured from the tension face
    # Reverse the coordinates if the moment is negative
    if posForce:
        coords = h - coords
    
    eConc = section.concrete.mat.ey
    strains = getSteelStrains(h, coords, NAlocation, eConc)  
    
    # Check to make sure that the correct input has been provided.
    if len(strains) != rebar.Nbar:
        raise Exception('A strain value must be given for each rebar.')
    
    ey = rebar.mat.ey
    
    
    Asteel = np.concatenate(rebar.getAttr('A'))
    overInd  = np.where(ey < strains)
    underInd = np.where(strains < -ey)
    strains[overInd]  =  ey
    strains[underInd] = -ey
    
    T = strains * Asteel * rebar.mat.E * phiS
                
    return T

def getSectionCr(section: SectionConcrete, NAlocation: float, 
                 yForce: bool = True,
                 posForce = True):
    """
    Gets the concrete compressive force at a section, given a NA location.
    Alpha and beta for the concrete are set at at the material.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the compression face of of the beam in mm.
    yForce : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    posForce : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.


    Returns
    -------
    C : float
        The output compression force in the section.

    """
    
    lunit = 'mm'
    sunit = 'MPa'    
    
    b = section.getWidth(yForce, lunit)

    sconvert = section.concrete.mat.sConvert(sunit)
    fc = section.concrete.mat.fc * sconvert
    alpha = section.concrete.mat.alpha
    beta = section.concrete.mat.beta

                
    return phiC * alpha * beta * NAlocation * fc * b

def getSectionMr(section: SectionConcrete, NAlocation: float = None, 
                 yForce: bool = True,
                 posForce:bool = True):
    """
    NA is measured from the compression face of the section 
    while coordinates are measured from the bottom of the section.
    """
    
    if not NAlocation:
        # The section could have no rebar, if so return 0
        if not section.rebar or len(section.rebar) == 0:
            return 0        
        NAlocation    = solveForNA(section, yForce, posForce)
    
    Sr = getSectionSr(section, NAlocation, yForce, posForce)
    Cr = getSectionCr(section, NAlocation, yForce, posForce)
    
    if yForce:
        coords = section.rebar.getyCoords('mm', flatten=True)
    else:
        coords = section.rebar.getxCoords('mm', flatten=True)
    d = section.getDepth(yForce, 'mm')
    
    # NAlocation is measured from the tension edge of the beam
    # coordinates are measured in an absolute position.
    if posForce:
        rebarCoords = (d - coords) - NAlocation
    else:
        rebarCoords = coords - NAlocation

    Mr =  (sum(Sr * rebarCoords) + Cr * (NAlocation/2)) / 1000
    return Mr

class SectionNASolverCSA24(SectionNASolver):
    """
    Attempts to solves for the neutral axis of a section. Assumes all 
    bars use the same material.
    
    Solves for the neutral axis within a section.
    The neutral axis is measured from the top of the section.

    Parameters
    ----------
    section : SectionConcrete
        The concrete section to solve the NA of.        
    Pf : float, optional
        A axial force applied to the section. The default is 0.
    yForce : bool, optional
        A flag that specifies if moment is applied in the y or x direction. 
        The default is True, for moment being applied about the x axis.
    posForce : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.
    tol : float, optional
        The tolerance required for convergence, i.e. the difference between
        the calcualted concrete and steel force. The default is 1e-3.
    maxIter : float, optional
        The maximum number of iterations needed before convergence is 
        reached. The default is 100.
    logging : bool, optional
        A flag that turns on or off logging. Currently is inactive. 
        The default is True.

    Returns
    -------
    None.

    """
    def __init__(self, section: SectionConcrete, Pf:float = 0, 
                 yForce: bool = True, posForce: bool = True, 
                 NAtrial: float = None, tol: float = 1e-3, 
                 maxIter: float = 100, logging: bool = True):
        super().__init__(section, getSectionCr, getSectionSr,
                         Pf, yForce, posForce, 
                         NAtrial, tol, maxIter, logging)
        
def solveForNA(section: SectionConcrete, Pf: float = 0, yForce: bool = True, 
             posForce: bool = True, NAtrial: float = None, tol: float = 1e-3, 
             maxIter: float = 100):
    """
    Attempts to solves for the neutral axis of a section. Assumes all 
    bars use the same material.
    
    Solves for the neutral axis within a section.
    The neutral axis is measured from the top of the section.

    Parameters
    ----------
    section : SectionConcrete
        The concrete section to solve the NA of.        
    Pf : float, optional
        A axial force applied to the section. The default is 0.
    yForce : bool, optional
        A flag that specifies if moment is applied in the y or x direction. 
        The default is True, for moment being applied about the x axis.
    posForce : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.
    tol : float, optional
        The tolerance required for convergence, i.e. the difference between
        the calcualted concrete and steel force. The default is 1e-3.
    maxIter : float, optional
        The maximum number of iterations needed before convergence is 
        reached. The default is 100.
    logging : bool, optional
        A flag that turns on or off logging. Currently is inactive. 
        The default is True.

    Returns
    -------
    None.

    """
    
    naSolver = SectionNASolverCSA24(section, Pf, yForce, posForce, NAtrial,
                               tol, maxIter)

    return naSolver.calcNA()
