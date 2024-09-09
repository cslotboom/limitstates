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
           'SectionRectangle', 'SectionSteel', 'SectionSteelHSS']

#Rename this to SectionArchetype?
class SectionAbstract(ABC):
    """
    The Abstract section should not be directly used. It contains interfaces 
    that other structural classes inheret from. This includes unit definitions,
    and getters for section stiffness.
    """
    
    @abstractmethod
    def getEIx(lunit='m', sunit='Pa' ):
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

        pass
    
    @abstractmethod
    def getEIy(lunit='m', sunit='Pa'):
        """
        Returns EI about the sections local y axis, which is generally the 
        weak axis. Returns in units of sunit x lunit^4  
        
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
        pass
    
    @abstractmethod
    def getGAx(lunit='m', sunit='Pa'):
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
        pass
    
    @abstractmethod
    def getGAy():
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
        pass
    
    def _initUnits(self, lunit:str='mm'):
        """
        Initiates units of the cross sections. Cross sections have length units
        only.

        Parameters
        ----------
        lunit : str, optional
            The length unit to use. The default is 'mm'.
        """

        self.lUnit      = lunit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        
        Parameters
        ----------
        outputUnit : str
            The unit to get the conversion factor to.

        Returns
        -------
        float
            The conversion factor between the current length unit and the
            target output length unit.

        """

        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
class SectionMonolithic(SectionAbstract):
    """
    The Monolithic section should not be used directly, it defines interfaces
    that all sections that use only one uniform material over their
    whole cross section will have.

    """
    
    def __len__(self):
        return 1
    
    def _getCfactors(self, lunit='m', sunit='Pa'):
        return self.mat.sConvert(sunit), self.lConvert(lunit)
    
    def getEA(self, lunit='m', sunit='Pa'):
        """
        Returns the axis stiffness EA for the section. 
        Returns in units of sunit x lunit^2  
        
        Parameters
        ----------
        lunit : float, optional
            The length units to output A in. The default is 'm'.
        sunit : float, optional
            Stress units to output E in. The default is 'Pa'.

        Returns
        -------
        float.
            The EA for the section.

        """
        
        sfactor, lfactor = self._getCfactors(lunit, sunit)
        return self.mat.E * sfactor * self.A * lfactor**2
        
    def getEIx(self, lunit='m', sunit='Pa'):
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
        sfactor, lfactor = self._getCfactors(lunit, sunit)
        return self.mat.E * sfactor * self.Ix * lfactor**4        
    
    def getEIy(self, lunit='m', sunit='Pa'):
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
        sfactor, lfactor = self._getCfactors(lunit, sunit)
        return self.mat.E * sfactor * self.Iy * lfactor**4
    
    def getGAx(self, lunit='m', sunit='Pa'):
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
        sfactor, lfactor = self._getCfactors(lunit, sunit)
        return self.mat.E * sfactor * self.Avx * lfactor**2
         
    def getGAy(self, lunit='m', sunit='Pa'):
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
        sfactor, lfactor = self._getCfactors(lunit, sunit)
        return self.mat.E * sfactor * self.Avy * lfactor**2        
    
    def _initMat(self, mat):
        self.mat = mat
    
class SectionGeneric(SectionMonolithic):
    """
    The generic section is unique in that it has no base geometry.
    Instead, all section propreties are set by the user, instead of infered 
    from geometry!

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
    
    def __init__(self, mat:MaterialElastic, Ix:float = 1, A:float = 1, 
                 Iy:float = 1, J:float = 1, Avx:float = None, Avy:float = None, 
                 lunits:str='mm'):

        
        self.mat:MaterialAbstract = mat
        self.Ix = Ix
        self.A = A
        self.Iy = Iy
        self.J = J
        self.Avx = Avx
        self.Avy = Avy
        
class SectionRectangle(SectionMonolithic):
    """
    A defines a rectangular monolitihic section. Section propreties are defined
    using geometry and mechanics of materials.
    
    Parameters
    ----------
    mat : MaterialElastic
        The material to use for the section.
    b : float
        The section width.
    d : float
        The section depth.
    lunits : str, optional
        The length units. The default is 'mm'.

    """
    def __init__(self, mat:MaterialElastic, b:float, d:float, lunits:str='mm'):
        self._initUnits(lunits)
        self.mat = mat
        
        self.d = d
        self.b = b
        self._setupSectionProps()
    
    def _setupSectionProps(self):
        b = self.b
        d = self.d
        
        self.A   = d*b
        self.Avx = self.A * (5/6)
        self.Avy = self.A * (5/6)
        self.Ix  = b*d**3 / 12
        self.Iy  = d*b**3 / 12
        self.Sx  = b*d**2 / 6
        self.Sy  = (b**2)*d / 6
        
        
        # Torsion modulus
        a = max(b, d)
        b = min(b, d)
        self.J   = (a*b**3) * (1/3 - 0.21*(b/a)*(1 - b**4/(12*a**4)))
        
        # Radius of Gyration
        self.rx = (self.Ix / self.A)**0.5
        self.ry = (self.Iy / self.A)**0.5
        
    def convertUnits(self, lUnit:str):
        """
        Converts the section from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        cfactor = self.lConvert(lUnit)
        self.lUnit = lUnit
        self.b = self.b*cfactor
        self.d = self.d*cfactor
        self._setupSectionProps()
    
    @property
    def name(self):
        return f"{self.b}x{self.d} {self.mat.name} Rectangle"
    
    def __repr__(self):
        return f"<limitstates {self.name} Section.>"

class SectionSteel(SectionMonolithic):
    """
    A class that represents the geometry for a steel section from one of the
    standard shapes. This include I beams (W sections), hollow sections (hss),
    etc.
    
    Steel sections are defined by importing from a database. See section 
    databases for all availible databases.

    Parameters
    ----------
    mat : MaterialElastic
        The steel material to use for the section.
    sectionDict : dict
        The input section dictionary, generally loaded from a database.
    lunits : str, optional
        The length units for the section dictionary. The default is 'mm'.


    """
    sectionClass = None
    def __init__(self, mat:MaterialElastic, sectionDict:dict, lunits:str='mm'):

        # add all items from the input section dictionary
        self.__dict__.update(sectionDict)
        self._initUnits(lunits)
        
        self.mat = mat
    
    @property
    def name(self):
        return f'{self.EDI_Std_Nomenclature} {self.sectionDB}'
       
    def __repr__(self):
        return f'<limitstates {self.name} Section>'
    
    def getCy(self, lunits = 'm', sunits='Pa'):
        lfactor = self.lConvert(lunits)
        sfactor = self.mat.sConvert(sunits)
        return self.A * lfactor**2 * self.mat.Fy * sfactor
    
    @property
    def Cy(self):
        return self.getCy( 'm', 'Pa')
    
    def getZ(self, useX:bool = True, lunits:str = 'mm'):
        """
        Returns the section's plastic modulus in the units and direction input.

        Parameters
        ----------
        useX : bool, optional
            A flag that toggles if the x (strong) or y (weak) axis is used. 
            The default is True, which uses the strong axis.
        lunits : string, optional
            The length units to use for the section. The default is 'mm'.

        Returns
        -------
        float
            The section's plastic modulus in the direction input.

        """
        lfactor = self.lConvert(lunits)
        if useX:
            return self.Zx*lfactor**3
        else:
            return self.Zy*lfactor**3
    
    def getS(self, useX = True, lunits = 'mm'):
        """
        Returns the section's elastic modulus in the units and direction input.

        Parameters
        ----------
        useX : bool, optional
            A flag that toggles if the x (strong) or y (weak) axis is used. 
            The default is True, which uses the strong axis.
        lunits : string, optional
            The length units to use for the section. The default is 'mm'.

        Returns
        -------
        float
            The section's elastic modulus in the direction input.

        """
        
        lfactor = self.lConvert(lunits)
        if useX:
            return self.Sx*lfactor**3
        else:
            return self.Sy*lfactor**3    
    
    def getI(self, useX = True, lunits = 'mm'):
        """
        Returns the section's moment of inertia in the units 
        and direction input.

        Parameters
        ----------
        useX : bool, optional
            A flag that toggles if the x (strong) or y (weak) axis is used. 
            The default is True, which uses the strong axis.
        lunits : string, optional
            The length units to use for the section. The default is 'mm'.

        Returns
        -------
        float
            The section's moment of inertia the direction input.

        """
        
        lfactor = self.lConvert(lunits)
        if useX:
            return self.Ix*lfactor**4
        else:
            return self.Iy*lfactor**4    
    
    
    
class SectionSteelHSS(SectionMonolithic):
    """A class that represents geometry for a steel HSS section."""
    
    def __init__(self, mat:MaterialElastic, sectionDict:dict, lunits:str='mm'):

        # add all items from the input section dictionary
        self.__dict__.update(sectionDict)
        self._initUnits(lunits)
        
        self.mat = mat
    
    
    @property
    def name(self):
        return f'{self.EDI_Std_Nomenclature} {self.sectionDB}'
       
    def __repr__(self):
        return f'<limitstates {self.name} Section>'
    
    
    
class SectionSteelAngle(SectionMonolithic):
    """A class that represents a standard steel W section."""





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


