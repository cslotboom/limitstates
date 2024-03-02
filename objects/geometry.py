"""
Represents netral geometry objects - these represent objects in space and are 
independant of any type of design
"""

from dataclasses import dataclass
import numpy as np

__all__ = ['Node', 'getLengthNodes',
           'Line', 'getLineFromNodes', 'getLineFromLength',
           'Member']

@dataclass(slots=True)
class Node:
    p1:np.ndarray | list
    units:str = 'm'
    label:str = None
    
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

@dataclass(slots=True)
class Line:
    n1:Node
    n2:Node
    length:float = None
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
    line.length = getLengthNodes(n1, n2)
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
    n2 = Node(np.array([L,0.,0.]),units)
    
    line    = Line(n1, n2)
    line.length  = L
    return line    
    
    
@dataclass(slots=True)
class Member:
    """
    Members aggregate lines with sections.
    """
    Line:float
    Nodes:list[Node] = None
    label:str = None






