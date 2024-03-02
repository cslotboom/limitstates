"""
Represents netral geometry objects - these represent objects in space and are 
independant of any type of design
"""

from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)
class Node:
    p1:np.ndarray
    label:str = None
    
    def getx(self):
        return self.p1[0]
    
    def gety(self):
        return self.p1[1]
    
    def getz(self):
        if len(self.p1) <=2:
            raise Exception('Node is 2D, no z value exists.')
        else:
            return self.p1[2]

def getLength(n1:Node, n2:Node):
    """
    Gets the length between two input points
    """
    return np.sum((n1.p1 - n1.p1)**2)**0.5


@dataclass(slots=True)
class Line:
    """
    Lines connect two points
    """
    Nodes:list[Node] = None
    length:float = None
    label:str = None
    

def getLinePoints(n1:Node, n2:Node):
    """
    Returns a new line from two input nodes

    Returns
    -------
    None.

    """
    
    
    
    
  
def getLineLength():
    """
    Returns a new line

    Returns
    -------
    None.

    """  
    
    
@dataclass(slots=True)
class Member:
    """
    Members aggregate lines with sections.
    """
    Line:float
    Nodes:list[Node] = None
    label:str = None






