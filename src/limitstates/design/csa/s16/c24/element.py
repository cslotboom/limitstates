"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass
from limitstates import (Member, SectionRectangle, initSimplySupportedMember, SectionSteel)

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from limitstates import BeamColumn, EleDisplayProps

__all__ = ["DesignPropsSteel24", "BeamColumnSteelCsa24", 
           "getBeamColumnSteelCsa24"]

@dataclass
class DesignPropsSteel24:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    lateralSupport:bool = True
    kx:float = 1
    ky:float = 1
    kz:float = 1
    Lx:float = None    
    Ly:float = None    
    Lz:float = None    
    Lex:float = None
    Ley:float = None
    Lez:float = None
    webStiffened = False
    
    def setkx(self, kx):
        self.kx  = kx
        self.Lex = self.Lx * self.kx 
        
    def setky(self, ky):
        self.ky  = ky
        self.Ley = self.Ly * self.ky 
        
    def setkz(self, kz):
        self.kz  = kz
        self.Lez = self.Lz * self.kz 
    
    
class BeamColumnSteelCsa24(BeamColumn):
    designProps:DesignPropsSteel24
    
    def __init__(self, member:Member, section:SectionSteel, 
                 designProps:DesignPropsSteel24 = None, 
                 userProps:dataclass = None,
                 eleDisplayProps:dataclass = None):
        """
        Design propreties for a glulam beam element.

        Parameters
        ----------
        member : Member
            The the structural member used to represent the beam's position,
            orientation and support conditions.
        section : SectionRectangle
            The section for the beamcolumn.
        designProps : DesignPropsGlulam19, optional
            The inital design propreties. The default is None, which creates 
            a empty DesignPropsGlulam19 object.
        userProps : dataclass, optional
            The user design propeties. The default is None, which creates an
            empty dataclass.
        eleDisplayProps : dataclass
            Propreties used to display the section.

        Returns
        -------
        None.

        """
        
        self._initMain(member, section)

        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsSteel24()

        # Initialize the design propreties if none are given.        
        if eleDisplayProps is None:
            eleDisplayProps = EleDisplayProps(self.section, self.member)

        self._initProps(designProps, userProps, eleDisplayProps)
        
    def setLex(self, Lex):
        self.designProps.Lex = Lex
        
    def setLey(self, Ley):
        self.designProps.Ley = Ley       
        
def getBeamColumnSteelCsa24(L:float, section:SectionRectangle, lUnit:str='m', 
                            kx:float = 1, 
                            ky:float = 1,
                            kz:float = 1,
                            Lx:float = None,
                            Ly:float = None,
                            Lz:float = None) -> BeamColumnSteelCsa24:

    """
    A function used to return a beamcolumn based on an input length.
    The beam uses a simply supported elemet by default. If a different type
    of element is required, it should be manually defined with 
    "BeamColumnGlulamCsa19" inatead.
    
    Default values are assigned to design propreties.
    
    Effective lengths will be a product of the effective length 'k' factor, and
    design length.

    Parameters
    ----------
    L : float
        The input length for the beamcolumn.
    section : SectionAbstract
        The section the beamcolumn ises.
    lUnit : str
        The units for the input length of the member.
    kx : float, optional
        The effective lenght factor for the direction x. The default is 1.
    ky : float, optional
        The effective lenght factor for the direction y. The default is 1.
    kz : float, optional
        The effective lenght factor for the direction z (the torsion axis). 
        The default is 1.
    Lx : float, optional
        The design length in the directon x. The default is None, which 
        defaults to using the total member length.
    Ly : float, optional
        The design length in the directon y. The default is None, which 
        defaults to using the total member length.
    Lz : float, optional
        The design length in the directon z. The default is None, which 
        defaults to using the total member length.
    Returns
    -------
    BeamColumn
        The output beamcolumn object.

    """
    member = initSimplySupportedMember(L, lUnit)
    designProps = DesignPropsSteel24()
    
    if not Lx:
        Lx = L
    designProps.Lx = Lx
    designProps.setkx(kx)
    
    if not Ly:
        Ly = L
    designProps.Ly = Ly
    designProps.setky(ky)
    
    if not Lz:
        Lz = L
    designProps.Lz = Lz
    designProps.setkz(kz)


    return BeamColumnSteelCsa24(member, section, designProps)
