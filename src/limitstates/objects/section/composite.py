"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""

from abc import ABC, abstractmethod
from enum import Enum

from .. material import MaterialAbstract, MaterialElastic
from ... units import ConverterLength
# from .plot import GeomRectangle, SectionPlotter, plotDisplayParameters

from .section import SectionAbstract

__all__ = ['SectionComposite']



class SectionComposite(SectionAbstract):

    
    def __init__(self, layers:list[SectionAbstract]):
        """
        Composite sections 
        """
        pass
    
    def getEA(sUnit='sUnit', lUnit='Pa'):
        pass    
    
    def getEIx(sUnit='sUnit', lUnit='Pa'):
        pass
    
    def getEIy(sUnit='sUnit', lUnit='Pa'):
        pass
    
    def getGAx(sUnit='sUnit', lUnit='Pa'):
        pass
    
    def getGAy(sUnit='sUnit', lUnit='Pa'):
        pass


