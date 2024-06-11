"""
Represents supports and support fixities. 
These are assigned to memebers and can be used by analysis classes.
They are all code neutral
"""

from dataclasses import dataclass
from enum import Enum

__all__ = ["Support", "SupportTypes2D"]

@dataclass(slots=True)
class Support:
    name:str = None
    fixity:list[int] = None
    reaction:dict = None
    
class SupportTypes2D(Enum):
    FREE    = Support('free',   (0,0,0))
    ROLLER  = Support('roller', (0,1,0))
    PINNED  = Support('pinned', (1,1,0))
    FIXED   = Support('fixed',  (1,1,1))






