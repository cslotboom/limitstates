
# from abc import ABC, abstractmethod
from dataclasses import dataclass

from .. geometry import Member, initSimplySupportedMember
from .. section import SectionAbstract

__all__ = ["BeamColumn", "getBeamColumn", "DisplayProps"]


@dataclass
class UserProps:
    def __repr__(self):
        "<limitStates User Propreties Dataclass>"

@dataclass
class DefaultDesignProps:
    def __repr__(self):
        "<limitStates Design Propreties Dataclass>"


@dataclass
class DisplayProps:
    section:SectionAbstract
    geometry:Member
        
    def __repr__(self):
        "<limitStates output Propreties Dataclass>"

    def getVerticies(self):
        pass






class Element1D:
    length:float
    designProps:DefaultDesignProps
    userProps:UserProps
    displyProps:DisplayProps
    
    @property
    def mat(self):
        return self.section.mat
     
    def getEIx(self, lUnit:str='m', sUnit:str='Pa'):
        return self.section.getEIx(sUnit, lUnit)  

    def getEIy(self, lUnit:str='m', sUnit:str='Pa'):
        """Returns EIy, i.e EI in the secondary axis"""             
        return self.section.getEIy(sUnit, lUnit)

    def getGAx(self, lUnit:str='m', sUnit:str='Pa'):
        """ Returns GA for the section """
        return self.section.getGAx(sUnit, lUnit)

    def getGAy(self, lUnit:str='m', sUnit:str='Pa'):
        """ Returns GA for the section """
        return self.section.getGAy(sUnit, lUnit)    
    
    def getLength(self):
        return self.member.L
    
    def getVolume(self, lUnit='m'):
        """
        Returns the volume of the element.
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
            displayProps = DisplayProps(self.section, self.member)
        self.displayProps = displayProps
        

class BeamColumn(Element1D):
    
    def __init__(self, member:Member, section:SectionAbstract, 
                 designProps:dataclass = None, userProps:dataclass = None,
                 geomProps:dataclass = None):
        
        self._initMain(member, section)
        self._initProps(designProps, userProps, geomProps)

      
    def _initMain(self, member:Member, section:SectionAbstract, lUnit:str='m'):
        self.member:Member = member
        self.section:SectionAbstract = section
    
    # def _initProps():
    #     pass
    
    
    # def _initUserProps(self, userProps:dataclass = None):
    #     if userProps is None:
    #         userProps = UserProps()
    #     self.userProps = userProps
        
    def __repr__(self):
        return f"<limitstates {self.member.L}{self.member.lUnit} BeamColumn>"

    

def getBeamColumn(L:float, section:SectionAbstract, lUnit:str='m', 
                  designProps:dict=None, **kwargs) -> BeamColumn:
    """
    A function used to return a beamcolumn based on an input length.
    The default beamcolumn is assumed to have a simply supported beam.

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





# class Element2D:
#     points:
#     designProps:DefaultDesignProps
#     userProps:UserProps
    
#     @property
#     def mat(self):
#         return self.section.mat
     
#     def getEIx(self, lUnit:str='m', sUnit:str='Pa'):
#         return self.section.getEIx(sUnit, lUnit)  

#     def getEIy(self, lUnit:str='m', sUnit:str='Pa'):
#         """Returns EIy, i.e EI in the secondary axis"""             
#         return self.section.getEIy(sUnit, lUnit)

#     def getGAx(self, lUnit:str='m', sUnit:str='Pa'):
#         """ Returns GA for the section """
#         return self.section.getGAx(sUnit, lUnit)

#     def getGAy(self, lUnit:str='m', sUnit:str='Pa'):
#         """ Returns GA for the section """
#         return self.section.getGAy(sUnit, lUnit)    
    
#     def getLength(self):
#         return self.member.length
    
#     def getVolume(self, lUnit='m'):
#         """
#         Returns the volume of the element.
#         """
#         slconvert = self.section.lConvert.convert(lUnit)
#         blconvert = self.member.lConvert.convert(lUnit)        
#         return self.member.L * self.section.A* slconvert**2 * blconvert

