"""
Returns the raw data that can be plotted or rendered.
All classes are unit agnostic.


"""

from dataclasses import dataclass
from . section import SectionAbstract
from . geometry import Member

MATCOLOURS = {  'default':'#B3CFE5', 
                'glulam':'#e3c697',     
                'glulamBurnt':'#7a6d65',
                'steel':'#72c2fc'}


@dataclass
class PlotConfigCanvas:
    """
    Controls how the canvas appears
    """
    maxFigsize:float = 8
    dpi:float = 300
    
@dataclass
class PlotConfigObject:
    """
    Controls a single object in the the canvas appears
    """
    c:str = MATCOLOURS['default']
    showOutline:bool = True
    lineWidth:bool = 0.5


@dataclass
class EleDisplayProps:
    """
    A class that aggregates all propreties which will be used to visualize
    outputs from element.
    """
    section:SectionAbstract = None
    member:Member = None
    displayColor:str = '#B3CFE5'
    
    configCanvas: PlotConfigCanvas = PlotConfigCanvas()
    configObject: PlotConfigObject = PlotConfigObject(displayColor)
        
    def __repr__(self):
        "<limitStates output Propreties Dataclass>"
        