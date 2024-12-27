"""

The display library contains configuration objectsthat are used to control 
the appearance of limitstates objects.
Returns the raw data that can be plotted or rendered.
All classes are unit agnostic.


"""
from typing import Optional
from enum import IntEnum

from dataclasses import dataclass, field
from . section import SectionAbstract
from . geometry import Member

MATCOLOURS = {  'default':'#B3CFE5', 
                'clt':'#e3c697',     
                'cltWeak':'#e8d1ab',     
                'glulam':'#e3c697',     
                'glulamBurnt':'#7a6d65',
                'steel':'#72c2fc',
                'lineInternal':'#d9d9d9',
                'black':'#000000'}


class PlotOriginPosition(IntEnum):
    """
    An enumeration that changes the default location a plot is placed at.
    
    - 1 is plotted at the centroid.
    - 2 is plotted with the bottom at y = 0, and at the centroid on x.
    - 3 is plotted with the bottom at y = 0, x = 0.
    """
    centered     = 1 
    bottomCenter = 2
    bottomLeft   = 3

@dataclass
class PlotConfigCanvas:
    """
    Controls how the canvas appears, i.e. size, pixel density, section origin
    location.
    
    Parameters
    ----------
    maxFigsize : str, optional
        The largest allowed dimension for the matplotlib figure.
    dpi : str, optional
        The density of pixels to use for the output image.
    showAxis : bool, optional
        A toggle that will turn on or off the axis of the matplotlib canvas..
    """
    maxFigsize:float = 8
    dpi:float = 300
    showAxis:bool = True
    
    
@dataclass
class PlotConfigObject:
    """
    Controls the appearance of a single object on a matplotlib canvas.
    
    Parameters
    ----------
    c : str, optional
        The colour to use for the object.
    showOutline : bool, optional
        A flag that turns on or off the plots outline.
    cLine : str, optional
        The colour to use for the outline of the object.    
    lineWidth : float, optional
        The linewidth to use for the object, in units of the canvas.
    newOriginLocation : int|PlotOriginPosition
        A flag that changes the default location the plot is placed at.
        
        1 is plotted at the centroid.
        2 is plotted with the bottom at y = 0, and at the centroid on x.
        3 is plotted with the bottom at y = 0, x = 0.
    cFillLines : str, optional
        The colour to use for any internal fill lines.
    cFillPatch : str, optional
        The colour to use for any internal fill patches.

    """
    c:str = MATCOLOURS['default']
    showOutline:bool = True
    cLine:str = MATCOLOURS['black']
    lineWidth:float = 1
    originLocation: PlotOriginPosition|int = 1
    cFillLines:Optional[str] = None
    cFillPatch:Optional[str] = None


@dataclass
class EleDisplayProps:
    """
    A class that aggregates all propreties which will be used to visualize
    outputs from elements.
    
    Parameters
    ----------
    section : str, SectionAbstract
        The section that will be used for plotting/display. 
        This can be different than design section.
    member : str, SectionAbstract
        The member used for plotting/display. This can be different than the
        design section..
    configCanvas : str, PlotConfigCanvas
        A configuration object that stores the canvas's . 
    configObject : str, PlotConfigObject
        A configuration object that stores the objects display propreties,
        i.e. colour linestyle etc. 
    """
    
    section:Optional[SectionAbstract] = None
    member:Optional[Member] = None
    
    configObject: Optional[PlotConfigObject] = None
    configCanvas: Optional[PlotConfigCanvas] = None
        
    def __repr__(self):
        "<limitStates output Propreties Dataclass>"
        
    def __post_init__(self):
        if self.configCanvas == None:
            self.configCanvas = PlotConfigCanvas()
 
        if self.configObject == None:
            self.configObject = PlotConfigObject('#B3CFE5')
            
    def setPlotOrigin(self, newOriginLocation:int|PlotOriginPosition):
        """
        Sets the type of origin location to use for the object.

        Parameters
        ----------
        newOriginLocation : int|PlotOriginPosition
            A flag that changes the default location the plot is placed at.
            
            1 is plotted at the centroid.
            2 is plotted with the bottom at y = 0, and at the centroid on x.
            3 is plotted with the bottom at y = 0, x = 0.

        """
        self.configObject.originLocation = newOriginLocation