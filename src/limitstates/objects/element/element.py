
from dataclasses import dataclass

from .. geometry import Member, initSimplySupportedMember
from .. section import SectionAbstract
from .. display import EleDisplayProps

__all__ = ["BeamColumn", "getBeamColumn"]


@dataclass
class UserProps:
    def __repr__(self):
        "<limitStates User Propreties Dataclass>"

@dataclass
class DefaultDesignProps:
    def __repr__(self):
        "<limitStates Design Propreties Dataclass>"

class Element1D:
    """
    Should not be used directly.
    Defines interfaces that other classes, i.e. a beam element or a column
    element will use.   

    Parameters
    ----------
    member : Member
        A structural member that records where the element lies in space,
        and records information loading information.
    section : SectionAbstract
        The cross section of the structural element.
    designProps : dataclass, optional
        The design props store store any internal attributes limitstates 
        need for design that are design code dependant. Examples include 
        the fire portection used for glulam elements, or if a beam 
        element is curved. The default is None.
    userProps : dataclass, optional
        A object that stores additional information needed for users. 
        The limitstates library will objects will not use this attribute. 
        The default is None.
    displayProps : dataclass, optional
        A object used to store information about output element geometry. 
        This includes information necessary for makign plots or rendering 
        geometry. The default is None.

    Returns
    -------
    None.

    """
    
    member:Member 
    designProps:DefaultDesignProps
    userProps:UserProps
    displayProps:EleDisplayProps
    
    @property
    def mat(self):
        return self.section.mat
     
    def getEIx(self, lUnit:str='m', sUnit:str='Pa'):
        """
        Returns EI about the sections local x axis, which is generally the 
        strong axis. Returns in units of sunit x lunit^4  
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output Ix in. The default is 'm'.
        sunit : float, optional
            Stress units to output E in. The default is 'Pa'.

        Returns
        -------
        float.
            The EIx for the section.

        """        
        return self.section.getEIx(sUnit, lUnit)  

    def getEIy(self, lUnit:str='m', sUnit:str='Pa'):
        """
        Returns EI about the sections local y axis, which is generally the 
        strong axis. Returns in units of sunit x lunit^4  
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output Iy in. The default is 'm'.
        sunit : float, optional
            Stress units to output E in. The default is 'Pa'.

        Returns
        -------
        float.
            The EIy for the section.

        """        
        return self.section.getEIy(sUnit, lUnit)

    def getGAx(self, lUnit:str='m', sUnit:str='Pa'):
        """
        Returns GA about the sections local x axis, which is generally the 
        strong axis. Returns in units of sunit x lunit^2  
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output Ax in. The default is 'm'.
        sunit : float, optional
            Stress units to output E in. The default is 'Pa'.

        Returns
        -------
        float.
            The GAx for the section.

        """
        
        return self.section.getGAx(sUnit, lUnit)

    def getGAy(self, lUnit:str='m', sUnit:str='Pa'):
        """
        Returns GA about the sections local y axis, which is generally the 
        strong axis. Returns in units of sunit x lunit^2  
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output Ay in. The default is 'm'.
        sunit : float, optional
            Stress units to output E in. The default is 'Pa'.

        Returns
        -------
        float.
            The GAy for the section.

        """
        return self.section.getGAy(sUnit, lUnit)    
    
    def getLength(self):
        """
        Returns the total length of the element.
        """
        return self.member.L
    
    def getVolume(self, lUnit='m'):
        """
        Returns the volume of the element in the input units.
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output Ay in. The default is 'm'.
        
        """
        slconvert = self.section.lConvert.convert(lUnit)
        blconvert = self.member.lConvert.convert(lUnit)        
        return self.member.L * self.section.A* slconvert**2 * blconvert

    def _initProps(self, designProps, userProps, displayProps):
        """ Initializes the main propreties of the element.
        """
                
        if designProps is None:
            designProps = DefaultDesignProps()
        self.designProps = designProps
        
        if userProps is None:
            userProps = UserProps()
        self.userProps = userProps
        
        if displayProps is None:
            displayProps = EleDisplayProps(self.section, self.member)
        self.eleDisplayProps = displayProps
        
    def setDisplayProps(self, displayProps):
        self.eleDisplayProps = displayProps

class BeamColumn(Element1D):
    """
    Represents a structural element that takes bending and axial loads.
    The beamcolumn class can be used directly, but is most commonly used
    by special objects in design libraries, which inherit from this class.

    Parameters
    ----------
    member : Member
        A structural member that records where the element lies in space,
        and records information loading information.
    section : SectionAbstract
        The cross section of the structural element.
    designProps : dataclass, optional
        The design props store store any internal attributes limitstates 
        need for design that are design code dependant. Examples include 
        the fire portection used for glulam elements, or if a beam 
        element is curved. The default is None.
    userProps : dataclass, optional
        A object that stores additional information needed for users. 
        The limitstates library will objects will not use this attribute. 
        The default is None.
    geomProps : dataclass, optional
        A object used to store information about output element geometry. 
        This includes information necessary for makign plots or rendering 
        geometry. The default is None.

    Returns
    -------
    None.

    """
    
    def __init__(self, member:Member, section:SectionAbstract, 
                 designProps:dataclass = None, userProps:dataclass = None,
                 geomProps:dataclass = None):
        
        self._initMain(member, section)
        self._initProps(designProps, userProps, geomProps)

      
    def _initMain(self, member:Member, section:SectionAbstract, lUnit:str='m'):
        self.member:Member = member
        self.section:SectionAbstract = section
            
    def __repr__(self):
        return f"<limitstates {self.member.L}{self.member.lUnit} BeamColumn>"

    

def getBeamColumn(L:float, section:SectionAbstract, lUnit:str='m', 
                  designProps:dict=None, **kwargs) -> BeamColumn:
    """
    A function used to return a basic beamcolumn based on an input length.
    The beamcolumn returned by this fuction will be a simply supported beam
    with one span.

    Parameters
    ----------
    L : float
        The input length for the beamcolumn.
    section : SectionAbstract
        The section the beamcolumn ises.
    lunit : str
        the units for the input length.
    designProps : dict, optional
        Additional design propreties the section will use. The default is None.

    Returns
    -------
    BeamColumn
        The output beamcolumn object.

    """
    
    member = initSimplySupportedMember(L, lUnit)
    
    return BeamColumn(member, section, designProps, **kwargs)


