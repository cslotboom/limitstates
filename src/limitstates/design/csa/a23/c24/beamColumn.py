"""
Contains the code designc clauses
"""

import numpy as np
from math import tan

from .element import BeamColumnConcreteCsa24, ShearConfigurations, phiC, phiS
from .section import REBARFACTORY

from .nasolver import getSectionCr
from limitstates import SectionConcrete, Rebar, RebarSpacingConfig

   
def getBalancedNA(deff: float, eyConc: float = 0.0035,
                  eySteel: float = 0.002):
    
    return eyConc / (eyConc + eySteel) * deff 

def getBalancedRatio(eyConc: float = 0.0035,
                     eySteel: float = 0.002):
    
    return eyConc / (eyConc + eySteel) 

def getRhoBalanced(alpha: float, beta: float, fc: float, fy: float, 
                   eyConc: float = 0.0035, eySteel: float = 0.002):
    
    ratio = getBalancedRatio(eyConc, eySteel)
    
    rho = ratio * alpha * beta * fc * phiC / (fy * phiS)
    return rho

def getSectionBalancedNA(section: SectionConcrete, deff: float = None,
                        eySteel: float = 0.002, yForce: bool = True, 
                        posForce: bool = True):
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
    yForce : bool, optional
        DESCRIPTION. The default is True.
    posForce : bool, optional
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
        deff = section.getDepth(yForce, posForce, lunit)*0.8
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
    
    return getRhoBalanced(alpha, beta, fc, fySteel, eyConc, eySteel)
    
def getSectionBalancedAnet(section: SectionConcrete, deff: float = None,
                        eySteel: float = 0.002, fySteel: float = 400,
                        yForce: bool = True, posForce: bool = True):
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
    yForce : bool, optional
        DESCRIPTION. The default is True.
    posForce : bool, optional
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
        deff = section.getDepth(yForce, posForce, lunit)
        # deff  =
    
    eyConc = section.concrete.mat.ey
    c  = getBalancedNA(deff, eyConc, eySteel)
    Cr = getSectionCr(section, c, yForce, posForce)
 
    return Cr / (phiS * fySteel)

def getCompressionDepth(Tr, alpha, fc, b):
    
    return Tr / (alpha * phiC * fc * b)

    
# =============================================================================
# Spacing
# =============================================================================

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
   
    
   
    
def getSectionSpacingRules(rebar: Rebar, section: SectionConcrete,
                            cover:float = 25, includeRadius = False, 
                            dstir = None, lUnit = 'mm') -> RebarSpacingConfig:
    
    rlFactor = rebar.lConvert(lUnit)
    d = rebar.d * rlFactor

    # TODO amax location this material
    lFactor = section.concrete.mat.lConvert(lUnit)
    amax    = section.concrete.mat.amax * lFactor
    
    s = getSmin(d, amax)
    c = cover
    
    if dstir:
        dstir = dstir
    elif section.stirrups:
        stirrup  = section.stirrups[0]
        lFactor = stirrup.rebar.lConvert(lUnit)
        dstir = stirrup.rebar.d * lFactor
    else:
        dstir = 0
        
    if section.stirrups and includeRadius:
        rcurve = section.stirrups[0].rebar.rcurve * lFactor
    else:
        rcurve = 0
    
    return RebarSpacingConfig(s, c, dstir, rcurve, lUnit)
        
    
def getElementSpacingRules(rebar: Rebar, element: BeamColumnConcreteCsa24, 
                           sectionInd: int = 0, includeRadius = False, 
                           lUnit = 'mm') -> RebarSpacingConfig:
    
    section = element.getSection(sectionInd)
    cover   = element.designProps.cover
        
    return getSectionSpacingRules(rebar, section, cover, includeRadius, lUnit)

        

   
    
   
# =============================================================================
# 
# =============================================================================
   
    
def getAsmin(fc: float, fy: float, bt: float, h: float):
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

def getdveff(dv: float, h: float):
    """
    Gets the code effective shear depth of a beam, which is 0.9 of the distance
    of the beam to the centroid of longditudinal reinforcement. 
    Assumes inputs are in mm.

    Parameters
    ----------
    dv : float
        The depth of depth of the rebar in the direction of interest.
    h : float
        The depth of the section in the direction of interst.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return max(0.9*dv, 0.72*h)






def getSectiondveff(section: SectionConcrete, yForce, posForce, 
                    dvEstimate: float = None, lUnit = 'mm'):
        
    # Manual override to dv
    if dvEstimate:
        dv = dvEstimate
    
    # if the rebar has not been set and there is no manual override, 
    # raise exception
    elif not section.rebar:
        raise Exception("Rebar in section has not been placed, and no dv"\
                        "estimate is given, Vc cannot be calcualted.")
    # Calculate dv, this is the normal thing that happens. 
    else:
        dv = section.getRebarMaxDepth(yForce, posForce, lUnit)
        
    h  = section.getDepth(yForce, lUnit)
    return getdveff(dv, h)
    


def getShearBeta(shearEnum: ShearConfigurations, dv:float = None) -> float:
    """
    A23.3 EQ 11.9
    """

    if shearEnum == ShearConfigurations.MinTransverse:
        beta = 0.18
    elif shearEnum == ShearConfigurations.NoTransverse:
        beta = (230) / (1000 + dv)
    elif shearEnum == ShearConfigurations.NoTransverseAmax20:
        raise Exception('Not implimented')
    return beta





def getElementVrc(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yForce: bool = True, posForce: bool = True, 
                 dvEstimate:float = None) -> float:

    section = element.getSection(sectionInd)
    lam     = element.designProps.lam

    shearENum = element.designProps.shearReinforcementType
    
                        
    # h  = section.getDepth(yForce)
    bw = section.getWidth(yForce)
    dveff = getSectiondveff(section, yForce, posForce, dvEstimate = dvEstimate)
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
                 yForce: bool = True, posForce: bool = True)  -> float:
    """
    Returns the maximum for an element
    
    Theta is taken from the design propreties, and should be set according
    to c.l. 11.3.6.3 if it hasn't already been.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        _description_
    sectionInd : int, optional
        _description_, by default 0
    yForce : bool, optional
        _description_, by default True
    posForce : bool, optional
        _description_, by default True

    Returns
    -------
    _type_
        _description_
    """
    section = element.getSection(sectionInd)
    theta   = element.designProps.theta

    mat = section.stirrups.mat
    sConvert = mat.sConvert('MPa')    
    fy       = mat.fy * sConvert
    
    
    
    Av = section.stirrups.getAvNet()
    s  = section.stirrups.getSpacing()

    dveff = getSectiondveff(section, yForce, posForce)
   
    return getVrs(Av, fy, dveff, theta, s)

def getVrs(Av: float, fy: float, dv: float, theta: float, s: float) -> float:
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


def getElementSminForVrs(element: BeamColumnConcreteCsa24, Vrs: float, 
                         sectionInd: int = 0, barType: str = '10M', 
                         Nlegs: int = 2, dvEstimate = None,
                         yForce: bool = True, posForce: bool = True)  -> float:
    """
    Returns the maximum for an element
    
    Theta is taken from the design propreties, and should be set according
    to c.l. 11.3.6.3 if it hasn't already been.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        _description_
    sectionInd : int, optional
        _description_, by default 0
    yForce : bool, optional
        _description_, by default True
    posForce : bool, optional
        _description_, by default True

    Returns
    -------
    _type_
        _description_
    """
    section = element.getSection(sectionInd)
    theta   = element.designProps.theta
        
    rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
    Av = rebar.A * Nlegs
    fy = rebar.mat.fy
    Av = Nlegs * rebar.A


    dveff = getSectiondveff(section, yForce, posForce, dvEstimate=dvEstimate)
   
    return getSminForVrs(Av, fy, dveff, theta, Vrs)



def getSminForVrs(Av: float, fy: float, dv: float, theta: float, Vs: float) -> float:
    """    

    Re-arranges to determine a required shear force, Vs, for 
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
    Vs : float
        The required Vs of the stirrups

    Returns
    -------
    _type_
        _description_
    """

    return phiS * Av * fy * dv  / (Vs * tan(theta))



def getVmax(fc: float, bw: float, dveff: float) -> float:
    """
    Calculates the maximum shear a section can resist from 
    A23.3 c.l. 13.3.3.

    Parameters
    ----------
    fc : float
        DESCRIPTION.
    bw : float
        The shear width of the section.
    dv : float
        The .

    Returns
    -------
    None.

    """
    
    return 0.25 * phiC * fc * bw * dveff

def getElementVmax(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yForce: bool = True, posForce: bool = True,
                 dvEstimate: float = None):
    
    section = element.getSection(sectionInd)

    dveff = getSectiondveff(section, yForce, posForce, dvEstimate)
    bw = section.getWidth(yForce)
    
    sConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sConvert
    return getVmax(fc, bw, dveff)



def getElementVr(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yForce: bool = True, posForce: bool = True,
                 dvEstimate: float = None):
    """_summary_

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        _description_
    sectionInd : int, optional
        _description_, by default 0
    yForce : bool, optional
        _description_, by default True
    posForce : bool, optional
        _description_, by default True

    Returns
    -------
    _type_
        _description_
    """
    section = element.getSection(sectionInd)
    lam     = element.designProps.lam
    theta   = element.designProps.theta


    scConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * scConvert    
    
    srConvert = section.stirrups.mat.sConvert('MPa')
    fy = section.stirrups.mat.fy * srConvert
    
    Av = section.stirrups.getAvNet()
    s  = section.stirrups.getSpacing()

    bw = section.getWidth(yForce)
    dveff = getSectiondveff(section, yForce, posForce, dvEstimate)
    # dv = section.getRebarMaxDepth(yForce, posForce)
    # h  = section.getDepth(yForce)
    # dveff = getdveff(dv, h)
   
    shearENum = element.designProps.shearReinforcementType
    beta  = getShearBeta(shearENum, dveff)   
   
    Vrs = getVrs(Av, fy, dveff, theta, s)
    Vrc = getVrc(lam, beta, fc, bw, dveff)

    return Vrs + Vrc





def getSmaxGeom(dveff: float, Vf: float = 0, Vrmax: float = 0) -> float:
    """
    Calculates the maximum shear a section can resist from 
    A23.3 c.l. 13.3.3.
    
    If the applied force is greater than half of Vrmax, then tighter spacing
    of stirrups is required.

    Parameters
    ----------
    dveff : float
        The effective shear depth in mm.
    Vf : float, optional
        The applied force on the section in kN. The default is 0.
    Vrmax : float, optional
        The maximum resistance of the section in kN. The default is 0.

    Returns
    -------
    float
        The maximum stirrup spacing in mm.

    """
    
    sMax = min(0.7*dveff, 600)
    
    if Vf > Vrmax/2:
        return sMax / 2
    else:
        return sMax
       
def getElementSmaxGeom(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                     yForce: bool = True, posForce: bool = True, 
                     dvEst: float = None,
                     Vf: float = 0, Vrmax: float = 0):
    """
    The maximum spacing possible by geometry
    """
    section = element.getSection(sectionInd)

    dveff = getSectiondveff(section, yForce, posForce, dvEst)

    return getSmaxGeom(dveff, Vf, Vrmax)
     


def getAvmin(fc: float, bw: float, fy: float, s: float) -> float:
    """
    Calculates the minimum area of shear reinforcement required according to 
    A23.3 c.l. 11.2.8.2

    Parameters
    ----------
    fc : float
        The applied concrete strength in MPa.
    bw : float
        The width of the section at the shear .
    s : float
        The spacing of the stirrups.
    fy : float
        The yield strength of the rebar.

    Returns
    -------
    float
        DESCRIPTION.

    """

    Avmin = 0.06 * (fc)**0.5 * (bw * s / fy)
    
    return Avmin
       

def getStirrupSmax(fc: float, bw: float, fy: float, Av: float) -> float:
    """
    Calculates the minimum shear spacing required for a given shear area, by
    rearranging A23.3 c.l. 11.2.8.2
    
    Generally used to calculate the maximum spacing that a given set of rebar
    can be placed at

    Parameters
    ----------
    fc : float
        The applied concrete strength in MPa.
    bw : float
        The width of the section at the shear .
    fy : float
        The yield strength of the rebar.
    Av : float
        The spacing of the stirrups.
        
    Returns
    -------
    float
        DESCRIPTION.

    """

    sMin = (Av * fy) / (0.06 * (fc)**0.5 * bw )
    
    return sMin
       

def getElementSmaxStirrup(element: BeamColumnConcreteCsa24, 
                          sectionInd: int = 0, barType: str = '10M', 
                          Nleg: int = 2, fy = 400, yForce = True):
    """
    The maximum spacing possible with a given bar
    """
    
    section = element.getSection(sectionInd)

    scConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * scConvert    
        
    bw = section.getWidth(yForce)
    
    rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
    Av = rebar.A * Nleg
  
    return getStirrupSmax(fc, bw, fy, Av)


def getElementSmax(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                   barType: str = '10M', Nleg: int = 2, fy = 400,
                     yForce: bool = True, posForce: bool = True, 
                     dvEst: float = None, Vf: float = 0, Vrmax: float = 0):

    S1 = getElementSmaxStirrup(element, sectionInd, barType, Nleg, fy, yForce)
    S2 = getElementSmaxGeom(element, sectionInd, yForce, posForce, 
                            dvEst, Vf, Vrmax)
    
    return min(S1, S2)

# def getSminForBar(Vs, sectionInd: int = 0,
#                    barType: str = '10M', 
#                    Nleg: int = 2, fy = 400, yForce = True):
    
#     section = element.getSection(sectionInd)

#     scConvert = section.concrete.mat.sConvert('MPa')
#     fc = section.concrete.mat.fc * scConvert    
        
#     bw = section.getWidth(yForce)
    
#     rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
#     Av = rebar.A * Nleg
  
#     return getStirrupSmin(fc, bw, fy, Av)


def designStirrups():
    pass
