
# from abc import ABC, abstractmethod
from dataclasses import dataclass

from .. geometry import Line, getLineFromLength
from .. section import SectionAbstract
from ... units import ConverterLength

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
    length:float
    designProps:DefaultDesignProps
    userProps:UserProps
    
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
    
    def getVolume(self, lUnit='m'):
        slconvert = self.section.lConvert.convert(lUnit)
        blconvert = self.lConvert.convert(lUnit)        
        return self.L * self.section.A* slconvert**2 * blconvert
        
    def _initUnits(self, lunit:str='m'):
        """
        Inititiates the unit of the section.
        """
        self.lUnit      = lunit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        """
        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
class BeamColumn(Element1D):
    
    def __init__(self, line:Line, section:SectionAbstract, lUnit:str='m', 
                 designProps:dataclass = None, userProps:dataclass = None):
        
        self._initMain(line, section, lUnit)
        
        if designProps is None:
            designProps = DefaultDesignProps()
        self.designProps = designProps
        
        if userProps is None:
            userProps = UserProps()
        self.userProps = userProps
    
    def _initMain(self, line:Line, section:SectionAbstract, lUnit:str='m'):
        self.line = line
        self.L = line.length
        self.section:SectionAbstract = section
        self._initUnits(lUnit)
    
    def _initUserProps(self, userProps:dataclass = None):
        
        if userProps is None:
            userProps = UserProps()
        self.userProps = userProps
        
    def __repr__(self):
        return f"<limitstates {self.L}{self.lUnit} BeamColumn>"


def getBeamColumn(L:float, section:SectionAbstract, lunit:str, 
                  designProps:dict=None) -> BeamColumn:
    """
    A function used to return a beamcolumn based on an input length

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
    line = getLineFromLength(L, lunit)
    return BeamColumn(line, section, lunit, designProps)





