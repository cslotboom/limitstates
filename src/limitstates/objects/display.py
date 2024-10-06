"""
Returns the raw data that can be plotted or rendered.
All classes are unit agnostic.


"""
from enum import IntEnum

from dataclasses import dataclass
from . section import SectionAbstract
from . geometry import Member

MATCOLOURS = {  'default':'#B3CFE5', 
                'glulam':'#e3c697',     
                'glulamBurnt':'#7a6d65',
                'steel':'#72c2fc'}


class PlotOriginPosition(IntEnum):
    """
    An enumeration that changes the default location a plot is placed at.
    
    1 is plotted at the centroid.
    2 is plotted with the bottom at y = 0, and at the centroid on x.
    3 is plotted with the bottom at y = 0, x = 0.
    """
    centered     = 1 
    bottomCenter = 2
    bottomLeft   = 3

@dataclass
class PlotConfigCanvas:
    """
    Controls how the canvas appears
    
    Parameters
    ----------
    maxFigsize : str, optional
        The largest allowed dimension for the matplotlib figure.
    dpi : str, optional
        The density of pixels to use for the output image.
    originLocation : str, optional
        A flag that changes where the origin is palced in the figure.
        The default is at the centroid of the base object.
    """
    maxFigsize:float = 8
    dpi:float = 300
    originLocation: PlotOriginPosition|int = 1
    
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
        