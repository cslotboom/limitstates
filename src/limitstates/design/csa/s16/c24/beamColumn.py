"""
Contains functions for managing sections specific to CSAo86-19

Note, right now all limits are calculated at once BEFORE the 
"""

from .element import BeamColumnSteelCsa24, SectionSteel
from typing import Callable
from numpy import pi
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



def _checkType(sectionType:str):
    SUPPORTEDTYPES = ['W', 'HSS']

    if sectionType.type not in SUPPORTEDTYPES:
        raise Exception(f'Section of type {sectionType.type} not supported, expected one of {SUPPORTEDTYPES}')


# =============================================================================
# 
# =============================================================================

# def checkSlendernessRatio(r:float, L:float, K:float=1.0) -> (bool, float):
#     """
#     Checks the slenderness ratio of a section.

#     Parameters
#     ----------
#     rx : float
#         DESCRIPTION.
#     Lx : float
#         DESCRIPTION.
#     Kx : float, optional
#         DESCRIPTION. The default is 1.0.

#     Returns
#     -------
#     passedX : TYPE
#         DESCRIPTION.
#     slendernessX : TYPE
#         DESCRIPTION.

#     """

#     return K*L/r

# def checkElementSlenderness():
#     """
#     Checks the slenderness ratio of a section.

#     Parameters
#     ----------
#     rx : float
#         DESCRIPTION.
#     Lx : float
#         DESCRIPTION.
#     Kx : float, optional
#         DESCRIPTION. The default is 1.0.

#     Returns
#     -------
#     passedX : TYPE
#         DESCRIPTION.
#     slendernessX : TYPE
#         DESCRIPTION.

#     """

#     return K*L/r



# =============================================================================
# 
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

    isW = section.type == 'W'    
    if isW:
        cflange = classifyFlangeWSection(section, useX)
        cweb    = classifyWebWSection(section, useX, Cf)
        return max(cflange, cweb)

# def setElementClass(beam:BeamColumnSteelCsa24):



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
    Calcualtes Mr for a supported member in Nm
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
    Moment
        The output moment in Nm.

    """
    # sectionClass = _getSectionClassIfNotSet(beam.sectionsection, True, Cf)
    
    # if 
    
    if not Lu:
        lconvert = beam.member.lConvert('mm')
        Lu = beam.designProps.Lx * lconvert
    
    phi = 0.9
    Mu = checkSectionMu(beam.section, Lu, omega)*phi
    Mx = checkBeamMrSupported(beam, True, Cf)
    
    if 0.67*Mx < Mu:
        return min(1.15*Mx*(1 - 0.28*Mx / Mu), Mx)

    else:
        return Mu 

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
    cl 13.6.1.a.
    length is input in mm.
    Returns in N*m
    """
    

    lfactor = section.lConvert('mm')
    sfactor = section.mat.sConvert('MPa')

    E = section.mat.E * sfactor
    G = section.mat.G * sfactor
    
    Iy = section.Iy * lfactor**4
    J  = section.J  * lfactor**4
    Cw = section.Cw * lfactor**6
    
    return checkMu(E, Iy, G, J, Cw, Lu, omega) / 1000

def checkMu(E:float, Iy:float, G:float, J:float, 
            Cw:float, Lu:float, omega:float):
    """
    Calculates critical bucklimg moment for a beam.

    Parameters
    ----------
    E : float
        DESCRIPTION.
    Iy : float
        DESCRIPTION.
    G : float
        DESCRIPTION.
    J : float
        DESCRIPTION.
    Cw : float
        DESCRIPTION.
    Lu : float
        DESCRIPTION.
    omega : float
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return (omega*pi / Lu) * (E*Iy*G*J + Iy*Cw*(pi*E/Lu)**2)**0.5


def getBeamMr(beam:BeamColumnSteelCsa24, ):
    pass





# =============================================================================
# Compression
# =============================================================================

def checkCompressionLimits(section:SectionSteel):
    """
    Checks the column agains table 1 compression limits.
    """

    _checkType(section)
    sconvert = section.mat.sConvert('MPa')

    isW = section.type == 'W'  
    Fy = section.mat.Fy*sconvert
    lim  = 1/Fy**0.5

    if isW:
        # flange propreties
        tf   = section.tf
        bel = section.bf / 2
        flangeLim = 250*lim
        flangePasses = (bel / tf) < flangeLim
        
        # Web propreties
        tw   = section.tw
        h   = section.d -  section.tf*2
        webLim = 670*lim
        webPasses = (h / tw) < webLim

        if flangePasses and webPasses:
            return True
        else:
            raise Exception('Member is class 4 for compression. Check flange and web limits with Table 1.')



def checkCr(A:float, Fy:float, lamda:float, n:float = 1.34):
    """
    Calculates compression resistance per 13.3.1.1
    
    """
    phi = 0.9
    
    return phi*A*Fy / (1 + lamda**(2*n))**(1/n)
    

def checkFe(E:float, Leff:float, reff:float):
    """
    Effective buckling stress per c.l. 13.3.1.2
    Leff is the effective buckling length, i.e. k*L
    
    """
    return pi**2 * E / (Leff/reff)**2

    

def checkCe(E:float, I:float, Leff:float):
    """
    Effective buckling stress per c.l. 13.3.1.2
    Leff is the effective buckling length, i.e. k*L
    
    """
    return pi**2 * E * I (Leff)



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
        The structural element to check..
    useX : TYPE, optional
        The x direction to check the column in. The default is True.

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
        r  = column.section.rx*lsconvert
    else:
        Le = column.designProps.Ley*lconvert
        r  = column.section.ry*lsconvert
        
    return checkFe(E, Le, r)

def checkColumnCeDirection(column:BeamColumnSteelCsa24, useX = True):
    """
    Calculates buckling stress in a single direction stress per 13.3.1.1
    
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
        The buckling stress in MPa.

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
    useX : TYPE, optional
        The x direction to check the column in. The default is True.

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
    isNotHSS = beam.section.type != 'W'  

    # Get the stress in each direction.
    Fex = checkColumnFeDirection(beam)
    Fey = checkColumnFeDirection(beam, False)

    # If the section is a HSS we have to check torsion and return that.
    # For now, assume that X0 and y0 are part of the cross section.
    if isNotHSS:
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
        DESCRIPTION. The default is 1.34.
    lam : float, optional
        A manual override on the lambda factor. The default is calcualted using
        clause 13.3.1.2.

    Returns
    -------
    TYPE
        DESCRIPTION.

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
# Combined Bending / shear
# =============================================================================
# !!! there is a lot of re=work occuring in these functions. 
# !!! Consider making a class.




class CombinedBendingChecker:
    
    def __init__(self, beamColumn:BeamColumnSteelCsa24, Cf, Mfx, Mfy, n, 
                 omega1, isBracedFrame = False):
        
        self.beamColumn


class Omega1LoadConditions(IntEnum):
    """
    An enumeration that represents possible loading cases for omega from 
    13.8.6
    1 = No loads
    2 = uniformly distributed loads, or regularly spaced point loads
    3 = concentrated loads applied at midspan to the member.
    """
    noLoads = 1
    distLoads = 2
    concentratedLoads = 3

def getOmega1(loadCase:Omega1LoadConditions, Mmax = None, Mmin = None):
    """
    The amplifaction factor when no transverse loads act between supports.
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

def getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta, betax = 0.85):
    
    return Cf/Cr + betax*U1x*Mfx/Mrx + beta*U1y*Mfy/Mry

def _getCaseAResistance(beamColumn:BeamColumnSteelCsa24, Cf, n, lam = 0):
    Cr = checkColumnCr(beamColumn, n, lam)
    Mrx = checkBeamMrSupported(beamColumn, True, Cf)
    Mry = checkBeamMrSupported(beamColumn, False, Cf)
    return Cr, Mrx, Mry

def getU1(omega:float, Cf:float, Ce:float):
    return omega / (1-Cf/Ce)

def checkCombinedCaseA(beamColumn:BeamColumnSteelCsa24, Cf:float, Mfx:float, 
                       Mfy:float, n:float, omega1:float):
    """
    Cross Section strength
    
    Clause 13.8.2 a
    beta = 0.6
    lamda = 0
    Mr is calculated as normal
    U1x/U2x are specified in 13.8.5 >= 1
    """
    Cr, Mrx, Mry = _getCaseAResistance(beamColumn, Cf, n)
    
    Cex = checkColumnCeDirection(beamColumn,True)
    Cey = checkColumnCeDirection(beamColumn,False)
    U1x = max(getU1(omega1, Cf, Cex),1)
    U1y = max(getU1(omega1, Cf, Cey),1)
        
    return getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=0.6)

def checkCombinedCaseB(beamColumn:BeamColumnSteelCsa24, Cf:float, Mfx:float, 
                       Mfy:float, n:float, omega1:float,
                       isBracedFrame:bool = False):
    """
    Overall member strength
    Unbraced moment Moment is amplified due to p-delta in the axis of bending 
    only
    
    Clause 13.8.2 b
    k = 1 for compression, based on axis of bending only.
    If there is only uniaxial bending, then we only look at Cr in that 
    direction.
    Mr is calculated as if the column is braced
    U1x/U2x are taken as 1, unless the system is in a braced frame
    If the system is a braced frame, it is calcualted with 13.8.5
    
    
    """
    
    # Temporarily set kx to one
    oldkx = beamColumn.designProps.kx
    oldky = beamColumn.designProps.ky
    beamColumn.designProps.setkx(1)
    
    # Use a small k factor in the y direction if there is only uniaxial bending
    # this forces the column to consider buckling in the strong axis only.
    if Mfy == 0:
        beamColumn.designProps.setky(0.0001)
    else:
        beamColumn.designProps.setky(1)

    
    Cr, Mrx, Mry = _getCaseAResistance(beamColumn, Cf, n, None)

    if isBracedFrame:
        Cex = checkColumnCeDirection(beamColumn,True)
        Cey = checkColumnCeDirection(beamColumn,False)
        U1x = getU1(omega1, Cf, Cex)
        U1y = getU1(omega1, Cf, Cey)
    else:   
        U1x = U1y = 1

    beamColumn.designProps.setkx(oldkx)
    beamColumn.designProps.setky(oldky)        
    
    # if lamy == None:
    sconvert = beamColumn.section.mat.sConvert('MPa')
    Fy = beamColumn.section.mat.Fy*sconvert
    Fey = checkColumnFeDirection(beamColumn, useX = False)
    lamy = (Fy/Fey)**0.5
    beta = _getBeta(lamy)
        
    return getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=beta)

def checkCombinedCaseC(beamColumn:BeamColumnSteelCsa24, Cf, Mfx, Mfy, n, 
                       omega1, isBracedFrame = False):
    """
    Lateral Torsional Buckling
    Typically govens sections with strong axis loaded.
    
    Clause 13.8.2 with weak axis bending only.
    Mrx is calculated as unbraced
    Mry is calculated as braced
    U1x/U1y = 1 for members in unbraced framses.
    U1x is calcualted as in clause 13.8.5, but not  less than 1.0 if braced
    U1y is calculated as in clause 13.8.5
    
    U1x/U2x are taken as 1, unless the system is in a braced frame
    If the system is a braced frame, it is calcualted with 13.8.5
    """
    Cr = checkColumnCr(beamColumn, n)
    
    # !!! only works for W sections
    Mrx = checkBeamMrUnsupportedW(beamColumn, True, Cf = Cf)
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
 
    return getUtil(Cf, Cr, U1x, Mfx, Mrx, U1y, Mfy, Mry, beta=beta)

def checkCombinedCaseD():
    """
    Biaxial Bending
    
    Members are calulated with 
    """
    # Cr, Mrx, Mry = _getCaseAResistance(beamColumn, n)
       
       

def checkBeamColumnCombined(beamColumn:BeamColumnSteelCsa24, Cf:float, 
                            Mfx:float, Mfy:float = 0, n:float = 1.24, 
                            omegax1:float = 1.0, isBracedFrame = False):
    
    if isBracedFrame:
        u1 = checkCombinedCaseA(beamColumn, Cf, Mfx, Mfy, n, omegax1)
    else:
        u1 = 0
    u2 = checkCombinedCaseB(beamColumn, Cf, Mfx, Mfy, n, omegax1, isBracedFrame)
    u3 = checkCombinedCaseC(beamColumn, Cf, Mfx, Mfy, n, omegax1, isBracedFrame)
    
    return u1, u2, u3
    


   








