"""
Contains code design clauses for working with CLT.
"""

from .element import BeamColumnCltCSA19, _getSection, _getphi
from .....objects import SectionCLT


def _getLayerGroup(section:SectionCLT, useStrongAxis:bool):
    
    if useStrongAxis:
        return section.sLayers
    else: 
        return section.wLayers

#TODO: consider making these vectorizable.
def checkMrClt(S:float, Fb:float, useStrongAxis=True, phi = 0.9):
    """
    Calcualtes the out of plane (flatwise) Mr for a CLT panel.

    Parameters
    ----------
    S : float
        The section modulus in mm3.
    Fb : float
        The factored bendings strength in MPa.
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
    if useStrongAxis:
        krb = 0.85
    else:
        krb = 1
    return phi*S*Fb*krb
    
   
def checkMrCltBeam(element:BeamColumnCltCSA19, knet:float = 1, 
               useFire:bool = False, useStrongAxis = True) -> float:
    """
    Checks the Mr for typical CLT panel, return units in Nm.
    
    Mr and kzbg is calculated according to 7.5.6.5, and 
    
    kL is calculated according to 7.5.6.4 and 7.5.6.3.1
    
    If there are points of inflection in the beam, kzbg should be calcualted
    per segment.

    Parameters
    ----------
    element : BeamColumnCltCSA19
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
    section:SectionCLT = _getSection(element, useFire)   
    phi = _getphi(useFire)

    layers = _getLayerGroup(section, useStrongAxis)
    sfactor = layers[0].mat.sConvert('MPa')
    fb = layers[0].mat.fb*sfactor
    E = layers[0].mat.E*sfactor
    
    # Get the conversion factor for y max
    # slfactor = section.lConvert('mm')
    
    if useStrongAxis:
        Smm = (section.getEIs(sunit='MPa', lunit='mm') / E / layers.getYmax())
        # Smm = (section.getEIs(lunit='mm') / E / (layers.getYmax() * slfactor)) /10e6
    else:
        # Smm = (section.getEIw() / E / layers.getYmax() * slfactor)      
        Smm = (section.getEIw(sunit='MPa', lunit='mm') / E / layers.getYmax())
        
    return checkMrClt(Smm, fb*knet, useStrongAxis, phi) / 1000


# =============================================================================
# Shear clauses      
# =============================================================================
    
def checkCltShear(Ag:float, Fs:float, phi = 0.9):
    """
    Checks 7.5.7.3b, and only applies if a beam with volume less than 2.0m^3.
    Other member types, i.e. columns, do not have this restriction.
    
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
    
    phi = 0.9
    return phi*Fs*Ag*(2/3)
  
def checkCltBeamShear(element:BeamColumnCltCSA19, knet:float = 1, 
                        useFire:bool = False, useStrongAxis = True) -> float:
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
    element : BeamColumnCltCSA19
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
    
    layers = _getLayerGroup(element.section, useStrongAxis)
    sfactor = layers[0].mat.sConvert('MPa')
    fv = layers[0].mat.fs*sfactor
    Anet = layers.d * section.w
    

  
    return checkCltShear(Anet, fv*knet, phi)



