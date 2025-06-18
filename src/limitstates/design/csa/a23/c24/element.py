"""
Xontains specific beamcolumn implementations for CSA glulam beams.
These are largely set up to ease development and provide type hints.
"""

from dataclasses import dataclass

from limitstates.objects import (Member, SectionRectangle, initSimplySupportedMember, 
                          SectionCLT)
from limitstates.objects.display import MATCOLOURS, PlotConfigCanvas,  PlotConfigObject
from limitstates import BeamColumn, EleDisplayProps, PlotOriginPosition



#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from .fireportection import GypusmRectangleCSA19, GypusmFlatCSA19

__all__ = ["BeamColumnGlulamCsa19", "getBeamColumnGlulamCsa19", 
           "BeamColumnCltCsa19", "DesignPropsClt19", "DesignPropsGlulam19",
           "EleDisplayPropsGlulam19"]

@dataclass
class DesignPropsGlulam19:
    """
    Design propreties specifically for a glulam beamcolumn element.
    Beams will either be single span or multi-span. For multi-span beams,
    Lx and Ly need to be set.
    
    Note Lx is the design length of an element. Lex is the effective design
    length, which is Lx * kx
    
    There are different design factors set for bending and compression design.
    This is because sometimes the top bracing for bending does not brace
    the full member in compression.
    

    Parameters
    ----------
    firePortection : GypusmRectangleCSA19
        The the structural member used to represent the beam's position,
        orientation and support conditions.
    sectionFire : SectionRectangle
        The fire section for the beamcolumn member.
    lateralSupport : bool, optional
        A flag that is set equal to true if the beamcolumn has continuous
        lateral support for bending.
        For single spans beams. For multi-segment beams.
    isCurved : bool
        A flag that specifies if the beam is curved. Curved members are 
        not currently supported.
    Lx : float|list[float]
        The beam column's unsupported length in the section's x direction, which
        is typically the strong direction.
        If the beam is mult-segment, this is a list of the beam length, multiplied
        by the factor ke from table 
    Ly : float|list[float]
        The beam column's unsupported length in the section's y direction, which
        is typically the weak direction.
    kexB : float
        A factor that converts the actual span length into the effective span
        length. See table 7.4 for guidance. 
        If the beam is multispan, it must have the same number of entries 
        as Lx and Ly. 
    kexC : float
        A factor that converts the actual span length into the effective span
        length for compression. See table A.4 for guidance. 
    keyC : float
        A factor that converts the actual span length into the effective span
        length for compression. See table A.4 for guidance. 
    """
    firePortection:GypusmRectangleCSA19 = None
    sectionFire:SectionRectangle = None
    lateralSupport:bool|list[bool] = True
    isCurved:bool = False
    Lx:float|list[float] = None
    Ly:float|list[float] = None
    
    kexB:float|list[float] = None
    kexC:float = None
    keyC:float = None
    
    burnDimensions:list[float] = None

    
    def setkexB(self, kexB):
        self.kexB  = kexB
        self.Lexb = self.Lx * self.kexB 
        
    def setkexC(self, kexC):
        self.kexC  = kexC
        self.LexC = self.Lx * self.kexC 
        
    def setkeyC(self, keyC):
        self.keyC  = keyC
        self.LeyC = self.Ly * self.keyC
        

@dataclass
class EleDisplayPropsGlulam19(EleDisplayProps):
    """
    """

    sectionFire: SectionRectangle = None
    fillColorLines: str = MATCOLOURS['glulamBurnt']
    configObjectBurnt: PlotConfigObject = None
    burnDimensions: list[float] = None
    displayLamHeight: float = 38
    
            
    def __post_init__(self):
        if self.configCanvas == None:
            self.configCanvas = PlotConfigCanvas()
 
        if self.configObject == None:
            self.configObject = PlotConfigObject(MATCOLOURS['glulam'],
                                                 cFillLines = MATCOLOURS['black'])
 
        if self.configObjectBurnt == None:
            self.configObjectBurnt = PlotConfigObject(MATCOLOURS['glulamBurnt'],
                                                 cFillLines = MATCOLOURS['black'])
            
    def setPlotOrigin(self, newOriginLocation:int|PlotOriginPosition):
        """
        Updates the plot 

        Parameters
        ----------
        newOriginLocation : int|PlotOriginPosition
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.configObject.originLocation = newOriginLocation
        self.configObjectBurnt.originLocation = newOriginLocation
        
        
class BeamColumnGlulamCsa19(BeamColumn):
    """
    Design propreties for a glulam beam element.
    
    Glulam Beam columns can either be single span or multi-span. 
    The span lengths are required to be set manually
    
    
    Multi-span members with compression loads are not supported.
    
    For multi-span beams, Lx and Ly need to be set.


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
        Propreties used to display the element.

    Returns
    -------
    None.

    """
    designProps:DesignPropsGlulam19
    
    def __init__(self, member:Member, section:SectionRectangle,
                 designProps:DesignPropsGlulam19 = None, 
                 userProps:dataclass = None,
                 eleDisplayProps:dataclass = None):

        
        self._initMain(member, section)
        # Initialize the design propreties if none are given.        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if eleDisplayProps is None:
            eleDisplayProps = EleDisplayPropsGlulam19(self.section, 
                                                   self.member,
                                                   sectionFire = designProps.sectionFire)

        self._initProps(designProps, userProps, eleDisplayProps)
        
    def setLx(self, Lx):
        self.designProps.Lx = Lx
        
    def setLy(self, Ly):
        self.designProps.Ly = Ly       
    
    def setSectionFire(self, sectionFire, burnDims = None):
        self.designProps.sectionFire = sectionFire
        self.eleDisplayProps.sectionFire = sectionFire
        
        if burnDims is not None:
            self.designProps.burnDimensions = burnDims
            self.eleDisplayProps.burnDimensions = burnDims

def getBeamColumnGlulamCsa19(L:float, section:SectionRectangle, lUnit:str='m', 
                             firePortection:GypusmRectangleCSA19 = None,
                             Lx:float = None, 
                             Ly:float = None,
                             kexB:float = 1,
                             kexC:float = 1,
                             keyC:float = 1) -> BeamColumnGlulamCsa19:
    """
    A function used to return a beamcolumn based on an input length.
    The beam uses a simply supported elemet. If a different type
    of element is required, it should be manually defined with 
    "BeamColumnGlulamCsa19" instead.
    
    Default values are assigned to design propreties.

    Parameters
    ----------
    L : float
        The input length for the beamcolumn.
    section : SectionAbstract
        The section the beamcolumn ises.
    lUnit : str
        The units for the input length of the member.

    Returns
    -------
    BeamColumn
        The output beamcolumn object.

    """
    member = initSimplySupportedMember(L, lUnit)
    designProps = DesignPropsGlulam19()

    
    if firePortection:
        designProps.firePortection = firePortection
        
    if Lx:
        designProps.Lx = Lx
    else:
        designProps.Lx = L
    designProps.kexB = kexB
    designProps.kexC = kexC

    if Ly:
        designProps.Ly = Ly
    else:
        designProps.Ly = L
    designProps.keyC = keyC
    
    return BeamColumnGlulamCsa19(member, section, designProps)

@dataclass
class DesignPropsClt19:
    """
    Design propreties specifically for a glulam beamcolumn element
    """
    firePortection:GypusmFlatCSA19 = None
    fireSection:SectionCLT = None
    Lx:bool = False
    Ly:bool = False
        

@dataclass
class EleDisplayPropsClt19(EleDisplayProps):
    """
    """

    sectionFire: SectionRectangle = None
    fillColorLines: str = MATCOLOURS['black']

    configObjectBurnt: PlotConfigObject = None
    burnDimensions: list[float] = None
    
            
    def __post_init__(self):
        if self.configCanvas == None:
            self.configCanvas = PlotConfigCanvas()
 
        if self.configObject == None:
            config = PlotConfigObject(MATCOLOURS['clt'],
                                      originLocation= 3,
                                      cFillLines = MATCOLOURS['black'],
                                      cFillPatch = MATCOLOURS['cltWeak'])
            self.configObject = config   
        if self.configObjectBurnt == None:
            config = PlotConfigObject(MATCOLOURS['glulamBurnt'],
                                      originLocation= 3,
                                      cFillLines = MATCOLOURS['black'],
                                      cFillPatch = MATCOLOURS['cltWeak'])            
            
            self.configObjectBurnt = config


class BeamColumnCltCsa19(BeamColumn):
    designProps:DesignPropsClt19
    section:SectionCLT
    
    def __init__(self, member:Member, section:SectionCLT, 
                 sectionOrientation:float = 0,
                 designProps:DesignPropsClt19 = None, 
                 userProps:dataclass = None,
                 eleDisplayProps:dataclass = None):
        """
        This design element treats the CLT panel as a beamcolumn.
        
        It is appropriate for modeling clt that acts in a one-way system,
        examples include line supported panels, or walls acting as columns.
        
        
        Parameters
        ----------
        member : Member
            The the structural member used to represent the beam's position,
            orientation and support conditions.
        section : SectionRectangle
            The section used.
        lUnit : str, optional
            the units used. The default is 'm'.
        designProps : DesignPropsGlulam19, optional
            The inital design propreties. The default is None, which creates 
            a empty DesignPropsGlulam19 object.
        userProps : dataclass, optional
            The user design propeties. The default is None, which creates an
            empty dataclass.

        Returns
        -------
        None.

        """
        
        self._initMain(member, section)
        
        if designProps is None:
            designProps = DesignPropsGlulam19()

        # Initialize the design propreties if none are given.        
        if eleDisplayProps is None:
            eleDisplayProps = EleDisplayPropsClt19(self.section, self.member)            
                    
        self._initProps(designProps, userProps, eleDisplayProps)
      
          
    def setSectionFire(self, sectionFire, burnDims = None):
        self.designProps.sectionFire = sectionFire
        self.eleDisplayProps.sectionFire = sectionFire
        
        if burnDims is not None:
            self.designProps.burnDimensions = burnDims
            self.eleDisplayProps.burnDimensions = burnDims
        
def _getSection(element, useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return element.designProps.sectionFire
    else:
        return element.section

        
def _getphi(useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return 1
    else:
        return 0.9

        
def _getphiCr(useFire:bool):
    """
    Gets the correct section to be used.
    """
    if useFire:
        return 1
    else:
        return 0.8

        
def _isGlulam(element:BeamColumn):
    """
    Checks if an element is timber or glulam.
    There may be better ways of checking if a element is of a certain type,
    for example we could add it to the design propreties.
    """
    if isinstance(element, BeamColumnGlulamCsa19):
        return True
    else:
        return False
        