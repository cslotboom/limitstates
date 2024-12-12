"""
Contains functions for managing sections specific to CSAo86-19

Note, right now all limits are calculated at once BEFORE the 
"""

from .element import BeamColumnSteelCsa24
from limitstates import SectionSteel, SteelSectionTypes, DesignDiagram
from typing import Callable
from numpy import pi, cumsum
from enum import IntEnum

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



def _checkType(section):
    SUPPORTEDTYPES = ['W', 'HSS']

    if section.type not in SUPPORTEDTYPES:
        _SectionUnsupporedError(section, SUPPORTEDTYPES)

def _SectionUnsupporedError(secton, SUPPORTEDTYPES):
        raise Exception(f'Section of type {secton.type} not supported, expected one of {SUPPORTEDTYPES}')
# =============================================================================
# 
# =============================================================================



def checkElementSlenderness(element:BeamColumnSteelCsa24, useX = True):
    """
    Checks the slenderness ratio of a steel element.

    Parameters
    ----------
    rx : float
        The radius of gyration for the section.
    Lx : float
        The design length of teh section.
    Kx : float, optional
        The buckling effective length factor. The default is 1.0.

    Returns
    -------
    slenderness : float
        The output slenderness of the section.

    """
    
    lconvert    = element.member.lConvert('mm')
    lsconvert   = element.section.lConvert('mm')
    
    if useX:
        L = element.designProps.Lx * lconvert
        k = element.designProps.kx
        r = element.section.rx * lsconvert
    else:
        L = element.designProps.Ly  * lconvert
        k = element.designProps.ky
        r = element.section.ry* lsconvert

    return checkSlendernessRatio(r, L, k)



def checkSlendernessRatio(r:float, L:float, K:float=1.0) -> (bool, float):
    """
    Checks the slenderness ratio of a steel element.

    Parameters
    ----------
    rx : float
        The radius of gyration for the section.
    Lx : float
        The design length of teh section.
    Kx : float, optional
        The buckling effective length factor. The default is 1.0.

    Returns
    -------
    slenderness : float
        The output slenderness of the section.

    """

    return K*L/r


# =============================================================================
# Tension
# =============================================================================


def checkTg(Ag, Fy):
    """
    Get the yield capacity for the goss section using c.l. 13.2

    Parameters
    ----------
    Ag : float
        The sections area in mm.
    Fy : float
        The yield capacity of the section in MPa.

    Returns
    -------
    Tg : float
        The gross tension capacity of the section..

    """
    
    phi = 0.9
    return phi*Ag*Fy


# TODO! Test
def checkTgElement(beam:BeamColumnSteelCsa24):
    """
    Uses c.l. 13.4.1.1 To calculate the Fs for a W section.
    
    Inputs are in mm and MPa.
    
    Force out is in N.

    Parameters
    ----------
    h : float
        The clear depth of the web between flanges of the flange.
    tw : float
        The thickness of the web of the flange.
    Fy : float
        The yield stress for the material used.

    Returns
    -------
    Fs : TYPE
        DESCRIPTION.

    """
    section = beam.section
    lconvert = section.lConvert('mm')
        
    sfactor = section.mat.sConvert('MPa')
    Fy      = section.mat.Fy*sfactor
    
    A = section.A * lconvert**2
        
    return checkTg(A, Fy)


# =============================================================================
# Bending
# =============================================================================

def classifySection(section:SectionSteel, useX=True, Cf = 0):
    """
    Used to classify a section, returning the worst case section class for 
    the flange and web. Currently only applies 
    
    Class 4 sections are not supported.

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of.
    useX : bool, optional
        A flag that specifies if the x axis (strong axis) should be used. 
        The default is True.
    Cf : float, optional
        The force acting on the section in N. The default is 0.

    Returns
    -------
    section class : int
        The worst case between the section class and web class.

    """

    _checkType(section)

    if section.typeEnum == SteelSectionTypes.w:
        cflange = classifyFlangeWSection(section, useX)
        cweb    = classifyWebWSection(section, useX, Cf)
        return max(cflange, cweb)
    elif section.typeEnum == SteelSectionTypes.hss:
        cflange = classifyFlangeHssSection(section, useX)
        cweb    = classifyWebHssSection(section, useX, Cf)
        return max(cflange, cweb)
    else:
        raise Exception(r'Section {section.type} not supported')
    

def classifyFlangeWSection(section:SectionSteel, useX = True):
    """
    Used to classify the flange of a W section.
    
    Class 4 sections are not supported.

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of.
    useX : bool, optional
        A flag that specifies if the x axis (strong axis) should be used. 
        The default is True.

    Returns
    -------
    section class : int
        The flange section class

    """
    
    
    # section.mat.sConvert()
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')
    t   = section.tf
    bel = section.bf / 2
    
    if useX:
        return classifyFlangeW(bel, t, Fy)
    else:
        return classifyFlangeWMinor(bel, t, Fy)
    
def classifyWebWSection(section:SectionSteel, useX = True, Cf:float= 0):
    """
    Used to classify a W section's web. See #11.3.2.c.
    
    Class 4 sections are not supported.

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of.
    useX : bool, optional
        A flag that specifies if the x axis (strong axis) should be used. 
        The default is True.
    Cf : float, optional
        The force acting on the section in N. The default is 0.

    Returns
    -------
    section class : int
        The web section class.

    
    """
    
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')
    t   = section.tw
    h   = section.d -  section.tf*2
    Cy  = section.Cy
    
    if useX:
        return classifyWebWMajor(h, t, Fy, Cf, Cy)
    else:
        return classifyWebWMinor(h, t, Fy, Cf, Cy)



def classifyWebHssSection(section:SectionSteel, useX = True, Cf:float= 0):
    """
    Classifys a HSS web. The web is the portion of hss the which is in both 
    compression and tension.
    
    If useX is toggled true the web is the vertical edge, i.e. height. 
    Otherwise it's the horizontal edge, i.e. width.
    Assumes that the section is supported along two edges, and has bending
    and compression.
    
    
    see #11.3.2.c. for a definittion of h
    
    Parameters
    ----------
    section : SectionSteel
        The section to classify.
    useX : bool, optional
        A toggle that activates the X direction. The default is True.
    Cf : float, optional
        The factored compression force of the section in N. The default is 0.

    Returns
    -------
    int
        The section class.

    """
    
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')
    t   = section.t
    Cy  = section.Cy
    
    if useX:
        h   = section.h -  t*4
    else:
        h   = section.b -  t*4
    return classifyWebWMajor(h, t, Fy, Cf, Cy)
        

def _getBelHSSSection(section:SectionSteel, useX = True):
    """
    see #11.3.2.b. for a definition of bel    
    """
    
    
    # In the strong axis, use the section 
    if useX:
        return  section.b -  section.t*4
    else:
        return  section.d -  section.t*4

def classifyFlangeHssSection(section:SectionSteel, useX = True):
    """
    Classifys a HSS flange
    
    If useX is toggled true the web is the vertical edge, i.e. height. 
    Otherwise it's the horizontal edge, i.e. width.
    Assumes that the section is supported along two edges, and has bending
    and compression.
    
    
    see #11.3.2.b. for a definittion of bel    
    
    Parameters
    ----------
    section : SectionSteel
        The steel section to classify.
    useX : TYPE, optional
        A toggle that activates the X direction. The default is True.
    Cf : float, optional
        The factored compression force of the section in N. The default is 0.

    Returns
    -------
    int
        The section class.

    """
    
    Fy  = section.mat.Fy * section.mat.sConvert('MPa')

    # units are not needed because bel and t divide eachother.
    t   = section.t
    bel = _getBelHSSSection(section,useX)
    
    return classifyHssRectFlange(bel, t, Fy)
        
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
    
    See c.l. 11.3.2.b. for a definition of bel    
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
    
    See c.l. 11.3.2.b. for a definition of bel    

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
    Assumes that the section is supported along two edges, and has bending
    and compression.
    Table 1
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
    From Table 2
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


def classifyHssRectFlange(bel, t, Fy):
    """
    Classify a square or rectangular HSS section for bending about an axis. 
    The flange is the portion of the section which is fully in compression.
        
    Parameters
    ----------
    bel : float
        The effective width, factoring in the curvature of the HSS
        See c.l. 11.3.2.b. for a definition of bel    

    t : float
        The wall thickness in mm.
    Fy : float
        The yield stress in MPa.

    Returns
    -------
    float
        The class for the flange.

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


def getOmega2(Mmax, Ma, Mb, Mc):
    """
    Omega is a load amplification factor
    """
    
    return min(4 * Mmax / (Mmax**2 + 4*Ma**2 + 7*Mb**2 + 4*Mc**2), 2.5)

        
def getOmega2Linear(Mmax, Mmin):
    """
    For approximately linearly varying loads 13.6.1.a
    """

    kappa = Mmin / Mmax
    return min(1.75 + 1.05*kappa + 0.3*kappa**2, 2.5)



def getMp(Z, Fy):
    """
    Assumes Z and Fy are in mm3 and MPa
    Returns in Nm
    """
    
    phi = 0.9
    return Z*Fy*phi / 1000
    
def getMy(S, Fy):
    """
    Assumes Z and Fy are in mm3 and MPa
    Returns in Nm
    """
    
    phi = 0.9
    return S*Fy*phi / 1000
    
def checkBeamMrSupported(beam:BeamColumnSteelCsa24, useX:bool=True, Cf:float = 0):
    """
    Calcualtes Mr for a supported member in Nm.
    For laterally supported members, Mr is calculated the same way for HSS and
    W sections. The only exception is class 4 sections, which are not supported
    by limitstates currently.
    
    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The beam to check the capacity of.
    useX : TYPE, optional
        A toggle that activates the X direction. The default is True.
    Cf : float, optional
        The factored compression force of the section in N. The default is 0.


    Returns
    -------
    float
        The capacity of the beam in N*m.

    """

    section = beam.section
    _checkType(section)
    
    sectionClass = _getSectionClassIfNotSet(section, useX, Cf)
    Fy = section.mat.Fy * section.mat.sConvert('MPa')
    
    if sectionClass <=2:
        Z = section.getZ(useX, 'mm')
        return getMp(Z, Fy) 
    elif sectionClass <=3:
        S = section.getS(useX, 'mm')
        return getMy(S, Fy) 
    else:
        raise Exception(f'{section} recieved is class 4, limitstates currently cannot design class 4 sections.')   
    
def checkBeamMrUnsupportedW(beam:BeamColumnSteelCsa24, omega:float=1, 
                            Lu:float = None, Cf = 0):
    """
    Calculates Mr for an unsupported W section according to c.l.13.6.1.a.
    Does not apply to cantilevers.
    Note that in the weak axis, the unsupported strength is equal to the
    supported strength
    
    For loads applied to a top flange, Mu can be calculated with omega = 1
    and Lu = 1.2 for simply supported members, and Lu = 1.4 for other member
    types.
    The user should set the length of the beam
    
    These can be modified by changing the keff factor in the x direction

    Parameters
    ----------
    section : SectionSteel
        A W section.
    omega : float, optional
        The moment distribution factor. The default is 1.
    Lu : float
        An override for the unbraced length in mm.
        By defult is none, which will use the design length of the beam in 
        it's x direction.
    Cf : float, optional
        The factored compression force of the section in N. The default is 0.

    Returns
    -------
    float
        The capacity of the beam in N*m.

    """
    # sectionClass = _getSectionClassIfNotSet(beam.sectionsection, True, Cf)
    
    # if 
    
    if not Lu:
        lconvert = beam.member.lConvert('mm')
        Lu = beam.designProps.Lx * beam.designProps.kx * lconvert
    
    phi = 0.9
    Mu = checkSectionMu(beam.section, Lu, omega)*phi
    Mx = checkBeamMrSupported(beam, True, Cf)
    
    if 0.67*Mx < Mu:
        return min(1.15*Mx*(1 - 0.28*Mx / Mu), Mx)

    else:
        return Mu 

    
def checkBeamMrUnsupported(beam:BeamColumnSteelCsa24, omega2:float=1, 
                            Lu:float = None, Cf = 0):
    """
    Calculates Mr for an unsupported W section according to c.l.13.6.1.a.
    Does not apply to cantilevers.
    Note that in the weak axis, the unsupported strength is equal to the
    supported strength
    For Hss sections, the unsupported results are the same as the supported
    results.
    
    For loads applied to a top flange, Mu should be calculated with omega = 1
    and Lu = 1.2 for simply supported members, and Lu = 1.4 for other member
    types.
    
    These can be modified by changing the keff factor in the x direction

    Parameters
    ----------
    section : SectionSteel
        A W section.
    omega : float, optional
        The moment distribution factor. The default is 1.
    Lu : float
        An override for the unbraced length in mm.
        By defult is none, which will use the design length of the beam in 
        it's x direction.

    Returns
    -------
    float
        The capacity of the beam in N*m.

    """
    
    if beam.section.typeEnum == SteelSectionTypes.w:
        return checkBeamMrUnsupportedW(beam, omega2, Lu, Cf)

    elif beam.section.typeEnum == SteelSectionTypes.hss:
        return checkBeamMrSupported(beam,  Cf = Cf)

    else: 
        raise Exception(f'Section type {beam.section.type} is unsupported' )


# !!! This might not be the correct place to store the section class.
def _getSectionClassIfNotSet(section:SectionSteel, 
                             useX:bool = True, Cf:float = 0):
        
    if not section.sectionClass:
        sectionClass = classifySection(section, useX, Cf=Cf)
    else:
        sectionClass = section.sectionClass 
    return sectionClass

def checkSectionMu(section:SectionSteel, Lu:float, omega:float):
    """
    Calculates Mu, the laterally unsupported buckling moment, 
    as per c.l. 13.6.1.a, assuming length is input in mm.
    
    Returns capacity in N*m

    Parameters
    ----------
    section : SectionSteel
        The steel section to check.
    Lu : float
        The input length in mm.
    omega : float
        The omega factor to apply to the span..

    Returns
    -------
    float
        The buckling moment for the beam.

    """

    lfactor = section.lConvert('mm')
    sfactor = section.mat.sConvert('MPa')

    E = section.mat.E * sfactor
    G = section.mat.G * sfactor
    
    Iy = section.Iy * lfactor**4
    J  = section.J  * lfactor**4
    Cw = section.Cw * lfactor**6
    
    return checkMu(E, Iy, G, J, Cw, Lu, omega) / 1000

def checkMu(E:float, Iy:float, G:float, J:float, Cw:float, Lu:float, 
            omega:float):
    """
    Calculates critical bucklimg moment for a beam.

    Parameters
    ----------
    E : float
        The elastic modulus of the section in MPa.
    Iy : float
        The weak axis moment of inetia in mm4.
    G : float
        The shear modulus of the section in MPa.
    J : float
        The polar moment of enrtia for the section in mm4.
    Cw : float
        The warpping torsion constant in mm6 (mm$^6$).
    Lu : float
        The unsupported length of the beam for bending in the strong axis in 
        mm.
    omega : float
        The omega load factor.

    Returns
    -------
    float
        Mu for the element.

    """
    return (omega*pi / Lu) * (E*Iy*G*J + Iy*Cw*(pi*E/Lu)**2)**0.5


def checkOmega(Mmax, Ma, Mb, Mc):
    
    return min(4 * Mmax / (Mmax**2 + 4*Ma**2 + 7*Mb**2 + 4*Mc**2)**0.5, 2.5)
    

# =============================================================================
# Multispan
# =============================================================================



class SegmentSupportTypes(IntEnum):
    """
    Options for multispan design checks:
        - If option 1 is selected, the beam is assumed to be continously laterally 
          supported over the entire beam. Note, Mr is the same for each segment.
        - If option 2 is selected, the beam is assumed to be laterally unsupported 
          between supports. In this case, it is assumed the load is applied to the 
          compression flange, and torsional fixity is provided at each support. 
          For W sections, the length is increased by 1.4 per c.l. 13.6.1.
        - If option 3 is selected, then the design propreties will be used to.
          The user should manually set the attributed Lx, kx, and lateralSupport
          in the designpropreties. Note, in this case Lx should be the actual length 
          (Not a design length), and kx should be the effective lenght factor.

    """
    continuous = 1
    supoorts = 2
    supportsAndTopFlange = 3
    manual = 4

def _getOmegas(bmd, Nspan, Lsegs):
    
    omegas = [None]*Nspan

    x1 = x2 = 0
    for ii in range(Nspan):
        dx  = Lsegs[ii]
        x2 = x1 + dx
        xa = 0.25*dx + x1
        xb = 0.5*dx + x1
        xc = 0.75*dx + x1
        
        ya, yb, yc = bmd.getForceAtx([xa, xb, xc])
        ymax = bmd.getMaxForceInRange(x1, x2)
        omegas[ii] = checkOmega(ymax, ya, yb, yc)
        x1 = x2
        
    return omegas

def getOmega1FromDesignDiagram(bmd:DesignDiagram):
    """
    Returns the value of Omega1 from a bending moment diagram per c.l. 13.8.6.
    Assumes that the input bending moment diagram is for a single span.
    
    Linear interoplation is used to determing the y values used in the omega 
    equation.

    Parameters
    ----------
    bmd : DesignDiagram
        The bending moment diagram to check for Omega.

    Returns
    -------
    float
        The output value of omega.

    """
    x = bmd.xy[:,0]
    x1 = min(x)
    x2 = max(x)
    dx  = x2 - x1
    x2 = x1 + dx
    xa = 0.25*dx + x1
    xb = 0.5*dx + x1
    xc = 0.75*dx + x1
    
    ya, yb, yc = bmd.getForceAtx([xa, xb, xc])
    ymax = bmd.getMaxForceInRange(x1, x2)
    return checkOmega(ymax, ya, yb, yc)


def checkMrBeamMultiSpan(element: BeamColumnSteelCsa24, 
                         bmd: DesignDiagram = None, 
                         lateralSupportType: SegmentSupportTypes | int = 3):
    """
    Returns the Mr value for each region of a multiSpanBeam.
    Each span is given a value for Mr.
    
    The beam is assumed to bend about it's strong axis.

    Assumes the BMD and member have the same units for length. The designer 
    must judge the torsional support conditions provided and select an option
    as per below:
        1, the beam is assumed to be continously laterally supported over the 
        entire beam. Where there are regions of siginficant negative bending, 
        the bottom chord of the stucture must also be continously braced.
        
        2, the beam is assumed to be laterally unsupported between supports, 
        **the load is applied to the at the shear center**, and torsional 
        fixity is provided at each support. Omega is calculated per the BMD.
    
        3, the beam is assumed to be laterally unsupported between supports, 
        **the load is applied to the top chord**, and torsional fixity is 
        provided at each support. 
        For W sections, the length is increased by 1.4 per c.l. 13.6.1.,
        and omega is set to be equal to one.
        
        4, The user should manually set the attributed Lx, kx, and 
        lateralSupportin the designpropreties. Note, in this case Lx should be 
        the actual length (Not a design length), and kx should be the 
        effective lenght factor.
        Lu = Lx * kx
        
    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The multi-span element to check.
    bmd : DesignDiagram
        The bending moment diagram for the load case to be checked.
    lateralSupportType : SegmentSupportTypes | int, optional
        The type of lateral support condition for bending. The default is 3:
            
        - 1 will return a beam lateral restraint on all segments
        - 2 will return a beam with no lateral restraint except at supports
        - 3 will return a beam with no lateral restraint except at supports, 
          and load applied at the top flange.
        - 4 will use the user define support conditions. The Lx, kex, and 
        lateralSupport must be set for each beam segment
        
    Returns
    -------
    MrOut : list[float]
        The Mr out for each design segment.
    xOut : list[float]
        The breakpoints for the beam, including the end of the beam. Moment 
        applies, i.e.
        
        Mr = MrOut[0] from         0 to xOut[0]
        
        Mr = MrOut[1] from   xOut[0] to xOut[1]
    omega : list[float]
        The omega factor for each span.

    """
        
    mlfactor = element.member.lConvert('mm')
    
    if True in element.member.isCantilever:
        raise Exception('A cantilever was found in the input beam. Cantilevers are not currently supported.')
        
    # Get the positive and negative bending regions.
    member  = element.member

    # Get the kL factor depending on the condition used.
    if lateralSupportType == 1:
        Nspan = member.Nspan
        isContinouslyBraced = [True] * Nspan
        Lsegs    = [line.L for line in member.curves]
        Ldesign  = [-1]*Nspan
        omegas = [None]*Nspan
        
    if lateralSupportType == 2:
        Nspan = member.Nspan
        isContinouslyBraced = [False] * Nspan
        
        Lsegs   = [line.L for line in member.curves]
        Ldesign = [L*mlfactor for L in Lsegs]
        omegas = _getOmegas(bmd, Nspan, Lsegs)
        
    if lateralSupportType == 3:
        Nspan = member.Nspan
        isContinouslyBraced = [False] * Nspan
        
        Lfactor = 1.4
        Lsegs    = [line.L for line in member.curves]
        Ldesign    = [L*Lfactor*mlfactor for L in Lsegs]
        omegas   = [1]*Nspan
        
    if lateralSupportType == 4:
        
        dProps = element.designProps
        Nspan  = len(dProps.Lx)
        isContinouslyBraced = dProps.lateralSupport
        Lsegs    = dProps.Lx
        Ldesign  = [L * kx * mlfactor for kx, L in zip(dProps.kx, Lsegs)]
        
        omegas = _getOmegas(bmd,Nspan,Lsegs)

    MrOut = [None]* Nspan
    for ii in range(Nspan):
        spanSupport = isContinouslyBraced[ii]
        L = Ldesign[ii]
        if spanSupport:
            Mr = checkBeamMrSupported(element)
        else:
            omega = omegas[ii]
            Mr = checkBeamMrUnsupported(element, omega, L)
        MrOut[ii] = Mr
    
    xOut = cumsum(Lsegs)
    return MrOut, xOut, omegas






# =============================================================================
# Shear
# =============================================================================

def getFsWUnstiffened(h:float, tw:float, Fy:float):
    """
    uses c.l. 13.4.1.1 To calculate the Fs for a W section.
    
    Inputs are in mm and MPa.
    
    Force out is in N.

    Parameters
    ----------
    h : float
        The clear depth of the web between flanges of the flange.
    tw : float
        The thickness of the web of the flange.
    Fy : float
        The yield stress for the material used.

    Returns
    -------
    Fs : TYPE
        DESCRIPTION.

    """
    
    ratio = h / tw
    
    sqrtFy = Fy**0.5
    
    r1 = 1014/sqrtFy
    if ratio <= r1:
        Fs = 0.66*Fy
    elif (r1 < ratio) and (ratio <= 1435/sqrtFy):
        Fs = 670*sqrtFy / ratio
    elif ratio <= 1014/sqrtFy:
        Fs = 961200 / (ratio)
        
    return Fs

def checkFsBeam(beam:BeamColumnSteelCsa24, Cf:float = 0):
    """
    Uses c.l. 13.4.1.1 To calculate the Fs for a W section or HSS.
    Only strong axis bending is supported
    
    Inputs are in mm and MPa.
    
    Force out is in N.

    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The beam to check the shear of.
    Cf : float
        The applied compressive load (N).
    Returns
    -------
    Fs : float
        The shear capacity of the beam in N.

    """
    phi = 0.9

    section = beam.section
    lfactor = section.lConvert('mm')

    if section.typeEnum == SteelSectionTypes.w:
        As, Fs = _getFsW(section, lfactor, beam.designProps.webStiffened)
    elif section.typeEnum == SteelSectionTypes.hss:
        
        sectionClass = classifySection(section, True, Cf)
        t = section.tw * lfactor            
        sfactor = section.mat.sConvert('MPa')
        Fy = section.mat.Fy*sfactor         
        
        if 3 <= sectionClass:
            # We need the width in the strong axis
            h = _getBelHSSSection(section, False)* lfactor
            As = 2 * h  * t
            Fs = getFsWUnstiffened(h, t, Fy)
        else:
            # NOTE: in weak axis loading these need to be swapped.
            As = section.A * section.d / (section.b + section.d) 
            Fs = 0.66*Fy         
    else:
        raise Exception('Member not yet supported for shear.')       
    return phi* Fs * As




def _getFsW(section, lfactor, isWebStiffened = False):

    sfactor = section.mat.sConvert('MPa')
    Fy = section.mat.Fy*sfactor    
    
    # Some section databases do not explicitly set this term
    if hasattr(section, 'ho'):
        h = section.ho * lfactor
    else:
        h = section.d - section.tf *2
        h *= lfactor
    
    tw = section.tw * lfactor            
    As = section.d  * lfactor * tw
    if isWebStiffened != True:
        Fs = getFsWUnstiffened(h, tw, Fy)
    else:
        raise Exception('Only unstiffned webs are currently supported.')    

    return As, Fs

# =============================================================================
# Compression
# =============================================================================

def checkCompressionLimits(section:SectionSteel):
    """
    Checks the column agains table 1 compression limits.


    Parameters
    ----------
    section : SectionSteel
        DESCRIPTION.

    Returns
    -------
    bool
        A pass/Fail depending on if the memeber passes or not.

    """

    _checkType(section)

    isW = section.typeEnum == SteelSectionTypes.w


    if isW:
        checkPasses = checkCompresionLimitsW(section)
    elif section.typeEnum == SteelSectionTypes.hss:
        checkPasses = checkCompresionLimitsHss(section)
    
    if checkPasses:
        return True
    else:
        raise Exception('Element is class 4 for compression. Check flange and web limits with Table 1.')


def _getCompressionLim(section:SectionSteel):
    sconvert = section.mat.sConvert('MPa')
    Fy = section.mat.Fy*sconvert
    return  1/Fy**0.5



def getCompressionThicknessRatioW(section:SectionSteel):
    """
    
    Check b/t rations for the flange and web of a W section in compression.
    
    See c.l. 11.3.2.b. for a definition of bel and h.

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of in compression

    Returns
    -------
    flangeRatio : float
        The ratio of bel divided by tflange.
    webRatio : float
        The ratio of h divided by tweb.

    """
        
    # flange propreties
    tf   = section.tf
    bel = section.bf / 2
    flangeRatio = (bel / tf)
    
    # Web propreties
    tw   = section.tw
    h   = section.d -  section.tf*2
    webRatio = (h / tw)     

    return flangeRatio, webRatio

def checkCompresionLimitsW(section:SectionSteel) -> bool:
    """
    Determines if a section complies with Table 1 for it's thickness to 
    depth ratios.
        
    See c.l. 11.3.2.b. for a definition of bel    

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of in compression
        
    Returns
    -------
    bool
        True if the section passes, false if it fails.

    """
    lim = _getCompressionLim(section)
    flangeLim = 250*lim
    webLim = 670*lim
    
    # flange/web propreties
    flangeRatio, webRatio = getCompressionThicknessRatioW(section)
    flangePasses = flangeRatio < flangeLim
    webPasses = webRatio < webLim

    if flangePasses and webPasses:
        return True
    else:
        return False


def getCompressionThicknessRatioHss(section:SectionSteel):
    """
    
    Check b/t rations for the flange and web of a Hss section in compression.
    
    See c.l. 11.3.2.b. for a definition of bel and h.

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of in compression

    Returns
    -------
    strongAxisRatio : float
        The ratio of bel divided by tflange.
    weakAxisRatio : float
        The ratio of h divided by tweb.

    """
        
    # flange propreties
    tf   = section.t
    belFange = _getBelHSSSection(section, True)
    
    strongAxisRatio = (belFange / tf)
    
    # Web propreties
    tw   = section.t
    belWeb = _getBelHSSSection(section, False)
    weakAxisRatio = (belWeb / tw)     

    return strongAxisRatio, weakAxisRatio

def checkCompresionLimitsHss(section:SectionSteel):
    """
    Determines if a section complies with Table 1 for it's thickness to 
    depth ratios.
        
    See c.l. 11.3.2.b. for a definition of bel    

    Parameters
    ----------
    section : SectionSteel
        The steel section to check the section class of in compression
        
    Returns
    -------
    bool
        True if the section passes, false if it fails.

    """
    
    lim = _getCompressionLim(section)
    strongAxisLim = weakAxislim = 670*lim    
    
    # flange/WEB propreties
    strongAxisRatio, weakAxisRatio = getCompressionThicknessRatioHss(section)
    flangePasses = strongAxisRatio < strongAxisLim
    webPasses = weakAxisRatio < weakAxislim

    if flangePasses and webPasses:
        return True
    else:
        return False
    
def checkCr(A:float, Fy:float, lamda:float, n:float = 1.34):
    """
    Calculates compression resistance per 13.3.1.1

    Parameters
    ----------
    A : float
        The sections area in sqmm.
    Fy : float
        The sections yield stress in MPa.
    lamda : float
        The ratio of yeld stress to the euler buckling stress.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.

    Returns
    -------
    float
        The compression resistance for the system in N.

    """

    phi = 0.9
    
    return phi*A*Fy / (1 + lamda**(2*n))**(1/n)
    

def checkFe(E:float, Leff:float, reff:float):
    """
    Calculates the euler buckling stress for a column in a given direction.
    
    Effective buckling stress per c.l. 13.3.1.2
    Leff is the effective buckling length, i.e. k*L
    
    """
    return pi**2 * E / (Leff/reff)**2


def getrBar(x0:float, y0:float, rx:float, ry:float):
    """
    Effective buckling stress per c.l. 13.3.1.2
        
    """
    
    return (x0**2 + y0**2 + rx**2 + ry**2)**0.5

def checkFez(E:float, Cw:float, Leff:float, G:float, 
             J:float, A:float, rbar:float):
    """
    Effective buckling stress per c.l. 13.3.1.2
    Leff is the effective buckling length, i.e. k*L
    all length units are the same.
    
    """
    return ((pi**2 * E * Cw ) / Leff**2 + G*J) / (A*rbar**2)


def checkColumnFeDirection(column:BeamColumnSteelCsa24, useX = True):
    """
    Calculates buckling stress in a single direction stress per 13.3.1.1
    
    Only applies to double symettric sections, i.e. W sections and
    HSS sections.
    Finds effective buckling stresses using 13.3.1.2

    
    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The structural element to check.
    useX :  bool, optional
        A flag that specifies the direction to check the column in. 
        The default is True, which checks the x direction.

    Returns
    -------
    float
        The buckling stress in MPa.

    """
    lconvert    = column.member.lConvert('mm')
    lsconvert   = column.section.lConvert('mm')
    
    sconvert = column.section.mat.sConvert('MPa')
    E = column.section.mat.E*sconvert
    
    if useX:
        Le = column.designProps.Lex * lconvert
        r  = column.section.rx * lsconvert
    else:
        Le = column.designProps.Ley * lconvert
        r  = column.section.ry * lsconvert
        
    return checkFe(E, Le, r)

def checkColumnCeDirection(column:BeamColumnSteelCsa24, useX = True):
    """
    Calculates buckling force (Fe*A) in a single direction stress per 13.3.1.1
    
    Only applies to double symettric sections, i.e. W sections and
    HSS sections.
    Finds effective buckling stresses using 13.3.1.2

    
    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The structural element to check..
    useX : TYPE, optional
        The x direction to check the column in. The default is True.

    Returns
    -------
    float
        The buckling force in N.

    """
    lsconvert   = column.section.lConvert('mm')
    A = column.section.A * lsconvert**2
    return checkColumnFeDirection(column, useX) * A

def checkColumnFeTorsion(beam:BeamColumnSteelCsa24, x0:float=0, y0:float=0):
    """
    Calculates the torsion bucking stress 13.3.1.1
    
    Only applies to double symetric sections, i.e. W sections and
    HSS sections.
    Finds effective buckling stresses using 13.3.1.2
    
    The variables x0 and y0 are the location of the shear center
    with respect tohte centroid of the cross section.
    
    kz, the buckling lenght for torsion, must be set in the member.
    
    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The structural element to check..
    useX :  bool, optional
        A flag that specifies the direction to check the column in. 
        The default is True, which checks the x direction.

    Returns
    -------
    float
        The buckling stress in MPa.

    """
    lsconvert = beam.section.lConvert('mm')
    rx  = beam.section.rx*lsconvert
    ry  = beam.section.ry*lsconvert
    
    sconvert = beam.section.mat.sConvert('MPa')
    E = beam.section.mat.E*sconvert
    
    lconvert = beam.member.lConvert('mm')
    Lez = beam.designProps.Lez*lconvert
    G   = beam.section.mat.G*sconvert
    Cw  = beam.section.Cw*lsconvert**6
    J   = beam.section.J*lsconvert**4
    A   = beam.section.A*lsconvert**2
        
    lsconvert = beam.section.lConvert('mm')
    rx  = beam.section.rx*lsconvert
    ry  = beam.section.ry*lsconvert

    rbar = getrBar(x0,y0,rx,ry)
    return checkFez(E, Cw, Lez, G, J, A, rbar)


"""
!!! There is code repetition in sub functions, e.g. we recall E several times
in each function.
"""

def checkColumnFe(beam:BeamColumnSteelCsa24):
    """
    Calculates buckling compression stress per 13.3.1.1
    
    Only applies to double symettric sections, i.e. W sections and
    HSS sections.
    
    Finds effective buckling stresses using 13.3.1.2
    
    kz, the buckling lenght for torsion, must be set in the member.

    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The steelbeamcolumn to check.
        
    Returns
    -------
    float
        The buckling stress in MPa.

    """
    # Confirm that the beam falls within the limits for compression.
    checkCompressionLimits(beam.section)
    
    # Check the member class and raise an exception if
    _checkType(beam.section)
    enum = beam.section.typeEnum 
    isNotHss = (enum != SteelSectionTypes.hss) and (enum != SteelSectionTypes.hssr)
    

    # Get the stress in each direction.
    Fex = checkColumnFeDirection(beam)
    Fey = checkColumnFeDirection(beam, False)

    # If the section is a W we have to check torsion and return that.
    # For now, assume that X0 and y0 are part of the cross section.
    if isNotHss:
        Fez = checkColumnFeTorsion(beam, 0, 0)    
        return min(Fex, Fey, Fez)
    return min(Fex, Fey)


def checkColumnCr(column:BeamColumnSteelCsa24, n:float = 1.34, 
                  lam:float = None):
    """
    Calculates compression resistance per 13.3.1.1
    
    Only applies to double symettric sections, i.e. W sections and
    HSS sections.

    Buckling effective stress is computed using 13.3.1.2
    
    Finds effective buckling stresses using 13.3.1.2

    kz, the buckling lenght for torsion, must be set in the member.


    Parameters
    ----------
    beam : BeamColumnSteelCsa24
        The steelbeamcolumn to check.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    lam : float, optional
        A manual override on the lambda factor. The default is calcualted using
        clause 13.3.1.2.

    Returns
    -------
    float
        The strength of the column in N.

    """
    
    lsconvert = column.section.lConvert('mm')
    A   = column.section.A*lsconvert**2
    
    sconvert = column.section.mat.sConvert('MPa')
    Fy = column.section.mat.Fy*sconvert
    
    # If there is no manual overide for lambda, check it
    if lam == None:
        Fe = checkColumnFe(column)
        lam = (Fy/Fe)**0.5
    
    return checkCr(A, Fy, lam, n)


# =============================================================================
# Combined Bending / compression
# =============================================================================
# !!! there is a lot of re=work occuring in these functions. 
# !!! Consider making a class.

class Omega1LoadConditions(IntEnum):
    """
    An enumeration that represents possible loading cases for omega from 
    13.8.6
    1 = No loads
    2 = uniformly distributed loads, or regularly spaced point loads
    3 = concentrated loads applied at to the member.
    """
    noLoads = 1
    distLoads = 2
    concentratedLoads = 3

def getOmega1(loadCase:Omega1LoadConditions, Mmax = 1, Mmin = -1):
    """
    Calculates the amplifction factor when no transvers loads acts between
    supports. See c.l. 13.8.6 for details.

    Parameters
    ----------
    loadCase : Omega1LoadConditions
        The load condition:
            1 if there are no intermediate loads
            2 if there are uniformy distributed loads
            3 if there are concentrated loads applied at to the member.
    Mmax : TYPE, optional
        TYhe maximum load. The default is 1.
    Mmin : TYPE, optional
        THe minimum load, negative if single curvature, positive if double 
        curvature. The default is 1.

    Returns
    -------
    float
        The output value of the factor.

    """
    
    if loadCase == Omega1LoadConditions.noLoads:
        return getOmega1CaseA(Mmax, Mmin)
    elif loadCase == Omega1LoadConditions.distLoads:
        return 1
    elif loadCase == Omega1LoadConditions.concentratedLoads:
        return 0.85

def getOmega1CaseA(Mmax, Mmin):
    """
    The amplifaction factor when no transverse loads act between supports.
    """
    kappa = Mmin / Mmax
    return max(0.6 - 0.4*kappa, 0.4)


def _getBeta(lamy=0):
    """
    c.l. 13.8.2
    """
    return min(0.6 + 0.4*lamy, 0.85)

def _getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta, betax = 0.85):
    
    return Cf/Cr + betax*U1x*Mfx/Mrx + beta*U1y*Mfy/Mry

def _getCaseAResistance(beamColumn:BeamColumnSteelCsa24, Cf, n, lam = None):
    Cr = checkColumnCr(beamColumn, n, lam)
    Mrx = checkBeamMrSupported(beamColumn, True, Cf)
    Mry = checkBeamMrSupported(beamColumn, False, Cf)
    return Cr, Mrx, Mry

def getU1(omega:float, Cf:float, Ce:float):
    
    ratio = Cf/Ce
    
    if  1 <= ratio:
        return omega * 1000
    
    return omega / (1-ratio)

def checkCombinedCaseA(beamColumn:BeamColumnSteelCsa24, Cf:float, Mfx:float, 
                       Mfy:float, n:float, omega1:float):
    """
    Checks the cross sectional member strength, where: 
        
    - Clause 13.8.2 a
    - beta = 0.6
    - lamda = 0
    - Mr is calculated as normal
    - U1x/U2x are specified in 13.8.5 >= 1
    
    Parameters
    ----------
    beamColumn : BeamColumnSteelCsa24
        The beamcolumn to check.
    Cf : float
        The applied compressive load (N).
    Mfx : float
        The applied moment in the strong axis direction (Nm).
    Mfy : float, optional
        The applied moment in the strong weak direction (Nm). The default is 0.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    omegax1 : float, optional
        Omega 1 calculated as per 13.8.6. It has a default value of is 1.0,
        which represents a constant moment in single curvature..

    Returns
    -------
    u : float
        The the output utilziation
    
    """
    Cr, Mrx, Mry = _getCaseAResistance(beamColumn, Cf, n, 0)
    
    Cex = checkColumnCeDirection(beamColumn, True)
    Cey = checkColumnCeDirection(beamColumn, False)
    U1x = max(getU1(omega1, Cf, Cex),1)
    U1y = max(getU1(omega1, Cf, Cey),1)
        
    return _getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=0.6)

def checkCombinedCaseB(beamColumn:BeamColumnSteelCsa24, Cf:float, Mfx:float, 
                       Mfy:float, n:float, omega1:float,
                       isBracedFrame:bool = False):
    """
    Overall member strength
    Unbraced moment Moment is amplified due to p-delta in the axis of bending 
    only. Assumes the following:
    - Clause 13.8.2 b
    - k = 1 for compression, based on axis of bending only.
    - If there is uniaxial bending, use calulate Cr in that direction.
    - Mr is calculated as if the column is braced
    - U1x/U2x are taken as 1, unless the system is in a braced frame
    - If the system is a braced frame, it is calcualted with 13.8.5
        
    Parameters
    ----------
    beamColumn : BeamColumnSteelCsa24
        The beamcolumn to check.
    Cf : float
        The applied compressive load (N).
    Mfx : float
        The applied moment in the strong axis direction (Nm).
    Mfy : float, optional
        The applied moment in the strong weak direction (Nm). The default is 0.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    omegax1 : float, optional
        Omega 1 calculated as per 13.8.6. It has a default value of is 1.0,
        which represents a constant moment in single curvature..
    isBracedFrame : bool, optional
        A flag that specifies if the beam is in a braced frame. 
        The default is False.

    Returns
    -------
    u : float
        The the output utilziation
    
    
    """
    
    # Temporarily set kx to one
    oldkx = beamColumn.designProps.kx
    oldky = beamColumn.designProps.ky
    oldkz = beamColumn.designProps.kz
    beamColumn.designProps.setkx(1)
    beamColumn.designProps.setkz(0.0001)
    
    # Use a small k factor in the y direction if there is only uniaxial bending
    # this forces the column to consider buckling in the strong axis only.
    if Mfy == 0:
        beamColumn.designProps.setky(0.0001)
    else:
        beamColumn.designProps.setky(1)
    
    Cr, Mrx, Mry = _getCaseAResistance(beamColumn, Cf, n, None)


    
    # # If the applied load is greater than the buckling load
    # if min(Cex, Cey) < Cf:
    #     return 1000
    
    if isBracedFrame:
        
        Cex = checkColumnCeDirection(beamColumn,True)
        Cey = checkColumnCeDirection(beamColumn,False)
        
        U1x = getU1(omega1, Cf, Cex)
        U1y = getU1(omega1, Cf, Cey)
    else:   
        U1x = U1y = 1

    beamColumn.designProps.setkx(oldkx)
    beamColumn.designProps.setky(oldky)        
    beamColumn.designProps.setkz(oldkz)        
    
    # if lamy == None:
    sconvert = beamColumn.section.mat.sConvert('MPa')
    Fy = beamColumn.section.mat.Fy*sconvert
    Fey = checkColumnFeDirection(beamColumn, useX = False)
    lamy = (Fy/Fey)**0.5
    beta = _getBeta(lamy)
        
    return _getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=beta)

def checkCombinedCaseC(beamColumn:BeamColumnSteelCsa24, 
                       Cf:float, Mfx:float, Mfy:float, n:float, 
                       omega1:float, omega2:float, isBracedFrame = False):
    """
    Lateral Torsional Buckling
    Typically govens sections with strong axis loaded. Assumes the following:
    
    - Clause 13.8.2 with weak axis bending only.
    - Mrx is calculated as unbraced
    - Mry is calculated as braced
    - U1x/U1y = 1 for members in unbraced framses.
    - U1x is calcualted as in clause 13.8.5, but not  less than 1.0 if braced
    - U1y is calculated as in clause 13.8.5
    - U1x/U2x are taken as 1, unless the system is in a braced frame
    - If the system is a braced frame, it is calcualted with 13.8.5
        
    Parameters
    ----------
    beamColumn : BeamColumnSteelCsa24
        The beamcolumn to check.
    Cf : float
        The applied compressive load (N).
    Mfx : float
        The applied moment in the strong axis direction (Nm).
    Mfy : float, optional
        The applied moment in the strong weak direction (Nm). The default is 0.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    omegax1 : float, optional
        Omega 1 calculated as per 13.8.6. It has a default value of is 1.0,
        which represents a constant moment in single curvature.
    omegax2 : float, optional
        Omega 1 calculated as per 13.8.1. It has a default value of is 1.0,
        which represents a constant moment in single curvature.

    isBracedFrame : bool, optional
        A flag that specifies if the beam is in a braced frame. 
        The default is False.

    Returns
    -------
    u : float
        The the output utilziation
    
    
    """
    Cr = checkColumnCr(beamColumn, n)
    
    Mrx = checkBeamMrUnsupported(beamColumn, omega2, Cf = Cf)
    Mry = checkBeamMrSupported(beamColumn, False, Cf)       
 
    if isBracedFrame:
        Cex = checkColumnCeDirection(beamColumn,True)
        Cey = checkColumnCeDirection(beamColumn,False)
        U1x = max(getU1(omega1, Cf, Cex),1)
        U1y = max(getU1(omega1, Cf, Cey),1)
    else:
        U1x = U1y = 1
    
    # If Mfy !=0, then the value of beta doesn't matter.
    if Mfy !=0:
        sconvert = beamColumn.section.mat.sConvert('MPa')
        Fy = beamColumn.section.mat.Fy*sconvert
        Fey = checkColumnFeDirection(beamColumn, useX = False)
        lamy = (Fy/Fey)**0.5
        beta = _getBeta(lamy)
    else:
        beta = 0.6
 
    return _getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=beta)

def checkCombinedCaseD(beamColumn:BeamColumnSteelCsa24, Cf, Mfx, Mfy, 
                       isBracedFrame = False):
    """
    Biaxial Bending
    
    Members are checked for biaxial bending, without considering compression.
    Compression is still passed to the function to determine section class.
        
    Parameters
    ----------
    beamColumn : BeamColumnSteelCsa24
        The beamcolumn to check.
    Cf : float
        The applied compressive load (N).
    Mfx : float
        The applied moment in the strong axis direction (Nm).
    Mfy : float, optional
        The applied moment in the strong weak direction (Nm). The default is 0.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    omegax1 : float, optional
        Omega 1 calculated as per 13.8.6. It has a default value of is 1.0,
        which represents a constant moment in single curvature..
    isBracedFrame : bool, optional
        A flag that specifies if the beam is in a braced frame. 
        The default is False.    
    
    """
    
    Mrx = checkBeamMrUnsupported(beamColumn, True, Cf = Cf)
    Mry = checkBeamMrSupported(beamColumn, False, Cf)              
       
    
    return _getUtil(0, 1, 1, Mfx, Mrx, 1, Mfy, Mry, beta=1, betax = 1)

def checkBeamColumnCombined(beamColumn:BeamColumnSteelCsa24, Cf:float, 
                            Mfx:float, Mfy:float = 0, n:float = 1.34, 
                            omegax1:float = 1.0, omegax2:float=1.0, 
                            isBracedFrame = False):
    """
    Checks the 4 cases required to assess a steel element in combined bending
    and shear: cross section strength (c.l. 13.8.2a);
    Overall member strength (c.l. 13.8.2b); Lateral Torsional Buckling 
    (c.l. 13.8.2c); and biaxial bending (c.l. 13.8.2d).
    

    Parameters
    ----------
    beamColumn : BeamColumnSteelCsa24
        The beamcolumn to check.
    Cf : float
        The applied compressive load (N).
    Mfx : float
        The applied moment in the strong axis direction (Nm).
    Mfy : float, optional
        The applied moment in the strong weak direction (Nm). The default is 0.
    n : float, optional
        The parameter for compressive resistance. The default is 1.34, but the
        parameter can be increased for certain section types per c.l. 13.3.1.1.
    omegax1 : float, optional
        Omega 1 calculated as per 13.8.6. It has a default value of is 1.0,
        which represents a constant moment in single curvature..
    isBracedFrame : bool, optional
        A flag that specifies if the beam is in a braced frame. 
        The default is False.

    Returns
    -------
    u1 : float
        The utilization in case 1, cross section strength.
    u2 : float
        The utilization in case 2, overall member strength.
    u3 : float
        The utilization in case 3, Lateral Torsional Buckling.
    u4 : float
        The utilization in case 4, biaxial bending.

    """
    
    if isBracedFrame:
        u1 = checkCombinedCaseA(beamColumn, Cf, Mfx, Mfy, n, omegax1)
    else:
        u1 = 0
    u2 = checkCombinedCaseB(beamColumn, Cf, Mfx, Mfy, n, omegax1, isBracedFrame)
    u3 = checkCombinedCaseC(beamColumn, Cf, Mfx, Mfy, n, omegax1, omegax2, isBracedFrame)
    u4 = checkCombinedCaseD(beamColumn, Cf, Mfx, Mfy, isBracedFrame)
    
    return u1, u2, u3, u4
    


   








