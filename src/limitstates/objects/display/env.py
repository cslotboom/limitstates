"""
Stores display propreties that are used globaly

"""

from dataclasses import dataclass

MATCOLOURS = {  'default':'#B3CFE5', 
                'glulam':'#e3c697',     
                'glulamBurnt':'#7a6d65',
                'steel':'#72c2fc'}


@dataclass
class CanvasPlotConfig:
    """
    Controls how the canvas appears
    """
    maxFigsize:float = 8
    dpi:float = 300
    
@dataclass
class CanvasObjectConfig:
    """
    Controls a single object in the the canvas appears
    """
    c:str = MATCOLOURS['default']
    showOutline:bool = True
    lineWidth:bool = 0.5
