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

@dataclass()
class Node:
    """
    Represents a node in 2D or 3D space.
    Nodes in 3D are currently not supported.
    
    Nodes have degrees of freedom [dx, dy, rz], or [dx, dy, dz, rx, ry, rz]
    where di is a translation, and ri is a rotation.
    
    Parameters
    ----------
    p1 : list or numpy ndarray
        A list or array of coordinate values in the form [x,y] or [x,y,z].
    units : str
        The units the node is stored in.
    label : str
        A label for the node.
    support : Support
        A support object, either one that is custom defined or defined using
        SupportTypes2D.
    """
    p1:np.ndarray | list
    units:str = 'm'
    label:str = None
    support:Support = SupportTypes2D.FREE.value
    
    def __post_init__(self):
        if not isinstance(self.p1, np.ndarray):
            self.p1 = np.array(self.p1)
            
    def getx(self):
        """
        Returns the x component of a nodes position.
        """
        return self.p1[0]
    
    def gety(self):
        """
        Returns the y component of a nodes position.
        """
        return self.p1[1]
    
    def getz(self):
        """
        Returns the z component of a nodes position, if it exists.
        """
        if len(self.p1) <=2:
            raise Exception('Node is 2D, no z value exists.')
        else:
            return self.p1[2]
        
    def setSupportType(self, newType:Support):
        """
        Sets a new support condition for the node.
        """
        self.support = newType

def _checkUnitsMatch(obj1, obj2):
    if obj1.units == obj2.units:
        return True
    else: 
        raise Exception('Units must match - obj1 has units f{obj1.units}'\
                        'obj2 has units f{obj2.units}')

def getLengthNodes(n1:Node, n2:Node):
    """
    Gets the length between two input nodes.
    Assumes that both points have the same units and dimensionality.

    Parameters
    ----------
    n1 : Node
        The first node.
    n2 : Node
        The second node.

    Returns
    -------
    float
        The length between two nodes.

    """

    _checkUnitsMatch(n1, n2)
    return np.sum((n1.p1 - n2.p1)**2)**0.5

class Curve:
    """
    An arbitary curve connecting two points.
    Currently only lines are used.
    """
    pass

@dataclass()
class Line(Curve):
    """
    A represents straight line in space between two nodes.
    
    Parameters
    ----------
    n1 : Node
        The first Node.
    n2 : Node
        The Second Node.
    units : str
        The length units the line uses. Will match the node units 
    label : str
        A label for the line.
    """

    n1:Node
    n2:Node
    units:str = 'm'
    label:str = None

    def __post_init__(self):
        self.L = getLengthNodes(self.n1, self.n2)

def getLineFromNodes(n1:Node, n2:Node, label = None) -> Line:
    """
    Returns a new line that connects two input nodes.

    Parameters
    ----------
    n1 : Node
        The first Node.
    n2 : Node
        The Second Node.
    label : str
        A label for the line.

    Returns
    -------
    Line
        The output line.

    """

    _checkUnitsMatch(n1, n2)
    return Line(n1, n2, n1.units, label)
   
def getLineFromLength(L:float, units = 'm') -> Line:
    """
    Makes a new line of length L that starts at the origin. Two nodes will be
    defined, one at the origin, and one at poition L in the x axis.
    
    Parameters
    ----------
    L : float
        The length of the line to be defined.
    units : TYPE, optional
        The units to use for the line. The default is 'm'.

    Returns
    -------
    Line
        The output line of length "L".

    """ 
    n1 = Node(np.array([0.,0.,0.]),units)
    n2 = Node(np.array([L, 0.,0.]),units)
    
    line    = Line(n1, n2)
    line.L  = L
    return line    


@dataclass()
class Member:
    """
    Members represent a multi-portion curve, and fully define where a 
    structural element goes in space.
    Members are made of curve segments, which are split by supports.
    Supports are assigned to nodes.
    
    They also contain data about the analysis, such as bending moment diagrams.
    
        
    Parameters
    ----------
    nodes : list[Node]
        The nodes of the member.
    curves : list[Line]
        The curves connecting each node.
    units : str, optional
        The units used in the member. Should match the Node and Line units. 
        The default is 'm'.
    label : str
        A label for the Member.
    loadData : str
        A dictionary containing loading informationa about the Member.
    analysisData : str
        A dictionary containing output information about analysis of the 
        Member, e.g. the bending moment diagram, the shear force diagram, etc.
    """
    nodes:list[Node] = None
    curves:list[Line] = None
    lUnit:str = 'm'
    label:str = None
    loadData:dict = None
    analysisData:dict = None
    lConverter:ConverterLength = None
    L:float = None
    
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

def initSimplySupportedMember(L:float, lUnit:str) -> Member:
    """
    A function that can intialize a simply supported member of length L between
    two points.

    Parameters
    ----------
    L : float
        The member length.
    lUnit : str
        The units to be used by the member and line.

    Returns
    -------
    Member
        The output member.

    """
    
    line = getLineFromLength(L, lUnit)
    line.n1.setSupportType(SupportTypes2D.PINNED.value)
    line.n2.setSupportType(SupportTypes2D.ROLLER.value)
    nodes = [line.n1, line.n2]
    return Member(nodes, [line], lUnit)



# =============================================================================
# Experimental classes, 
# =============================================================================

@dataclass()
class Surface:
    """
    !!!EXPERIMENTAL!!!

    This class is experimental and may not be supported in the full release


    Surfaces are flat elements that are defined between a set of nodes.
    
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
    

class SurfaceRectangular(Surface):
    """
    !!!EXPERIMENTAL!!!

    This class is experimental and may not be supported in the full release
    
    A panel is an element that is a rectangular plane, with width and length.
        
    """
    def __init__(self, nodes:list[Node]):
        super().__init__()
        
        
        