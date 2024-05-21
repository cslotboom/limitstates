"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""

from abc import ABC, abstractmethod
from .. material import MaterialAbstract, MaterialElastic
from ... units import ConverterLength

__all__ = ['SectionAbstract', 'SectionMonolithic', 'SectionGeneric', 
           'SectionRectangle']

class SectionAbstract(ABC):
    """
    Contains interfaces relevant to all sections
    """
    
    @abstractmethod
    def getEIx(sunit='Pa', lunit='m'):
        """
        IE about the sections local x axis
        """
        pass
    
    @abstractmethod
    def getEIy(sunit='Pa', lunit='m'):
        """
        IE about the sections local y axis
        """
        pass
    
    @abstractmethod
    def getGAx(sunit='Pa', lunit='m'):
        pass
    
    @abstractmethod
    def getGAy():
        pass
    
    def _initUnits(self, lunit:str='mm'):
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
    
class SectionMonolithic(SectionAbstract):
    """
    Defines interfaces common to all monotonic sections.
    These sections have propreties that are consistent 
    """
    
    def __len__(self):
        return 1
    
    def _getCfactors(self, sunit='Pa', lunit='m'):
        return self.mat.sConvert(sunit), self.lConvert(lunit)
    
    def getEA(self, sunit='Pa', lunit='m'):
        sfactor, lfactor = self._getCfactors(sunit, lunit)
        return self.mat.E * sfactor * self.A * lfactor**2
        
    def getEIx(self, sunit='Pa', lunit='m'):
        sfactor, lfactor = self._getCfactors(sunit, lunit)
        return self.mat.E * sfactor * self.Ix * lfactor**4        
    
    def getEIy(self, sunit='Pa', lunit='m'):
        sfactor, lfactor = self._getCfactors(sunit, lunit)
        return self.mat.E * sfactor * self.Iy * lfactor**4
    
    def getGAx(self, sunit='Pa', lunit='m'):
        sfactor, lfactor = self._getCfactors(sunit, lunit)
        return self.mat.E * sfactor * self.Avx * lfactor**2
         
    def getGAy(self, sunit='Pa', lunit='m'):
        sfactor, lfactor = self._getCfactors(sunit, lunit)
        return self.mat.E * sfactor * self.Avy * lfactor**2        
    
    def _initMat(self, mat):
        self.mat = mat
    
class SectionGeneric(SectionMonolithic):
    """
    The user section is unique in that it has no base geometry.
    All section propreties are set by the user, not infered from geometry!

    Parameters
    ----------
    mat : MaterialAbstract
        The material to use in the section.
    Ix : float, optional
        The moment of interia of the section about it's local x axis. 
        The default is 1.
    A : float, optional
        The area of the section about it's local. The default is 1.
    Iy : float, optional
        The moment of interia of the section about it's local y axis. 
        The default is 1.
    J : float, optional
        The torsion constant for the section. The default is 1.
    Ax : float, optional
        The area in the shear direction x. The default is None.
    Ay : float, optional
        The area in the shear direction y. The default is None.
    lunits : str, optional
        The units for length used in the section. The default is 'mm'.

    Returns
    -------
    None.

    """
    
    def __init__(self, mat:MaterialElastic, Ix = 1, A = 1, Iy = 1, J = 1, 
                 Avx = None, Avy = None, lunits='mm'):

        
        self.mat:MaterialAbstract = mat
        self.Ix = Ix
        self.A = A
        self.Iy = Iy
        self.J = J
        self.Avx = Avx
        self.Avy = Avy

class SectionRectangle(SectionMonolithic):

    def __init__(self, mat:MaterialElastic, b:float, d:float, lunits='mm'):
        
        self._initUnits(lunits)
        self.mat = mat
        self.d = d
        self.b = b
        
        self.A   = self.d*self.b
        self.Avx = self.A * (5/6)
        self.Avy = self.A * (5/6)
        self.Ix  = self.b*self.d**3 / 12
        self.Iy  = self.d*self.b**3 / 12
        
        # Torsion modulus
        a = max(b, d)
        b = min(b, d)
        self.J   = (a*b**3) * (1/3 - 0.21*(b/a)*(1 - b**4/(12*a**4)))
        
        # Radius of Gyration
        self.rx = (self.Ix / self.A)**0.5
        self.ry = (self.Ix / self.A)**0.5

class SectionDatabase(SectionMonolithic):
    """
    A section that is defined from a database. Generally used for steel or more
    complex shapes where section geometry requires a large number of parameters
    to define.

    Parameters
    ----------
    mat : MaterialAbstract
        The material to use in the section.
    sectionDict : dict
        A dictionary containing all of the information necessary to define
        the section.
    lunits : str, optional
        The units for length used in the section. The default is 'mm'.

    Returns
    -------
    None.

    """

    def __init__(self, mat:MaterialElastic, sectionDict:dict, lunits='mm'):
        
        self.__dict__.update(sectionDict)
        self._initMat(mat)
        self._initUnits(lunits)


class SectionComposite(SectionAbstract):

    
    def __init__(self, layers:list[SectionAbstract]):
        """
        Composite sections 
        """
        pass
    
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



# =============================================================================
# 
# =============================================================================

# class SectionLayered(Section):
#     """
#     Represents a layered section, for example CLT
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
