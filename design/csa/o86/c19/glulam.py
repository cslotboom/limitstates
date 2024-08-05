"""
Contains the code designc clauses
"""

from .element import GlulamBeamColumnCSA19,  _getSection, _getphi, _getphiCr
from numpy import pi

def checkCb(Le, d, b):
    """
    Calculates slenderness ratio according to c.l. 7.5.6.4.3
    """
    return (Le*d/b**2)**0.5   

def getBeamCb(element:GlulamBeamColumnCSA19, useX:bool = True):
    """
    Calculates slenderness ratio according to c.l. 7.5.6.4.3
    """
    if useX:
        Le = element.designProps.Lex
        b = element.section.b
        d = element.section.d
    else:
        Le = element.designProps.Ley
        b = element.section.d
        d = element.section.b
    
    return (Le*d/b**2)**0.5

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
        return 0

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


def checkGlulamMr(S:float, Fb:float, kzbg:float, kL:float = 1, kx:float=1,
                  phi = 0.9):
    """
    Calcualtes Mr for a beam or beam segment.

    Parameters
    ----------
    S : float
        The section modulus in mm3.
    Fb : float
        The factored bending strength in MPa.
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
    Mr0 = phi*Fb*S
    Mr1 = Mr0*kzbg*kx
    Mr2 = Mr0*kL*kx
    return min(Mr1, Mr2) / 1000
    
   
def checkMrGlulamBeamSimple(element:GlulamBeamColumnCSA19, knet:float = 1, 
                        useFire:bool = False, useX = True) -> float:
    """
    Checks the Mr for a beamcolumn, where there are not points of inflection 
    in the bending moment diagram. Generally does not apply to multispan beams
    or those with points of inflection.
    
    Mr and kzbg is calculated according to 7.5.6.5, and 
    
    kL is calculated according to 7.5.6.4 and 7.5.6.3.1
    
    If there are points of inflection in the beam, kzbg should be calcualted
    per segment.

    Parameters
    ----------
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire sectio.
    useX : bool, optional
        A toggle that sets the diretion moment will be checked in.
        Weak axis bending is currently not supported by limitstates.


    Returns
    -------
    Mr
        The output in Nm.

    """
    section = _getSection(element, useFire)   
    phi = _getphi(useFire)
    
    # check for lateral support
    if element.designProps.lateralSupport:
        kL = 1
    elif (element.section.d / element.section.b) < 2.5:
        kL = 1
    else:
        raise Exception('Element is unsupported and 7.5.6.4 does not apply. limitstates can currently only design supported members.')
  
    # check for curvature
    if not element.designProps.isCurved:
        kx = 1
    else:
        raise Exception('Element curved, limitstates can currently only design straight members.')
    
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
    
    return checkGlulamMr(Smm, section.mat.fb*knet, kzbg, kL, kx, phi)


def checkMrMultispanBeamColumn():
    pass
    # phi = 0.9
    


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

def checkVrGlulamBeamSimple(element:GlulamBeamColumnCSA19, knet:float = 1, 
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
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire sectio.


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
    Z = Amm* Lmm
    if  2.0*1e9 < Z:
        print('Element length is greater than 2 m^3. Check does not apply for beams, see c.l. 7.5.7.3')
  
    return checkGlulamShearSimple(section.A, section.mat.fv*knet,phi)



def checkWrGlulamBeamSimple(element:GlulamBeamColumnCSA19, knet:float = 1, 
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
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
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

def checkColumnCc(element:GlulamBeamColumnCSA19, useFire:bool = False):
    """
    Returns the slenderness factors for a column in each direction.
    Requires Lex and Ley to be set.

    Parameters
    ----------
    element : GlulamBeamColumnCSA19
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

    Cx = _checkSlenderness(element.designProps.Lex*lfactor, section.d)
    Cy = _checkSlenderness(element.designProps.Ley*lfactor, section.b)
    
    return Cx, Cy



def checkKci(Fc:float, kzcg:float, Ci:float, E:float, kSE:float = 1, 
           kT:float = 1):
    """
    get Kci in direction i
    """
    
    return (1 + ((Fc*kzcg*Ci**3) / (35*0.87*E*kSE*kT)))**-1
    

def checkKzcg(Ag:float, L:float):
    """
    get Kci in direction i
    """
    
    return min(0.68*(Ag*L)**-0.13, 1)
    


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

   
def checkPrGlulamColumn(element:GlulamBeamColumnCSA19, knet:float = 1, 
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
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire sectio.
    kSE : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
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
    
    # there is probably a way to reduce the computational effort here.
    kcx = checkKci(Fc, kzcg, Cx, E, kSE, kT)
    kcy = checkKci(Fc, kzcg, Cy, E, kSE, kT)
    
    kc = min(kcx, kcy)

    return checkGlulamPr(section.A, Fc, kzcg,  kc, phi)

# =============================================================================
# Interaction
# =============================================================================


def checkPE(E:float, I:float, Lei:float, kSE:float = 1, kT:float = 1):
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
    
    return (pi)**2*0.87*E*kSE*kT*I / Lei**2

   
def checkPEGlulamColumn(element:GlulamBeamColumnCSA19, knet:float = 1, 
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
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire sectio.
    kSE : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
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
    slfactor = (section.lConvert('mm'))**4
    
    # Note, kzcg is based on the ORIGINAL element size.
    E = section.mat.E
    PEx = checkPE(E, section.Ix*slfactor, element.designProps.Lex, kSE, kT)
    PEy = checkPE(E, section.Ix*slfactor, element.designProps.Ley, kSE, kT)
    
    return PEx, PEy

def checkInteractionGlulamColumn(Pf:float, Pr:float, Mf:float, Mr:float, PE:float) -> float:
    """
    Checks the column for .
    
    Pr and kzbg is calculated according to 7.5.8.5, and     
    kc is calculated according to 7.5.8.6
    
    If KSE or KT are not equal to one, they must be included in the equation,
    in addition to knet. knet should still be the product of all k factors.
    These terms are seperated out due to clause 7.5.8.6, which seperates
    kSE and KT when calcualting the factor Kc.

    Parameters
    ----------
    element : GlulamBeamColumnCSA19
        The glulam element to check.
    knet : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.
    useFire : bool, optional
        A toggle that makes the beam use it's fire section when selected. 
        The default is False, which uses no fire sectio.
    kSE : flaot, optional
        The product of all standard k factors, including kd, kse, etc. 
        The default is 1.

    Returns
    -------
    Pr
        The output in N.

    """
    
    return (Pf/Pr)**2 + (Mf/Mr) * (1 - (1-Pf/PE))


# def checkPrGlulamBeam(element:GlulamBeamColumnCSA19, knet:float = 1, 
#                             useFire:bool = False, kSE = 1, kT = 1) -> float:
#     """
#     Checks the Pr for a beamcolumn.
    
#     Pr and kzbg is calculated according to 7.5.8.5, and     
#     kc is calculated according to 7.5.8.6
    
#     If KSE or KT are not equal to one, they must be included in the equation,
#     in addition to knet. knet should still be the product of all k factors.
#     These terms are seperated out due to clause 7.5.8.6, which seperates
#     kSE and KT when calcualting the factor Kc.

#     Parameters
#     ----------
#     element : GlulamBeamColumnCSA19
#         The glulam element to check.
#     knet : flaot, optional
#         The product of all standard k factors, including kd, kse, etc. 
#         The default is 1.
#     useFire : bool, optional
#         A toggle that makes the beam use it's fire section when selected. 
#         The default is False, which uses no fire sectio.
#     kSE : flaot, optional
#         The product of all standard k factors, including kd, kse, etc. 
#         The default is 1.

#     Returns
#     -------
#     Pr
#         The output in N.

#     """
#     section = _getSection(element, useFire)   
#     phi = _getphiCr(useFire)
    
#     # check for lateral support
#     Cx, Cy = checkColumnCc(element, useFire)
    
#     # Calculate kzcg
#     lfactor = element.member.lConvert('m')
#     slfactor = section.lConvert('m')
    
#     # Note, kzcg is based on the ORIGINAL element size.
#     dmm = element.section.d*slfactor
#     bmm = element.section.b*slfactor
#     Lmm = element.getLength()*lfactor
#     kzcg = checkKzcg(bmm*dmm, Lmm)
    
#     Fc = section.mat.fc*knet
#     E = section.mat.E
    
#     # there is probably a way to reduce the computational effort here.
#     kcx = checkKci(Fc, kzcg, Cx, E, kSE, kT)
#     kcy = checkKci(Fc, kzcg, Cy, E, kSE, kT)
    
#     kc = min(kcx, kcy)

#     return checkGlulamPr(section.A, Fc, kzcg,  kc, phi)
