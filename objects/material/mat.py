from ... units import ConverterStress, ConverterDensity


"""
Stores information relevant to all materials.
Material are relevant to design.

"""

class Material:
    
    """
    The common material object. Contains interfaces relevant for all design
    objects.
    """
    
    def _initUnits(self, sunit:str='MPa', rhounit='kg/m3'):
        """
        Inititiates the unite of the material.
        """
        self.sunit      = sunit
        self.sconvert   = ConverterStress()        
        self.rhounit  = rhounit
        self.sconvert = ConverterDensity()
        
class MaterialElastic(Material):

    def __init__(self, E:float, G:float=None, rho=None, 
                 sunit:str='MPa', rhounit='kg/m3'):
        """
        Represents a typical elastic material. This material is code agnostic
        and generally not used in design.
        """
        self._initUnits()
        self.E = E
        self.G = G
        self.rho = rho

        
        