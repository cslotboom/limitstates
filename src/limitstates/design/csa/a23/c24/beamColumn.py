"""
Contains the code designc clauses
"""
from typing import Union
from enum import IntEnum
import numpy as np
from math import tan

from .element import BeamColumnConcreteCsa24, ShearConfigurations
from .section import REBARFACTORY, loadRebarFactory
from .material import MaterialRebarCSA24
from limitstates import DesignDiagram, SectionConcrete
from limitstates.objects.section.concrete import SectionNASolver, RebarPlacerRow, RebarSpacingConfig


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
                 yMoment: bool = True,
                 posMoment: bool = True):
    """
    Gets gets an array with the force in each rebar. By default assumes
    that the rebars have yielded.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the tension edge of the beam in mm.
    yMoment : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    posMoment : bool, optional
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
    # rebar[0][0].

    lfactor = section.concrete.lConvert(lunit)
    if yMoment:
        h = section.concrete.d * lfactor
        coords = section.rebar.getyCoords(lunit, True)
    else:
        h = section.concrete.b * lfactor
        coords = section.rebar.getxCoords(lunit, True)

    # the strains are measured from the tension face
    # Reverse the coordinates if the moment is negative
    if posMoment:
        coords = h - coords
    
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
                 posMoment = True):
    """
    Gets the concrete compressive force at a section, given a NA location.
    Alpha and beta for the concrete are set at at the material.
    
    Parameters
    ----------
    section : SectionConcrete
        The concrete section to check.
    NAlocation : float
        The neutral axis location from the compression face of of the beam in mm.
    yMoment : bool, optional
        A flag that specifies if moment is about the y axis, i.e. the strong
        axis. The default is True, setting up strong axis bending.
    posMoment : bool, optional
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
    
    b = section.getWidth(yMoment, posMoment, lunit)

    sconvert = section.concrete.mat.sConvert(sunit)
    fc = section.concrete.mat.fc * sconvert
    alpha = section.concrete.mat.alpha
    beta = section.concrete.mat.beta

                
    return phiC * alpha * beta * NAlocation * fc * b

def getSectionMr(section:SectionConcrete, NAlocation:float = None, 
                 yMoment:bool = True,
                 posMoment = True):
    """
    NA is measured from the compression face of the section 
    while coordinates are measured from the bottom of the section.
    """
    
    if not NAlocation:
        # The section could have no rebar, if so return 0
        if not section.rebar or len(section.rebar) == 0:
            return 0        
        NAlocation    = solveForNA(section, yMoment, posMoment)
    
    Sr = getSectionSr(section, NAlocation, yMoment, posMoment)
    Cr = getSectionCr(section, NAlocation, yMoment, posMoment)
    
    if yMoment:
        coords = section.rebar.getyCoords('mm', flatten=True)
    else:
        coords = section.rebar.getxCoords('mm', flatten=True)
    d = section.getDepth(yMoment, 'mm')
    
    # NAlocation is measured from the tension edge of the beam
    # coordinates are measured in an absolute position.
    if posMoment:
        rebarCoords = (d - coords) - NAlocation
    else:
        rebarCoords = coords - NAlocation

    Mr =  (sum(Sr * rebarCoords) + Cr * (NAlocation/2)) / 1000
    return Mr


def getBalancedNA(deff:float, eyConc: float = 0.0035,
                  eySteel: float = 0.002):
    
    return eyConc / (eyConc + eySteel) * deff 

def getBalancedRatio(eyConc: float = 0.0035,
                     eySteel: float = 0.002):
    
    return eyConc / (eyConc + eySteel) 


def getRhoBalanced(alpha:float, beta:float, fc: float, fy: float, 
                   eyConc: float = 0.0035, eySteel: float = 0.002):
    
    ratio = getBalancedRatio(eyConc, eySteel)
    
    rho = ratio * alpha * beta * fc * phiC / (fy * phiS)
    return rho


def getSectionBalancedNA(section:SectionConcrete, deff:float = None,
                        eySteel = 0.002, yMoment:bool = True, 
                        posMoment = True):
    """
    Estimates the balanced NA position for a section. If no deff is provided,
    then the depth will be estimated as 80% of the section height.
    
    This check is typically used before steel has been palced in the section.
    It is assumed that the steel has not yet been placed in the section

    Parameters
    ----------
    section : SectionConcrete
        DESCRIPTION.
    deff : float, optional
        DESCRIPTION. The default is None.
    yMoment : bool, optional
        DESCRIPTION. The default is True.
    posMoment : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    lunit = 'mm'
    
    if not deff :
        print('No depth provided. Depth is estimated as 80% of h')
        deff = section.getDepth(yMoment, posMoment, lunit)*0.8
        # deff  =
    
    eyConc = section.concrete.mat.ey
    
    return getBalancedNA(deff, eyConc, eySteel)

def getSectionBalancedRho(section: SectionConcrete, 
                         eySteel:float = 0.002, fySteel:float = 400):
    
    """
    RHo for the balanced condition is returned assuming Cr = Tr, and assuming
    that all steel is in the same layer and has yielded.
    
    If steel is, the balanced condition equation is not correct.
    """
    
    alpha = section.concrete.mat.alpha
    beta = section.concrete.mat.beta
    
    sConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sConvert    
    eyConc = section.concrete.mat.ey
    # c = getBalancedNA(deff, eyConc, eySteel)
    # Cr = getSectionCr(section, c, yMoment, posMoment)
     
    
    return getRhoBalanced(alpha, beta, fc, fySteel, eyConc, eySteel)
    
def getSectionBalancedAnet(section:SectionConcrete, deff:float = None,
                        eySteel:float = 0.002, fySteel:float = 400,
                        yMoment:bool = True, 
                        posMoment = True):
    """
    Estimates the balanced NA position for a section. If no deff is provided,
    then the depth will be estimated as 80% of the section height.
    
    It is assumed that the steel has not yet yielded

    Parameters
    ----------
    section : SectionConcrete
        DESCRIPTION.
    deff : float, optional
        DESCRIPTION. The default is None.
    yMoment : bool, optional
        DESCRIPTION. The default is True.
    posMoment : bool, optional
        A flag that specifies if moment is positive or negative. Positive
        moment is defined as moment that creates tension at the "bottom"
        of the beam. e.g. a simply supported beam has positive bending.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    lunit = 'mm'
    
    if not deff :
        print('No depth provided. Depth is estimated as 80% of h')
        deff = section.getDepth(yMoment, posMoment, lunit)
        # deff  =
    
    eyConc = section.concrete.mat.ey
    c = getBalancedNA(deff, eyConc, eySteel)
    Cr = getSectionCr(section, c, yMoment, posMoment)
 
    return Cr / (phiS * fySteel)

def checkSectionYield(c:float, d:float, epsCmax:float, epsyLim = 0.02):
    
    """
    A23.3 C1.10.5.2
    """
    
    
    return c
    
    

def getCompressionDepth(Tr, alpha, fc, b):
    
    return Tr / (alpha * phiC * fc * b)
    
    
def getSmin(db:float, amax:float):
    """
    Returns minimum spacing for a given rebar with a given aggregate.

    Parameters
    ----------
    db : float
        The diameter for the rebar.
    amax : float
        The aggregate size.

    Returns
    -------
    float
        The minimum clear spacing

    """
    return np.max((1.4*db, 1.4*amax, 30))
   
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

    
    return 0.2 * (fc)**0.5 / fy * bt * h


def getSectionAsmin(section: SectionConcrete, fy: float = None):
    """
    Currently only applies to rectangular sections.
    
    CSA A23.3 Cl.10.5.1.2
    
    If no fy is provided, the section's rebar will be used for fy. If the 
    section has no rebar, a default value of 400MPa is used. 

    Returns in units of sqmm    
    
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
    
    
    sConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sConvert
    
    b = section.getWidth()
    h = section.getDepth()
        
    # If the 
    if fy is None and section.rebar:
        sConvert = section.rebar.mat.sConvert('MPa')
        fy = section.rebar.mat.fy
    if fy is None and section.rebar is None:
        fy = 400
    
    return getAsmin(fc, fy, b, h)


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
    yMoment : bool, optional
        A flag that specifies if moment is applied in the y or x direction. 
        The default is True, for moment being applied about the x axis.
    posMoment : bool, optional
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
    def __init__(self, section: SectionConcrete, 
                 Pf:float = 0, yMoment: bool = True, 
                 posMoment: bool = True, NAtrial: float = None,
                 tol: float = 1e-3, maxIter: float = 100,
                 logging:bool = True):
        super().__init__(section, getSectionCr, getSectionSr,
                         Pf, yMoment, posMoment, 
                         NAtrial, tol, maxIter, logging)
        
# TODO, move this function into it's own folder?
def solveForNA(section: SectionConcrete, 
             Pf:float = 0, yMoment: bool = True, 
             posMoment = True, NAtrial: float = None,
             tol: float = 1e-3, maxIter: float = 100):
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
    yMoment : bool, optional
        A flag that specifies if moment is applied in the y or x direction. 
        The default is True, for moment being applied about the x axis.
    posMoment : bool, optional
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
    
    naSolver = SectionNASolverCSA24(section, Pf, yMoment, posMoment, NAtrial,
                               tol, maxIter)

    return naSolver.calcNA()



def getdveff(dv: float, h: float):
    return max(0.9*dv, 0.72*h)



def getShearBeta(shearEnum: ShearConfigurations, dv:float = None):
    """
    A23.3 EQ 11.9
    """

    if shearEnum == ShearConfigurations.MinTransverse:
        beta = 0.18
    elif shearEnum == ShearConfigurations.NoTransverseAmax20:
        beta = (230) / (1000 + dv)
    elif shearEnum == ShearConfigurations.NoTransverse:
        raise Exception('Not implimented')
    return beta



def getElementVrc(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yShear: bool = True, posShear: bool = True):

    section = element.getSection(sectionInd)
    lam     = element.designProps.lam

    shearENum = element.designProps.shearReinforcenemtType
    dv = section.getRebarDepth(yShear, posShear)
    h  = section.getDepth(yShear)
    bw = section.getWidth(yShear)
    dveff = getdveff(dv, h)
    beta  = getShearBeta(shearENum, dveff)
    
    fc = section.concrete.mat.fc

    return getVrc(lam, beta, fc, bw, dveff)

def getVrc(lam: float, beta: float, fc: float,
          bw: float, dv: float):
    """
    Returns the Value Vc for a concrete 
    c.l. 11.3.4.

    """

    return phiC * lam * beta * fc**0.5 * bw * dv



def getElementVrs(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yShear: bool = True, posShear: bool = True):
    """_summary_

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        _description_
    sectionInd : int, optional
        _description_, by default 0
    yShear : bool, optional
        _description_, by default True
    posShear : bool, optional
        _description_, by default True

    Returns
    -------
    _type_
        _description_
    """
    section = element.getSection(sectionInd)
    theta   = element.designProps.theta

    fy = section.stirrups.rebar.mat.fy
    Av = section.stirrups.Nlegs * section.stirrups.rebar.A
    s  = section.stirrups.spacing

    dv = section.getRebarDepth(yShear, posShear)
    h  = section.getDepth(yShear)
    dveff = getdveff(dv, h)
   
    return getVrs(Av, fy, dveff, theta, s)



def getVrs(Av: float, fy: float, dv: float, theta: float, s: float):
    """    

    Returns the Value Vc for a concrete using the simplified method.
    c.l. 11.3.4.

    Theta from c.l. 11.3.6.3
    

    Parameters
    ----------
    Av : float
        The area per leg of stirrup in sqmm
    fy : float
        The rebar yield stress in MPa
    dv : float
        The shear depth of the concrete section in the direction of interst, in mm.
    theta : float
        The angle of diagonal compressive stresses, see c.l. 11.3.6.3
    s : float
        The spacing of the stirrups

    Returns
    -------
    _type_
        _description_
    """

    return phiS * Av * fy * dv / (tan(theta) * s)


