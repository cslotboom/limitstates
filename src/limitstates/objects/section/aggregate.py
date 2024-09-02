"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""

from .section import SectionAbstract
from ..material import MaterialElastic

from dataclasses import dataclass
from numpy import ndarray

@dataclass
class LayerClt:
    t:float
    orientation:float        
    mat:MaterialElastic
    y:float = None
    w:float = None
    A:float = None
    
    
    def setI():
        self.I = t**3 * w / 12



class CltLayerGroup:
    # y:ndarray[float]
    # w:ndarray[float]
    # A:ndarray[float]
    # mats:list[MaterialElastic]
    layers:list[Layer]
    ybar:float
    dnet:float
    
    def setYbar(self):
        
        
    def set
        
    

class SectionLayered(SectionAbstract):
    """
    Represents a layered section, for example CLT.
    """
    
    def getEA(sunit='sunit', lunit='Pa'):
        pass    
    
    def getEIx(sunit='sunit', lunit='Pa'):
        pass
    
    def getEIy(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAx(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAy(sunit='sunit', lunit='Pa'):
        pass

    




# class SectionAggregate(Section):
#     """
#     """
    
#     def getEA(sunit='sunit', lunit='Pa'):
#         pass    
    
#     def getEIx(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getEIy(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getGAx(sunit='sunit', lunit='Pa'):
#         pass
    
#     def getGAy(sunit='sunit', lunit='Pa'):
#         pass
