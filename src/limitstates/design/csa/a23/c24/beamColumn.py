"""
Author: CS
Description:
    Functions used to design a concrete beamcolumn, according to CSA A23.3-24.
"""

import numpy as np
from math import tan

# Import fom the object Library
from limitstates import SectionConcrete, Rebar, RebarSpacingConfig

# Import from A23.3
from .element import BeamColumnConcreteCsa24, ShearConfigurations, phiC, phiS
from .section import REBARFACTORY
from .nasolver import getSectionCr
   
def getBalancedNA(deff: float, eyConc: float = 0.0035,
                  eySteel: float = 0.002):
    """
    Returns the neutral axis position for steel at a given effective depth 
    at the balanced condition (where steel yields at the same time as concrete 
    crushing). 
    Assumes all inputs are in mm.
    Assumes strains are linearly distributed through the section.

    Parameters
    ----------
    deff : float
        The effective depth for the steel in the section.
    eyConc : float, optional
        The crushing/yield strain for the concrete. The default is 0.0035.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.

    Returns
    -------
    float
        The balanced neutral axis position, measured from where deff is 
        measured from.

    """
    
    return getBalancedRatio(eyConc, eySteel) * deff 

def getBalancedRatio(eyConc: float = 0.0035,
                     eySteel: float = 0.002):
    """
    Returns the ratio between the total change in strain, and concrete strain
    for the balanced condition (where steel yields at the same time as concrete 
    crushing).
    
    This is equivalent to the NA depth, divided by deff.

    Parameters
    ----------
    eyConc : float, optional
        The crushing/yield strain for the concrete. The default is 0.0035.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.

    Returns
    -------
    float
        The strain ratio.

    """
    
    return eyConc / (eyConc + eySteel) 

def getRhoBalanced(alpha: float, beta: float, fc: float, fy: float, 
                   eyConc: float = 0.0035, eySteel: float = 0.002):
    """
    Returns the rho value (ratio between steel area and total area) for the 
    balanced condition (where steel yields at the same time as concrete 
    crushing)

    Parameters
    ----------
    alpha : float
        The ratio of average stress in a compression block to specified
        stress (fc). See c.l. 10.1.7.
    beta : float
        The ratio of the rectangular compression block to depth of the neutral
        axis. See c.l. 10.1.7.
    fc : float
        The specified concrete strength in MPa.
    fy : float
        The specified steel strength in MPa.
    eyConc : float, optional
        The crushing/yield strain for the concrete. The default is 0.0035.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.

    Returns
    -------
    rho : float
        The ratio between steel area and total section ara for the balanced
        condition.

    """
    
    ratio = getBalancedRatio(eyConc, eySteel)
    
    rho = ratio * alpha * beta * fc * phiC / (fy * phiS)
    return rho

def getSectionBalancedNA(section: SectionConcrete, deff: float = None,
                        eySteel: float = 0.002, yDir: bool = True, 
                        posDir: bool = True):
    """
    Estimates the balanced NA position for a section in the balanced condition 
    (where steel yields at the same time as concrete 
    crushing). 
    
    If no deff is provided, then the depth will be estimated as 80% of the 
    section height.
    
    This check is typically used before steel has been palced in the section.
    It is assumed that the steel has not yet been placed in the section.
    
    Input units are assumed to be in mm, and output units are in mm.

    Parameters
    ----------
    section : SectionConcrete
        The section to use in the calculation.
    deff : float, optional
        The effective depth for the rebar in section. Used to calculate a NA
        position. The default is None.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.

    Returns
    -------
    float
        The effective NA position for the balanced condition.

    """
    
    lunit = 'mm'
    
    if not deff :
        print('No depth provided. Depth is estimated as 80% of h')
        deff = section.getDepth(yDir, posDir, lunit)*0.8
    
    eyConc = section.concrete.mat.ey
    
    return getBalancedNA(deff, eyConc, eySteel)

def getSectionBalancedRho(section: SectionConcrete, 
                         eySteel:float = 0.002, fy:float = 400):
    """
    Returns Rho for a section in the balanced condition,     
    (where steel yields at the same time as concrete crushing). 
    
    Rho for the balanced condition is returned assuming Cr = Tr, and assuming
    that all steel is in the same layer and has yielded.
    
    Note that this function does not factor in top steel.
    
    Parameters
    ----------
    section : SectionConcrete
        The section to use in the calculation.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.
    fy : float
        The specified steel strength in MPa. The default is 400MPa.

    Returns
    -------
    float
        rho for the balanced section.

    """
    
    
    alpha = section.concrete.mat.alpha
    beta = section.concrete.mat.beta
    
    sConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sConvert    
    eyConc = section.concrete.mat.ey    
    
    return getRhoBalanced(alpha, beta, fc, fy, eyConc, eySteel)
    
def getSectionBalancedAnet(section: SectionConcrete, deff: float = None,
                        eySteel: float = 0.002, fy: float = 400,
                        yDir: bool = True, posDir: bool = True):
    """
    Estimates the balanced Anet for a section. If no deff is provided,
    then the depth will be estimated as 80% of the section height.
    
    It is assumed that the steel has not yet yielded.
    
    Expects all inputs in mm, and returns outputs in mm.

    Parameters
    ----------
    section : SectionConcrete
        The section to use in the calculation.
    deff : float, optional
        The effective depth for the rebar in section. Used to calculate a NA
        position. The default is None.
    eySteel : float, optional
        The yield strain for the rebar. The default is 0.002.
    fy : float
        The specified steel strength in MPa. The default is 400MPa.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.

    Returns
    -------
    float
        The output area required for the balanced section in mm.

    """
    
    lunit = 'mm'
    
    if not deff :
        print('No depth provided. Depth is estimated as 80% of h')
        deff = section.getDepth(yDir, posDir, lunit)
    
    eyConc = section.concrete.mat.ey
    c  = getBalancedNA(deff, eyConc, eySteel)
    Cr = getSectionCr(section, c, yDir, posDir)
 
    return Cr / (phiS * fy)
    
# =============================================================================
# Spacing
# =============================================================================

def getSmin(db: float, amax: float):
    """
    Returns minimum spacing for a given rebar with a given aggregate.
    Expects units in mm and returns units in mm.

    Parameters
    ----------
    db : float
        The diameter for the rebar.
    amax : float
        The maximum aggregate size, see c.l. 6.6.5.2

    Returns
    -------
    float
        The minimum clear spacing in mm

    """
    return np.max((1.4*db, 1.4*amax, 30))
   
def getSectionSpacingRules(rebar: Rebar, section: SectionConcrete,
                            cover:float = 25, includeRadius = False, 
                            dstir = None, lUnit = 'mm') -> RebarSpacingConfig:
    """
    Returns a set of standard spacing rules for a section, given a input
    rebar section.

    Parameters
    ----------
    rebar : Rebar
        The rebar to use when determing spacing rules.
    section : SectionConcrete
        The section to get the spacing rules with. The section is used to pull
        material information (amax), and stirrup information.
    cover : float, optional
        The clear distance from the rebar to a section edge. 
        The default is 25mm.
    includeRadius : str, optional
        A flag that specifies if rebar bend radius should be included in the
        output class. The default is False.
    dstir : str, optional
        The diamter of the stirrup. If it is not provided, and the section has 
        stirrups, the section's stirrup diameter is used. The default is None.
        If this is provided, the diameter of rebar in the section is ignored.
    lUnit : str, optional
        The length units for the output config. The default is 'mm'.

    Returns
    -------
    RebarSpacingConfig
        The configuration object containing the rebar spacing information.

    """
    
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
                           dstir = None,
                           lUnit = 'mm') -> RebarSpacingConfig:
    
    """
    Returns a set of standard spacing rules for a element, given a input
    rebar section index.

    Parameters
    ----------
    rebar : Rebar
        The rebar to use when determing spacing rules.
    element : BeamColumnConcreteCsa24
        The element to get the spacing rules with. The element is used to pull
        material information (amax, cover), and stirrup information.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    includeRadius : str, optional
        A flag that specifies if rebar bend radius should be included in the
        output class. The default is False.
    dstir : str, optional
        The diamter of the stirrup. If it is not provided, and the section has 
        stirrups, the section's stirrup diameter is used. The default is None.
        If this is provided, the diameter of rebar in the section is ignored.
    lUnit : str, optional
        The length units for the output config. The default is 'mm'.

    Returns
    -------
    RebarSpacingConfig
        The configuration object containing the rebar spacing information.
    """
    
    
    section = element.getSection(sectionInd)
    cover   = element.designProps.cover
        
    return getSectionSpacingRules(rebar, section, cover, includeRadius, 
                                  dstir, lUnit)

   
# =============================================================================
# Shear
# =============================================================================
   
    
def getAsmin(fc: float, fy: float, bt: float, h: float):
    """
    Returns the minimum steel needed for general compression members
    according to c.l. 10.5.1.2, for slabs and footings refer to c.l. 7.8.
    Expects inputs in units of mm and MPa, outputs in sqmm.
    
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
        The minimum required steel in mm.

    """
    
    return 0.2 * (fc)**0.5 / fy * bt * h

def getSectionAsmin(section: SectionConcrete, fy: float = None):
    """
    Returns the Asmin for a concrete section, assuming it is not a footing
    or slab. Uses CSA A23.3 Cl.10.5.1.2.
    
    Currently only applies to rectangular sections.
        
    If no fy is provided, the section's rebar will be used for fy. If the 
    section has no rebar, a default value of 400MPa is used. 

    Returns in units of sqmm   
    
    Parameters
    ----------
    section : SectionConcrete
        The section to use in the calculation.
    fy : float
        The specified steel strength in MPa. The default is None, which uses
        the rebar in the section.

    Returns
    -------
    float
        The minimum required steel in mm.
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

def getdveff(d: float, h: float):
    """
    Gets the code effective shear depth of a beam, which is 0.9 of the distance
    of the beam to the centroid of longditudinal reinforcement. 
    Assumes inputs are in mm, and returns in mm.

    Parameters
    ----------
    d : float
        The distance from the compression edge to the centroid of the
        rebar in the direction of interest.
    h : float
        The depth of the section in the direction of interst.

    Returns
    -------
    float
        The effective shear depth, given a shear depth and a section height.
        Returns in mm.

    """
    return max(0.9*d, 0.72*h)

def getSectiondveff(section: SectionConcrete, yDir: bool = True, 
                    posDir: bool = True, 
                    dEst: float = None, 
                    NAlocation:float = None):
    """
    Gets the code effective shear depth of a beam, which is 0.9 of the distance
    of the beam to the centroid of longditudinal reinforcement. 
    Assumes inputs are in mm, and returns in mm.   

    Parameters
    ----------
    section : SectionConcrete
        The section to use in the calculation.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.
        
        If set to true, then the NA will be measured from the "bottom" of the
        section, which will be assumed to be in compression.
        
        The default is True.
    dEst : float, optional
        An manual estimate for d. If set, will overwrite the given d.
        The default is None, which causes no action to be taken.
    NAlocation : float, optional
        A manual overwrite, which can be used to specify the neutral axis
        location. This is used to determine which bars should be used
        when calculating deff. By default, the centerline of the beam is
        used. This will exclude top bars, but may include skin reinforcing 
        if there is any.

    Returns
    -------
    float
        The effective shear depth.

    """
    lUnit = 'mm'
    
    # Manual override to dv
    if dEst:
        d = dEst
    
    # if the rebar has not been set and there is no manual override, 
    # raise exception
    elif not section.rebar:
        raise Exception("Rebar in section has not been placed, and no dv"\
                        "estimate is given, dv cannot be calcualted.")
    # Calculate dv, this is the normal thing that happens. 
    else:
        d = section.getdeff(yDir, posDir, NAlocation, lUnit)
        # d = section.getRebarMaxDepth(yDir, posDir, lUnit)
        
    h  = section.getDepth(yDir, lUnit)
    return getdveff(d, h)
    
def getShearBeta(shearEnum: ShearConfigurations, dv: float = None) -> float:
    """
    A helper function used to get beta, the shear resistance factor
    for cracked concrete, given a shear configuration.
    See A23.3 EQ 11.9

    Parameters
    ----------
    shearEnum : ShearConfigurations
        The type of shear reinforcement present.
    dv : float, optional
        The effective depth of the longditudinal reinforcement. 
        The default is None.

    Returns
    -------
    float
        The beta value for the section.

    """
    
    if shearEnum == ShearConfigurations.MinTransverse:
        beta = 0.18
    elif shearEnum == ShearConfigurations.NoTransverse:
        if dv is None:
            raise Exception("dv is needed if no transverse reinforcemnt is provided")
        beta = (230) / (1000 + dv)
    elif shearEnum == ShearConfigurations.NoTransverseAmax20:
        raise Exception('Not implimented')
    return beta

def getElementVrc(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yDir: bool = True, posDir: bool = True, 
                 dEst: float = None) -> float:
    """
    Returns the shear capacity of the concrete in a concrete section, according
    to c.l. 11.3.4.
    
    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.        
        The default is True.
    dEst : float, optional
        An manual estimate for d. If set, will overwrite the given d.
        The default is None, which causes no action to be taken.

    Returns
    -------
    float
        The shear resitance of the concrete in a concrete section in N.

    """

    section = element.getSection(sectionInd)
    lam     = element.designProps.lam

    shearENum = element.designProps.shearReinforcementType
    
                        
    bw = section.getWidth(yDir)
    dveff = getSectiondveff(section, yDir, posDir, dEst = dEst)
    beta  = getShearBeta(shearENum, dveff)
    
    fc = section.concrete.mat.fc

    return getVrc(lam, beta, fc, bw, dveff)

def getVrc(lam: float, beta: float, fc: float,
          bw: float, dv: float):
    """
    Returns the shear capacity of the concrete in a concrete section, according
    to c.l. 11.3.4.

    Parameters
    ----------
    lam : float, optional
        The concrete density factor. Taken as 1 for normal density concrete.
        See c.l. 8.6.5
    beta : float
        The shear resistance factor, see A23.3 EQ 11.9.
    fc : float
        The specified concrete strength in MPa.
    bw : float
        The shear width in mm.
    dv : float
        The effective shear depth of the beam in mm.

    Returns
    -------
    float
        The shear resitance of the concrete in a concrete section in N.

    """

    return phiC * lam * beta * fc**0.5 * bw * dv

def getElementVrs(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yDir: bool = True, posDir: bool = True)  -> float:
    """
    Returns the steel strength in N for a section in a concrete element.
    
    Theta is taken from the design propreties, and should be set according
    to c.l. 11.3.6.3 if it hasn't already been.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.

    Returns
    -------
    float
        The steel strength for a section in a concrete element, in N.
    """
    section = element.getSection(sectionInd)
    theta   = element.designProps.theta

    mat = section.stirrups.mat
    sConvert = mat.sConvert('MPa')    
    fy       = mat.fy * sConvert
    
    
    
    Av = section.stirrups.getAvNet()
    s  = section.stirrups.getSpacing()

    dveff = getSectiondveff(section, yDir, posDir)
   
    return getVrs(Av, fy, dveff, theta, s)

def getVrs(Av: float, fy: float, dv: float, theta: float, s: float) -> float:
    """    

    Returns the Vrs, i.e. the steel strength for a concrete 
    section using the simplified method. See c.l. 11.3.4. and 
    c.l. 11.3.6.3 for theta.
    

    Parameters
    ----------
    Av : float
        The area per leg of stirrup in sqmm.
    fy : float
        The rebar yield stress in MPa.
    dv : float
        The shear depth of the concrete section in the direction of interst, in mm.
    theta : float
        The angle of diagonal compressive stresses, see c.l. 11.3.6.3
    s : float
        The spacing of the stirrups.

    Returns
    -------
    float
        The steel strength for a concrete section.
    """

    return phiS * Av * fy * dv / (tan(theta) * s)

def getElementSminForVrs(element: BeamColumnConcreteCsa24, Vrs: float, 
                         sectionInd: int = 0, barType: str = '10M', 
                         Nlegs: int = 2, dEst = None,
                         yDir: bool = True, 
                         posDir: bool = True)  -> float:
    """
    Returns the minumum shear spacing for an element
    
    Theta is taken from the design propreties, and should be set according
    to c.l. 11.3.6.3 if it hasn't already been.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    Vrs : float
        The factored shear resistance in N.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    barType : str, optional
        The type of bar to place e.g. 15M. The default is '10M'.
    Nlegs : int, optional
        The number of legs per stirrup. The default is 2.
    dEst : float, optional
        An manual estimate for d. If set, will overwrite the given d.
        The default is None, which causes no action to be taken.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.

    Returns
    -------
    float
        The minimum shear spacing in mm.

    """
    section = element.getSection(sectionInd)
    theta   = element.designProps.theta
        
    rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
    Av = rebar.A * Nlegs
    fy = rebar.mat.fy
    Av = Nlegs * rebar.A


    dveff = getSectiondveff(section, yDir, posDir, dEst=dEst)
   
    return getSminForVrs(Av, fy, dveff, theta, Vrs)

def getSminForVrs(Av: float, fy: float, dv: float, theta: float, Vs: float) -> float:
    """    

    Re-arranges to determine a required shear force, Vs, given a shear area.
    
    Uses c.l. 11.3.4. and take Theta from c.l. 11.3.6.3
    

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
        The required Vs of the stirrups in N

    Returns
    -------
    float
        The required spacing for Vs, in mm.
    """

    return phiS * Av * fy * dv  / (Vs * tan(theta))

def getVmax(fc: float, bw: float, dveff: float) -> float:
    """
    Calculates the maximum shear a section can resist from 
    A23.3 c.l. 13.3.3.

    Parameters
    ----------
    fc : float
        The specified shear strength for the section in MPa.
    bw : float
        The shear width of the section in mm.
    dveff : float
        The effective shear depth for the section..

    Returns
    -------
    float
        The output maximum shear, in N.

    """
    
    return 0.25 * phiC * fc * bw * dveff

def getElementVmax(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yDir: bool = True, posDir: bool = True,
                 dEst: float = None):
    """
    Gets the maximum shear capacity of a section.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.        
        The default is True.
    dEst : float, optional
        An manual estimage for d. If set, will overwrite the given d.

    Returns
    -------
    float
        The maximum shear strength for the section in N

    """
    
    section = element.getSection(sectionInd)

    dveff = getSectiondveff(section, yDir, posDir, dEst)
    bw = section.getWidth(yDir)
    
    sConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * sConvert
    return getVmax(fc, bw, dveff)

def getElementVr(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                 yDir: bool = True, posDir: bool = True,
                 dEst: float = None):
    """
    Returns the total Vr for a section, which considers both steel and concrete
    shear.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.

    Returns
    -------
    float
        The shear cpacity for the section in N.
    """
    section = element.getSection(sectionInd)
    lam     = element.designProps.lam
    theta   = element.designProps.theta


    scConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * scConvert    
    
    bw = section.getWidth(yDir)
    dveff = getSectiondveff(section, yDir, posDir, dEst)
   
    shearENum = element.designProps.shearReinforcementType
    beta  = getShearBeta(shearENum, dveff)   
   
    Vrc = getVrc(lam, beta, fc, bw, dveff)

    
    if     section.stirrups and section.stirrups.mat:
        srConvert = section.stirrups.mat.sConvert('MPa')
        fy = section.stirrups.mat.fy * srConvert
        
        Av = section.stirrups.getAvNet()
        s  = section.stirrups.getSpacing()
    
        Vrs = getVrs(Av, fy, dveff, theta, s)
    else:
        Vrs = 0


    return Vrs + Vrc

# =============================================================================
# Shear Spacing
# =============================================================================

def getSmaxGeom(dveff: float, Vf: float = 0, Vrmax: float = 0) -> float:
    """
    The maximum spacing possible, limited by geometry, i.e. c.l. 11.3.8.1. 
    Outputs in mm.
    
    If the applied force is greater than half of Vrmax, then tighter spacing
    of stirrups is required.

    Parameters
    ----------
    dveff : float
        The effective shear depth in mm.
    Vf : float, optional
        The applied force on the section in N. The default is 0.
    Vrmax : float, optional
        The maximum resistance of the section in N. The default is 0.

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
                     yDir: bool = True, posDir: bool = True, 
                     dEst: float = None,
                     Vf: float = 0, Vrmax: float = 0):
    """
    The maximum spacing possible, limited by geometry, i.e. c.l. 11.3.8.1. 
    Outputs in mm.
        
    If the applied force is greater than half of Vrmax, then tighter spacing
    of stirrups is required.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.        
        The default is True.
    dEst : float, optional
        An manual estimate for d. If set, will overwrite the given d.
        The default is None, which causes no action to be taken.
    Vf : float, optional
        The applied force on the section in N. The default is 0.
    Vrmax : float, optional
        The maximum resistance of the section in N. The default is 0.

    Returns
    -------
    float
        The output in mm for the maximum spacing, limited by geometry.

    """
    section = element.getSection(sectionInd)

    dveff = getSectiondveff(section, yDir, posDir, dEst)

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
        The width of the section at the shear.
    s : float
        The spacing of the stirrups.
    fy : float
        The yield strength of the rebar.

    Returns
    -------
    float
        The minimum area required for shear reinforcement.

    """

    Avmin = 0.06 * (fc)**0.5 * (bw * s / fy)
    
    return Avmin
       
def getStirrupSmax(fc: float, bw: float, fy: float, Av: float) -> float:
    """
    Calculates the minimum shear spacing required for a given shear area, by
    rearranging A23.3 c.l. 11.2.8.2
    
    Generally used to calculate the maximum spacing that a given set of rebar
    can be placed at.

    Parameters
    ----------
    fc : float
        The applied concrete strength in MPa.
    bw : float
        The width of the section at the shear.
    fy : float
        The yield strength of the rebar.
    Av : float
        The spacing of the stirrups.
        
    Returns
    -------
    float
        The maximum spacing permitted, limited by force.

    """

    sMin = (Av * fy) / (0.06 * (fc)**0.5 * bw )
    
    return sMin
       
def getElementSmaxStirrup(element: BeamColumnConcreteCsa24, 
                          sectionInd: int = 0, barType: str = '10M', 
                          Nleg: int = 2, fy = 400, yDir = True):
    """
    Calculates the minimum shear spacing required for a given shear area, by
    rearranging A23.3 c.l. 11.2.8.2
    
    Generally used to calculate the maximum spacing that a given set of rebar
    can be placed at.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    barType : str, optional
        The type of bar to place e.g. 15M. The default is '10M'.
    Nleg : int, optional
        The number of legs each stirrup has. Currently only two legs are 
        supported per stirrup.
    fy : float, optional
        The specified steel strength in MPa. The default is 400MPa.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.

    Returns
    -------
    float
        The maximum shear spacing permitted for a section, using units of 
        force.

    """
    
    section = element.getSection(sectionInd)

    scConvert = section.concrete.mat.sConvert('MPa')
    fc = section.concrete.mat.fc * scConvert    
        
    bw = section.getWidth(yDir)
    
    rebar = REBARFACTORY.getRebar(barType, lUnit = 'mm')
    Av = rebar.A * Nleg
  
    return getStirrupSmax(fc, bw, fy, Av)

def getElementSmax(element: BeamColumnConcreteCsa24, sectionInd: int = 0,
                   barType: str = '10M', Nleg: int = 2, fy = 400,
                     yDir: bool = True, posDir: bool = True, 
                     dEst: float = None, Vf: float = 0, Vrmax: float = 0):
    """
    Returns the maximum specing permitted, considering both geometry and
    strength.
    
    Strength is calculated by rearranging A23.3 c.l. 11.2.8.2, see 
    'getElementSmaxStirrup'
    
    Geometry is calculated by 11.3.8.1. Outputs in mm.

    Parameters
    ----------
    element : BeamColumnConcreteCsa24
        The element to get the strength of.
    sectionInd : int, optional
        The index of the section used to place rebar in. The default is 0, 
        which is the first section / only section if there is just one section.
    barType : str, optional
        The type of bar to place e.g. 15M. The default is '10M'.
    Nleg : int, optional
        The number of legs each stirrup has. Currently only two legs are 
        supported per stirrup.
    fy : float, optional
        The specified steel strength in MPa. The default is 400MPa.
    yDir : bool, optional
        A flag that specifies if the direction of interest is in the 
        sections vertical (y) direction. The default value is true, leading
        to vertical outputs, i.e. y axis outputs.
    posDir : bool, optional
        A flag that specifies if force should be positive or negative. 
        Positive is defined as force or moment that creates tension at the 
        "bottom" of the beam. e.g. a simply supported beam has positive 
        bending, a downards shear force is positive.        
        The default is True.
    dEst : float, optional
        An manual estimate for d. If set, will overwrite the given d.
        The default is None, which causes no action to be taken.
    Vf : float, optional
        The applied force on the section in N. The default is 0.
    Vrmax : float, optional
        The maximum resistance of the section in N. The default is 0.

    Returns
    -------
    float
        The maximum specing permitted in mm.

    """

    S1 = getElementSmaxStirrup(element, sectionInd, barType, Nleg, fy, yDir)
    S2 = getElementSmaxGeom(element, sectionInd, yDir, posDir, 
                            dEst, Vf, Vrmax)
    
    return min(S1, S2)
