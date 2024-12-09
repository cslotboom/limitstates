"""
Contains the code designc clauses
"""
from numpy import pi, diff, cumsum
from enum import IntEnum

from .element import BeamColumnGlulamCsa19,  _getSection, _getphi, _getphiCr, _isGlulam
from limitstates import DesignDiagram


def checkCb(Leb, d, b):
    """
    Calculates slenderness ratio according to c.l. 7.5.6.4.3
    Assumes units are all in m or mm.

    Parameters
    ----------
    Leb : float
        The effective length of the section in the direction being checked
        for bending.
    d : float
        The depth of the section in the direction being checked.
    b : float
        The width of the section in the direction being checked.

    Returns
    -------
    float
        The Cb factor.

    """
    return (Leb*d/b**2)**0.5   


# T
def checkBeamCb(element:BeamColumnGlulamCsa19, useX:bool = True):
    """
    Checks Cb, assuming the beam is single span
    Calculates slenderness ratio according to c.l. 7.5.6.4.3

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The beamcolumn element to use for checks.
    useX : bool, optional
        A flag that toggles if the x direction is to be used for Cb. 
        The default is True.

    Returns
    -------
    float
        The Cb factor.

    """
    if useX:
        Lexb = element.designProps.Lx * element.designProps.kexB
        b = element.section.b
        d = element.section.d
    else:
        raise Exception('Weak axis bending is not currently supported.')
        # Leb = element.designProps.Ley
        # b = element.section.d
        # d = element.section.b
    
    return checkCb(Lexb, d, b)

def checkKL(Cb:float, E:float, Fb:float, kse:float=1, kt:float=1, kx:float=1):
    """
    Calculates kL, if a beam is not laterally supported along it's compression 
    flange.
    
    One of three cases is considered, depending on the size of Cb.
    
    Note, Fb = fb (KD * KH * KSb * KT)
    
    C.l., units in MPa.

    Parameters
    ----------
    Cb : float
        The slenderness Factor.
    E : float
        The modulus of elasticity in MPa.
    Fb : TYPE
        Beam fb factored by knet in MPa.
    kse : float, optional
        The service k factor. The default is 1.
    kT : TYPE
        DESCRIPTION.
    kt : float, optional
        The treatment k factor. The default is 1.
    kx : float, optional
        The curvature factor to for the beam. The default is 1.

    """
    
    # Case a
    if Cb < 10:
        return 1
    Ck = (0.97*E*kse*kt / Fb)**0.5
    # Case b
    if 10 < Cb and Cb < Ck:
        return 1 - (1/3)*(Cb/Ck)**4
    # Case c        
    elif Ck < Cb and Cb < 50:
        return 0.65*E*kse*kt / (Cb**2*Fb*kx)
    else:
        return -1

def checkKzbg(b:float, d:float, LM0:float):
    """
    Calculates kzbg according to c.l. 7.5.6.5.
    
    **restriction:** for multiple piece laminations b may not be the beam width.
    **restriction:** LM0 is the length of beam segments between zero moment.
    If there are many points of inflection, a factor must be applied to each 
    segment.
    
    
    Parameters
    ----------
    b : float
        Beam width or widdest beam width for multi-piece laminations.
    d : float
        beam depth mm.
    LM0 : float
        length of beam segment between points of zero moment, mm.

    """
    
    kzbg = ((130/b)*(610/d)*( 9100 / LM0)) **0.1
    return min(1.3, kzbg)


def _getMr0(S:float, Fb:float, phi = 0.9):
    return phi*Fb*S

def checkGlulamMr(S:float, Fb:float, kzbg:float, kL:float = 1, kx:float=1,
                  phi = 0.9):
    """
    Calcualtes Mr for a beam or beam segment according to cl. 7.5.6.5.1

    Parameters
    ----------
    S : float
        The section modulus in mm3.
    Fb : float
        The factored bending strength in MPa, this is equal to fb * knet, where
        knet is the sum of all k factores except for specialty ones.
    kzbg : float
        The size factor.
    kL : float, optional
        The lateral stability factor. The default is 1.
    kx : float, optional
        The curvature factor. The default is 1.

    Returns
    -------
    float
        Mr in Nm.

    """
    Mr0 = _getMr0(S, Fb, phi)
    Mr1 = Mr0*kzbg*kx
    Mr2 = Mr0*kL*kx
    return min(Mr1, Mr2) / 1000
    

# def _CheckSectionMr():
#     # Calculate kzbg
#     lfactor = element.member.lConvert('mm')
#     slfactor = section.lConvert('mm')
    
#     # Note, kzbg is based on the ORIGINAL element size.
#     dmm = element.section.d*slfactor
#     bmm = element.section.b*slfactor
#     Lmm = element.getLength()*lfactor
#     kzbg = checkKzbg(bmm, dmm, Lmm)

#     if useX:
#         Smm = section.Sx*slfactor**3
#     else:
#         raise Exception('Weak axis bending currently is not supported by limitstates')
    
#     return checkGlulamMr(Smm, section.mat.fb*knet, kzbg, kL, kx, phi)

def _checkIfLatSupport(supportCondition:bool|list[bool]):
    """
    Checks a simple span if it is laterally supported
    """
    
    if supportCondition is True:
        return True
    elif isinstance(supportCondition, list):
        return True    
    return False



def _checkElementkL(element, knet, kse, kt, kx = 1):
    """
    Checks kL for simplified condtions
    
    kL is calculated according to 7.5.6.4 and 7.5.6.3.1
    
    Only checks kL in the strong axis

    """
        
    # check for lateral support, this should be boolean for simple members / segments
    
    latSupport = _checkIfLatSupport(element.designProps.lateralSupport)
    if latSupport:
        kL = 1
    # c.l. 7.5.6.3.2
    elif (element.section.d / element.section.b) < 2.5:
        kL = 1
    else:
        # raise Exception('Element is unsupported and 7.5.6.3.2 does not apply. limitstates can currently only design supported members.')
        sLunit = element.section.lUnit
        L = element.designProps.Lx * element.member.lConvert(sLunit)
        Cb = checkCb(L, element.section.d, element.section.b)
        
        E = element.section.mat.E
        fb = element.section.mat.fb
        kL = checkKL(Cb, E, fb*knet, kse, kt, kx)
        
    return kL

def checkMrGlulamBeamSimple(element:BeamColumnGlulamCsa19, knet:float = 1, 
                            useFire:bool = False, useX = True,
                            kse:float = 1, kt:float = 1) -> float:
    """
    Checks the Mr for a single span beamcolumn, where there are not points of 
    inflection in the bending moment diagram. If there are multiple spans, 
    multiple unsupported regions, or or points of inflection, then use
    :func:`checkMrGlulamBeamMultiSpan <limitstates.design.csa.o86.c19.glulam.checkMrGlulamBeamMultiSpan>`
    instead.
    If it is applied to a multi-span beam then it will assume the beam is
    laterally supported.
    
    Mr and kzbg is calculated according to 7.5.6.5, and 7.5.6.5.
    
    kL is calculated according to 7.5.6.4 and 7.5.6.3.1. The support condition
    is set in the design propreties.
    
    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check.
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.
    useX : bool, optional
        A toggle that sets the diretion moment will be checked in.
        Weak axis bending is currently not supported by limitstates.


    Returns
    -------
    Mr
        The output in Nm.

    """

  
    # check for curvature
    if not element.designProps.isCurved:
        kx = 1
    else:
        raise Exception('Element curved, limitstates can currently only design straight members.')
        
    kL = _checkElementkL(element, knet, kse, kt)

    section = _getSection(element, useFire)   
    phi = _getphi(useFire)
    
    # Calculate kzbg
    lfactor = element.member.lConvert('mm')
    slfactor = section.lConvert('mm')
    
    # Note, kzbg is based on the ORIGINAL element size.
    dmm = element.section.d*slfactor
    bmm = element.section.b*slfactor
    Lmm = element.getLength()*lfactor
    kzbg = checkKzbg(bmm, dmm, Lmm)

    if useX:
        Smm = section.Sx*slfactor**3
    else:
        raise Exception('Weak axis bending currently is not supported by limitstates')
    
    Fb = section.mat.fb*knet
    return checkGlulamMr(Smm, Fb, kzbg, kL, kx, phi)





def checkBMDkzbg(inflectionCoords:list[float], 
                 b:float, 
                 d:float):
    """
    Determins kzbg for a number of beam segments.

    Assumes all input units are are in mm.


    Parameters
    ----------
    interCoords : list[float]
        The points of inflection in mm. This should include the start and end 
        of the beam.
    b : float
        The width of the beam in mm.
    d : float
        The depth of the beam in mm.

    Returns
    -------
    interLengths : list[float]
        The segment lengths in mm.
    kzbgOut : float
        The output kzbg factors for each segment.

    """
    
    interLengths = diff(inflectionCoords)
    
    kzbgOut = []
    for L in interLengths:
        kzbgOut.append(checkKzbg(b, d, L))
    
    return interLengths, kzbgOut


def getMemberkL(segmentLengths: list[float], 
                segmentke, 
                segmentBraceCondition,
                b, d, E, Fb, kse, kt, kx):
    """
    Assumes that all segments have the same length.
    XX TO TEST
    """
        
    LeOut = []
    kLOut = []
    # checkKL(Cb, E, Fb)
    for L, ke, bc in zip(segmentLengths, segmentke, segmentBraceCondition):
        
        # If the compression flange is braced
        if bc == True:
            kLOut.append(1)
        # If the compression flange is braced
        elif d/b < 2.5:
            kLOut.append(1)
        else:
            Le = L*ke
            CbSegment = checkCb(Le, d, b)
            kLOut.append(checkKL(CbSegment, E, Fb, kse, kt, kx))
    
    return kLOut


def getMultispanRegions(Lkzbg, kzbg, Lseg, kL):
    xKzbg = cumsum(Lkzbg)
    xSeg  = cumsum(Lseg)
    xbreakpoints = list(set(list(xKzbg) + list(xSeg)))
    xbreakpoints.sort()
    nn = 0
    mm = 0
    kzbgOut = []
    kLOut   = []
    for ii in range(len(xbreakpoints)):
        xZ = xKzbg[nn]
        xS = xSeg[mm]
        
        kzbgOut.append(kzbg[nn])
        kLOut.append(kL[mm])
        xbreak = xbreakpoints[ii]
        
        if xZ <= xbreak:
            nn += 1
        if xS <= xbreak:
            mm += 1        
    return xbreakpoints, kzbgOut, kLOut
        

class SegmentSupportTypes(IntEnum):
    CONTINOUS = 1
    SUPPORTS = 2
    MANUAL = 3


def checkMrGlulamBeamMultiSpan(element: BeamColumnGlulamCsa19, 
                              bmd: DesignDiagram, 
                              lateralSupportType: SegmentSupportTypes | int = 2,
                              knet:float = 1, 
                              useFire:bool = False,
                              kse = 1, kt = 1, kx = 1):
    """
    Returns the Mr value for each region of a multiSpanBeam.
    Regions for Mr are determined using the span lengths for kL, and points
    of inflection for kzbg.

    Assumes the BMD and member have the same units for length.
    
    Regions for kzbg are calculated by finding points of inflection in the
    bending moment diagram.
    
    Regions for kL are calculated depending on the option selected.
    
    - If option 1 is selected, the beam is assumed to be continously laterally 
    supported over the entire beam.
    
    - If option 2 is selected, the beam is assumed to be laterally unsupported 
    between supports. In this case the factor ke is taken as 1.92 from 
    table 7.4
    
    - If option 3 is selected, then the design propreties will be used to.
    The user should manually set the attributed Lex, kexB, and lateralSupport
    in the designpropreties..

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The multi-span element to check.
    bmd : DesignDiagram
        The bending moment diagram for the load case to be checked.
    lateralSupportType : SegmentSupportTypes | int, optional
        The type of lateral support condition for bending. The default is 2.
        
        - 1 will return a beam with continous lateral supported on all segments
        - 2 will return a beam with no continous lateral support, i.e. lateral support only provided at nodes.
        - 3 will use the user define support conditions. The Lx, kexB, and 
        lateralSupport must be set for each beam segment
        
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.
    kSE : float, optional
        The service condition factor, used when calculating kC. 
        The default is 1.
    kT : float
        The treatment condition factor, used when calculating kC. 
        The default is 1.

    Returns
    -------
    MrOut : list[float]
        The Mr out for each design segment.
    xOut : list[float]
        The length of each design segment - these are either support conditions
        or points of inflection in the BMD.
    kzbgout : list[float]
        The kxbgout for each segment.
    kLout : list[float]
        The kL out for each segment..

    """
        
    mlfactor = element.member.lConvert('mm')
    slFactor = element.section.lConvert('mm')

    b  = element.section.b * slFactor # kzbg is based on the original section!
    d  = element.section.d * slFactor # kzbg is based on the original section!
    E  = element.section.mat.E
    Fb = element.section.mat.fb* knet
        
    # Get the regions for xkbg
    coordsmm = bmd.getIntersectionCoords() * mlfactor
    Lkzbg, kzbg = checkBMDkzbg(coordsmm, b, d)
        
    section = _getSection(element, useFire)    
    bkL = section.b * slFactor # kL is based on the fire section!
    dkL = section.d * slFactor # kL is based on the fire section!
    Sx   = section.Sx*slFactor**3
    
    if lateralSupportType != 3:
        Lseg, kexBSeg = _getElemenKlSegments(element)
        Lseg = [L * mlfactor for L in Lseg]
        Nseg = len(Lseg)    
    # Get the kL factor depending on the condition used.
    if lateralSupportType == 1:
        kL = [1] * len(Lseg)
    if lateralSupportType == 2:
        isContinouslyBraced = [False]* Nseg
        kL = getMemberkL(Lseg, kexBSeg, isContinouslyBraced,
                         bkL, dkL, E, Fb, kse, kt, kx)
    if lateralSupportType == 3:
        Lseg    = element.designProps.Lx  * mlfactor
        kexBSeg = element.designProps.kexB
        isContinouslyBraced = element.designProps.lateralSupport
        
        kL = getMemberkL(Lseg, kexBSeg, isContinouslyBraced,
                         bkL, dkL, E, Fb, kse, kt, kx)
    
    xOut, kzbgout, kLout = getMultispanRegions(Lkzbg, kzbg, Lseg, kL)
    xOut = [L / mlfactor for L in xOut]
    kmin = [min(kl, kz) for kl, kz  in zip(kzbgout, kLout)]
    

    phi  = _getphi(useFire)
    Mr0  = _getMr0(Sx, Fb, phi) / 1000
    MrOut = [Mr0* k  for k in kmin]
    
    return MrOut, xOut, kzbgout, kLout

def _getElemenKlSegments(element: BeamColumnGlulamCsa19) -> (list[float], list[float]):
    """
    
    Classifies a elements segments between supports.
    All segments are assumed to have a ke factor of 1.92. This is conservative
    for all loading types.
    
    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check.
        
    Returns
    -------
    segments : float
        The segment length.

    segmentsKe : float
        The segment ke factor.

    """
    member = element.member
    segments = []
    Ncurves = len(member.curves)
    for ii in range(Ncurves):
        line = member.curves[ii]
        segments.append(line.L)
        
    segmentsKe = [1.92]*Ncurves

    return segments, segmentsKe


# =============================================================================
# Shear clauses      
# =============================================================================
    

    
def checkGlulamShearSimple(Ag:float, Fv:float, phi = 0.9):
    """
    Checks 7.5.7.3b, and only applies if a beam with volume less than 2.0m^3.
    Other member types, i.e. columns, do not have this restriction.
    
    Parameters
    ----------
    Fv : float
        The shear factored by knet.
    Ag : float
        The Area of the cross section.

    Returns
    -------
    None.

    """
    
    return phi*Fv*Ag*(2/3)

    
     
def checkGlulamWr(Ag:float, Fv:float, Lbeam:float, Cv = 3.69, phi = 0.9):
    """
    Checks 7.5.7.3a, for net load
    Cv should be calculated according to c.l. 7.5.7.6 
    
    Parameters
    ----------
    Fv : float
        The shear factored by knet.
    Ag : float
        The Area of the cross section.
    Lbeam : float
        The beams's length in mm.
    Cv : TYPE, optional
        The Shear-load coefficient. The default is 3.69.

    Returns
    -------
    None.

    """
    
    return phi*Fv*0.48*Ag*Cv*(Ag*Lbeam/1e9)**-0.18    

def checkVrGlulamBeamSimple(element:BeamColumnGlulamCsa19, knet:float = 1, 
                        useFire:bool = False) -> float:
    """
    Checks the Wr for a beamcolumn, where there are no notches and no positive
    to negative discontinuties in the shear force diagram.
    
    Checks 7.5.7.3b, and only applies if a beam with volume less than 2.0m^3.
    Other member types, i.e. columns, do not have this restriction.

    
    If the shear force diagram changes sides, i.e. if there are intermediate
    supports or complex loading, then this check does not apply and the beam
    needs to be checked per segment.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check.
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.


    Returns
    -------
    Vr
        The output in N.

    """
    section = _getSection(element, useFire)   
    phi     = _getphi(useFire)

    # check for volume support
    lconvert = element.member.lConvert('mm')
    slconvert = element.section.lConvert('mm')
    Amm = element.section.A *slconvert**2
    Lmm = element.member.L*lconvert
    Z = Amm* Lmm
    if  2.0*1e9 < Z:
        print('Element length is greater than 2 m^3. Check does not apply for beams, see c.l. 7.5.7.3')
  
    return checkGlulamShearSimple(section.A, section.mat.fv*knet,phi)



def checkWrGlulamBeamSimple(element:BeamColumnGlulamCsa19, knet:float = 1, 
                        useFire:bool = False, Cv:float = 3.69) -> float:
    """
    Checks the Vr for a beamcolumn, where there are no notches and no positive
    to negative discontinuties in the shear force diagram.
    
    Checks 7.5.7.3b, and only applies if a beam with volume less than 2.0m^3.
    Other member types, i.e. columns, do not have this restriction.

    
    If the shear force diagram changes sides, i.e. if there are intermediate
    supports or complex loading, then this check does not apply and the beam
    needs to be checked per segment.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check.
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.


    Returns
    -------
    Vr
        The output in N.

    """
    section = _getSection(element, useFire)   
    phi = _getphi(useFire)

    # check for volume support
    lconvert = element.member.lConvert('mm')
    slconvert = element.section.lConvert('mm')
    Amm = element.section.A *slconvert**2
    Lmm = element.member.L*lconvert
    Z = Amm * Lmm
    if  Z < 2.0*1e9:
        print('Element length is greater than 2 m^3. Check does not apply for beams, see c.l. 7.5.7.3')
        
    
    return checkGlulamWr(Amm, section.mat.fv*knet, Lmm, Cv, phi)


# =============================================================================
# Check glulam compression
# =============================================================================



def _checkSlenderness(Le, r):
    return Le / r

def checkColumnCc(element:BeamColumnGlulamCsa19, useFire:bool = False):
    """
    Returns the slenderness factors for a column in each direction, assuming
    it is a rectangular column.
    Requires Lx and Ly to be set, and requires the beamcolumn only has one
    span.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The beamcolumn element to check.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.

    Returns
    -------
    Cx : float
        The effectice slenderness in the strong axis.
    Cy : float
        The effectice slenderness in the weak axis.

    """
    
    section = _getSection(element, useFire)

    # convert to the same unit.
    lfactor = element.member.lConvert(element.section.lUnit)
    props = element.designProps
    Lexc = props.Lx * props.kexC * lfactor
    Leyc = props.Ly * props.keyC * lfactor
    Cx = _checkSlenderness(Lexc, section.d)
    Cy = _checkSlenderness(Leyc, section.b)
    
    return Cx, Cy


# !!! What is the refernce code clause.
def checkKci(Fc:float, kzcg:float, Ci:float, E05:float, kSE:float = 1, 
           kT:float = 1):
    """
    get Kci in direction i
    """
    
    return (1 + ((Fc*kzcg*Ci**3) / (35*E05*kSE*kT)))**-1
    
# !!! What is the refernce code clause.
def checkKzcg(Ag:float, L:float):
    """
    Gets the compression kzcg factor.


    Parameters
    ----------
    Ag : float
        DESCRIPTION.
    L : float
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    return min(0.68*(Ag*L)**-0.13, 1)
    

def _getE05(E, useFire, isGlulam):
    if useFire:
        return E
    if isGlulam: 
        return 0.87*E
    else: # saw lumber
        return 0.62*E

def checkGlulamPr(Ag:float, Fc:float, kzcg:float, kc:float, phi = 0.8):
    """
    Calcualtes Pr for a column according to 7.5.8.5.

    Parameters
    ----------
    Ag : float
        The section modulus in mm2.
    Fc : float
        The factored compression strength in MPa.
    kzcg : float
        The size factor.
    phi : float
        The phi factor for the beamcolumn.

    Returns
    -------
    float
        Pr in N.

    """

    return phi*Ag*Fc*kzcg*kc

   
def checkPrGlulamColumn(element:BeamColumnGlulamCsa19, knet:float = 1, 
                        useFire:bool = False, kSE = 1, kT = 1) -> float:
    """
    Checks the Pr for a beamcolumn.
    Only single segment beamcolumns are supported.
    
    Pr and kzbg is calculated according to 7.5.8.5, and     
    kc is calculated according to 7.5.8.6
    
    If KSE or KT are not equal to one, they must be included in the equation,
    in addition to knet. knet should still be the product of all k factors.
    These terms are seperated out due to clause 7.5.8.6, which seperates
    kSE and KT when calcualting the factor Kc.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check.
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.
    kSE : float, optional
        The service condition factor, used when calculating kC. 
        The default is 1.
    kT : float
        The treatment condition factor, used when calculating kC. 
        The default is 1.
        
    Returns
    -------
    Pr
        The output in N.

    """
    section = _getSection(element, useFire)   
    phi = _getphiCr(useFire)
    
    # check for lateral support
    Cx, Cy = checkColumnCc(element, useFire)
    
    # Calculate kzcg
    lfactor = element.member.lConvert('m')
    slfactor = section.lConvert('m')
    
    # Note, kzcg is based on the ORIGINAL element size.
    dmm = element.section.d*slfactor
    bmm = element.section.b*slfactor
    Lmm = element.getLength()*lfactor
    kzcg = checkKzcg(bmm*dmm, Lmm)
    
    Fc = section.mat.fc*knet
    E = section.mat.E
    
    isGlulam = _isGlulam(element)
    E05 = _getE05(E, useFire,isGlulam)
    
    # there is probably a way to reduce the computational effort here.
    kcx = checkKci(Fc, kzcg, Cx, E05, kSE, kT)
    kcy = checkKci(Fc, kzcg, Cy, E05, kSE, kT)
    
    kc = min(kcx, kcy)

    return checkGlulamPr(section.A, Fc, kzcg,  kc, phi)

# =============================================================================
# Interaction
# =============================================================================

     
        

def checkPE(E05:float, I:float, Lei:float, kSE:float = 1, kT:float = 1):
    """
    Calculates the critical buckling load for a typical column based on the
    critical buckling length.

    Parameters
    ----------
    E : float
        The elastic modulus.
    I : float
        The moment of Inertia in the direction i.
    Lei : float
        The effectice buckling length in the direction i.
    kSE : float, optional
        The service k factor. The default is 1.
    kT : float, optional
        The treatment k factor. The default is 1.

    Returns
    -------
    float
        The critical buckling load in N.

    """
    
    return (pi)**2*E05*kSE*kT*I / Lei**2

   
def checkPEColumn(element:BeamColumnGlulamCsa19, knet:float = 1, 
                  useFire:bool = False, kSE = 1, kT = 1) -> float:
    """
    Checks the Pr for a beamcolumn.
    
    Pr and kzbg is calculated according to 7.5.8.5, and     
    kc is calculated according to 7.5.8.6
    
    If KSE or KT are not equal to one, they must be included in the equation,
    in addition to knet. knet should still be the product of all k factors.
    These terms are seperated out due to clause 7.5.8.6, which seperates
    kSE and KT when calcualting the factor Kc.

    Parameters
    ----------
    element : BeamColumnGlulamCsa19
        The glulam element to check. Can also be solid timber elements.
    knet : float, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire section.
    kSE : float, optional
        The service condition factor, used when calculating kC. 
        The default is 1.
    kT : float
        The treatment condition factor, used when calculating kC. 
        The default is 1.
        

    Returns
    -------
    Pr
        The output in N.

    """
    section = _getSection(element, useFire)   
    
    
    # check for lateral support
    Cx, Cy = checkColumnCc(element, useFire)
    
    # Calculate kzcg
    slfactor = (section.lConvert('m'))**4
    
    # Note, kzcg is based on the ORIGINAL element size.
    sfactor = section.mat.sConvert('Pa')
    E = section.mat.E * sfactor
    
    isGlulam = _isGlulam(element)
    E05 = _getE05(E, useFire, isGlulam)
    
    Lexc = element.designProps.Lx * element.designProps.kexC 
    Leyc = element.designProps.Ly * element.designProps.keyC 
    PEx = checkPE(E05, section.Ix*slfactor, Lexc, kSE, kT)
    PEy = checkPE(E05, section.Iy*slfactor, Leyc, kSE, kT)
    
    return PEx, PEy

def checkInterTimberGeneric(Pf:float, Pr:float, Mf:float, Mr:float, PE:float) -> float:
    """
    Checks interaction for a generic timber member.
    
    The force in the column is factored up by little p-delta loads.

    Parameters
    ----------
    Pf : float
        The factored compression force.
    Pr : float
        The compression resistance.
    Mf : float
        The factored moment force.
    Mr : float
        The moment resistance.
    PE : float
        The Euler bockling force for the column.

    Returns
    -------
    float
        The interactionutilization.

    """
    
    return (Pf/Pr)**2 + (Mf/Mr) * (1 - (1-Pf/PE))

def checkInterEccPf(Pf:float, e:float, Pr:float, Mr:float, PE:float) -> float:
    """
    Checks interaction for eccentrically loaded members in compression.
    
    limitations:
        - For glulam, does not apply to the weak axis of bending.
        - Assumes the bending diagram has no points of inflection in it
        - Assumes the member is constraind at both ends.
        - Does not consider any amplification due to large P-delta effects.
        
    See Section 5.1 of the wood hand book for more information.
    
    This is valid, because for eccentriclly loaded members the maximum moment 
    occurs at the midspan of the member, litle p delta effects occur at the
    center of the member.
    
    Assumes consistent units used, e.g. N, m, Nm

    Parameters
    ----------
    Pf : float
        The factored compression force.
    e : float
        The eccentricty the load applies at, in m.
    Pr : float
        The compression resistance.
    Mr : float
        The moment resistance.

    Returns
    -------
        float
        The interaction utilization in the form (top utilization , middle utilization)

    """
    
    return (Pf/Pr)**2 + (Pf*e/Mr), (Pf/Pr)**2 + 0.5*(Pf*e/Mr)*(1/(1-Pf/PE))



def checkInterEccPfColumn(element:BeamColumnGlulamCsa19, Pf:float, e:float,
                          Mr:float, knet:float = 1, useX:bool = True,
                          useFire:bool = False, 
                          kSE = 1, kT = 1) -> float:
    """
    Checks interaction for eccentrically loaded members in compression.
    Moment is applied in x if useX is set to true.
    For glulam, 
    
    limitations:
        - For glulam, does not apply to the weak axis of bending.
        - Assumes the bending diagram has no points of inflection in it
        - Assumes the member is constraind at both ends.
        - Does not consider any amplification due to large P-delta effects.

        
    See Section 5.1 of the wood hand book for more information.
        
    This is valid, because for eccentriclly loaded members the maximum moment 
    occurs at the midspan of the member, litle p delta effects occur at the
    center of the member.
    
    Parameters
    ----------
    Pf : float
        The factored compression force, in N.
    e : float
        The eccentricty the load applies at, in m.


    kSE : float, optional
        The service condition factor, used when calculating kC. 
        The default is 1.
    kT : float
        The treatment condition factor, used when calculating kC. 
        The default is 1.
        


    Returns
    -------
        float
        The interaction utilization.

    """
    
    if _isGlulam(element) and (not useX):
        raise Exception('Glualam checks in the weak axis are currently supported.')
    
    Mr = checkMrGlulamBeamSimple(element, knet, useFire, useX)
    Pr = checkPrGlulamColumn(element, knet, useFire, kSE, kT)
    
    PEx, PEy = checkPEColumn(element, knet, useFire, kSE, kT)
    if useX:
        PE =  PEx
    else:
        PE = PEy
    
    return max(checkInterEccPf(Pf, e, Pr, Mr, PE))


