"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""


from abc import ABC

class Section(ABC):
    """
    Contains interfaces relevant to all sections
    """
    
    def getEIx(sunit='sunit', lunit='Pa'):
        pass
    
    def getEIy(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAx(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAy():
        pass

class SectionMonolithic(Section):
    
    def getEA(sunit='Pa', lunit='m'):
        pass    
    
    def getEIx(sunit='Pa', lunit='m'):
        pass
    
    def getEIy(sunit='Pa', lunit='m'):
        pass
    
    def getGAx(sunit='Pa', lunit='m'):
        pass
    
    def getGAy(sunit='Pa', lunit='m'):
        pass

class SectionLayered(Section):
    """
    Represents a layered section, for example CLT
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

class SectionAggregate(Section):
    """
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
