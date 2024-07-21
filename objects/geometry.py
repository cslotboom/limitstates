"""
Represents netral geometry objects - these represent objects in space and are 
independant of any type of design
"""

from dataclasses import dataclass
from .support import Support, SupportTypes2D
from .. units import ConverterLength
import numpy as np


__all__ = ['Node', 'getLengthNodes',
           'Line', 'getLineFromNodes', 'getLineFromLength',
           'Member', 'initSimplySupportedMember']

@dataclass(slots=True)
class Node:
    p1:np.ndarray | list
    units:str = 'm'
    label:str = None
    support:Support = SupportTypes2D.FREE.value
    
    def __post_init__(self):
        if not isinstance(self.p1, np.ndarray):
            self.p1 = np.array(self.p1)
            
    def getx(self):
        return self.p1[0]
    
    def gety(self):
        return self.p1[1]
    
    def getz(self):
        if len(self.p1) <=2:
            raise Exception('Node is 2D, no z value exists.')
        else:
            return self.p1[2]
        
    def setSupportType(self, newType:Support):
        self.support = newType

def _checkUnitsMatch(obj1, obj2):
    if obj1.units == obj2.units:
        return True
    else: 
        raise Exception('Units must match - obj1 has units f{obj1.units}'\
                        'obj2 has units f{obj2.units}')

def getLengthNodes(n1:Node, n2:Node):
    """
    Gets the length between two input points
    Assumes that both points have the same units.

    """
    _checkUnitsMatch(n1, n2)
    return np.sum((n1.p1 - n2.p1)**2)**0.5

class Curve:
    pass

@dataclass(slots=True)
class Line(Curve):
    n1:Node
    n2:Node
    L:float = None
    units:str = 'm'
    label:str = None

def getLineFromNodes(n1:Node, n2:Node) -> Line:
    """
    Returns a new line from two input nodes.

    Returns
    -------
    None.

    """
    _checkUnitsMatch(n1, n2)
    line = Line(n1,n2)
    line.L = getLengthNodes(n1, n2)
    return line
   
def getLineFromLength(L:float, units = 'm') -> Line:
    """
    Returns a new line.
    By default uses the x axis for the line.

    Returns
    -------
    None.

    """  
    n1 = Node(np.array([0.,0.,0.]),units)
    n2 = Node(np.array([L, 0.,0.]),units)
    
    line    = Line(n1, n2)
    line.L  = L
    return line    


@dataclass(slots=True)
class Member:
    """
    Members represent a multi-portion curve, and fully define where a 
    structural element goes in space.
    Members are made of curve segments, which are split by supports.
    Supports are assigned to nodes.
    
    They also contain data about the analysis, such as bending moment diagrams.
    
    """
    nodes:list[Node] = None
    curves:list[Curve] = None
    lUnit:str = 'm'
    label:str = None
    loadData:dict = None
    analysisData:dict = None
    L:float = None
    lConverter:ConverterLength = None

    
    def __post_init__(self):
        self._initUnits(self.lUnit)
        self.L = sum([curve.L for curve in self.curves])
        
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

    #TODO: add this!
    def convertLunit(self):
        pass

def initSimplySupportedMember(L:float, lUnit:str):
    """
    Initialized a simply supported member.

    Parameters
    ----------
    L : float
        The member length.
    lUnit : str
        The length units.

    Returns
    -------
    Member
        A simply supported member.

    """
    
    line = getLineFromLength(L, lUnit)
    line.n1.setSupportType(SupportTypes2D.PINNED.value)
    line.n2.setSupportType(SupportTypes2D.ROLLER.value)
    nodes = [line.n1, line.n2]
    return Member(nodes, [line], lUnit)

@dataclass(slots=True)
class Surface:
    """
    Surfaces are flat planes that are defined between a set of nodes.
    
    They do not have width/length.
        
    """
    nodes:list[Node] = None
    lUnit:str = 'm'
    label:str = None
    loadData:dict = None
    analysisData:dict = None
    lConverter:ConverterLength = None

    def __post_init__(self):
        self._initUnits(self.lUnit)
        
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

    #TODO: add this!
    def convertLunit(self):
        pass
    

class Panel(Surface):
    """
    A panel is an element that is a rectangular plane, with width and length.
        
    """
    def __init__(self):
        super().__init__()