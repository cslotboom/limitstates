"""
Represents supports and support fixities. 
These are assigned to memebers and can be used by analysis classes.
They are all code neutral
"""

from dataclasses import dataclass
from enum import Enum

__all__ = ["Support", "SupportTypes2D"]

@dataclass()
class Support:
    """
    Represents a support in 2D or 3D space. Currently only 2D supportes are
    supported.
    Nodes have degrees of freedom [dx, dy, rz], or [dx, dy, dz, rx, ry, rz]
    where di is a translation, and ri is a rotation.
    
    
    Parameters
    ----------
    name : str
        The name for the node.
    fixity : list | tuple
        A list or tuple representing the fixity of the node. A one means that
        the degree of freedom is fixed, and 0 means it is free to translate.
    reaction : dict
        XXX Currently currently unused. In the future will hold reaction force
        data.
    """
    name:str = None
    fixity:list[int] = None
    reaction:dict = None
    # is2D:bool = True

    def is2D(self):
        return len(self.fixity) == 3
    
    def isFree(self):
        return self.fixity == (0,0,0)
    
class SupportTypes2D(Enum):
    """
    A enumeration class that represents all possible support types in 2D.
    The support type is a list of one or zero for each degree of freedom the
    node has, where 1 means the degree of freedom is fixed and 0 
    means it is free.
    """
    FREE    = Support('free',   (0,0,0))
    ROLLER  = Support('roller', (0,1,0))
    PINNED  = Support('pinned', (1,1,0))
    FIXED   = Support('fixed',  (1,1,1))






