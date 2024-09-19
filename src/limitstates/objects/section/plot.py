"""
Allows sections to be plotted.


Features of a plot:
    - Create a visualization of the section
    - Show a dictionary of common propreties Ix, Sx, Zx, etc.
    - SHow a dictionary of results


"""

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as np
from abc import ABC
from dataclasses import dataclass

from .section import SectionAbstract, SectionRectangle, SectionSteel, SteelSectionTypes


class GeometryParameters(ABC):

    def getPlotVerticies(self):
        pass

@dataclass
class GeomRectangle(GeometryParameters):
    h:float
    b:float
    x0:float = 0
    y0:float = 0
        
    def getPlotVerticies(self):
        
        h = self.h
        b = self.b
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-b/2, -b/2 , b/2, b/2, -b/2]) + x0
        y = np.array([0 ,    h ,   h,   0,    0])  + y0
        return list(x), list(y)

@dataclass
class GeomIbeam(GeometryParameters):
    d:float
    tw:float
    bf:float
    tf:float
    rf:float = None
    rw:float = None

    x0:float = 0
    y0:float = 0
    
    def getPlotVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h = self.d 
        w = self.bf 
        tw = self.tw 
        tf = self.tf 
        x0 = self.x0
        y0 = self.y0
        
        x = np.array([-w/2, w/2, w/2, tw/2, tw/2, w/2,  
                      w/2, -w/2, -w/2, -tw/2, -tw/2, -w/2])
        y = np.array([ h/2, h/2, h/2 - tf, h/2 - tf, -h/2 + tf,  
             -h/2 + tf, -h/2,-h/2, -h/2+tf, -h/2+tf, h/2-tf, h/2-tf])
        
        
        return list(x +x0), list(y + y0)    


@dataclass
class GeomIbeamRounded(GeometryParameters):
    d:float
    tw:float
    bf:float
    tf:float
    rf:float
    rw:float

    x0:float = 0
    y0:float = 0
    NradiusPoints:int = 6
        
    def _getcornerVerticies(self, x0, y0, r, dx = 1, dy = 1):
        """
        dx /  dy are direction terms which are either 1 or negative 1
        """
        
        x = np.cos(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dx*r + x0
        y = np.sin(np.linspace(0,1,self.NradiusPoints)*np.pi/2)*dy*r + y0
        
        return list(x), list(y)
        
        
    
    def getPlotVerticies(self):
        """ Gets the a list of (x, y) verticies in clockwise order"""
        h   = self.d 
        w   = self.bf 
        tw  = self.tw 
        tf  = self.tf 
        x0  = self.x0
        y0  = self.y0
        rf:float = self.rf
        rw:float = self.rw

        
        tLeg_x = [-w/2, w/2]
        tLeg_y = [ h/2, h/2]
        
        # Top right flange
        xCorner = w/2 - rf
        yCorner = h/2 - tf + rf
        trfx, trfy = self._getcornerVerticies(xCorner, yCorner, rf, 1, -1)

        # Top right web
        xCorner = tw/2 + rw
        yCorner = h/2 - tf - rw
        trwx, trwy = self._getcornerVerticies(xCorner, yCorner, rw, -1, 1)
        trwx = trwx[::-1]
        trwy = trwy[::-1]

        # Bottom right web
        xCorner = tw/2 + rw
        yCorner = -h/2 + tf + rw
        brwx, brwy = self._getcornerVerticies(xCorner, yCorner, rw, -1, -1)
        
        # Bottom right flange
        xCorner = w/2 - rf
        yCorner = -h/2 + tf - rf
        brfx, brfy = self._getcornerVerticies(xCorner, yCorner, rf, 1, 1)
        brfx = brfx[::-1]
        brfy = brfy[::-1]
        
        # Bottom leg
        bLeg_x = [w/2, -w/2]
        bLeg_y = [-h/2,-h/2]
        
        # Bottom left flange
        xCorner = -w/2 + rf
        yCorner = -h/2 + tf  - rf
        blfx, blfy = self._getcornerVerticies(xCorner, yCorner, rf, -1, 1)

        # Bottom left web
        xCorner = -tw/2 - rw
        yCorner = -h/2 + tf +rw 
        blwx, blwy = self._getcornerVerticies(xCorner, yCorner, rw, 1, -1)
        blwx = blwx[::-1]
        blwy = blwy[::-1]
        
        # top left web
        xCorner = -tw/2 - rw
        yCorner = h/2 - tf - rw
        tlwx, tlwy = self._getcornerVerticies(xCorner, yCorner, rw, 1, 1)

        # top left flange
        xCorner = -w/2 + rf
        yCorner = h/2 - tf + rf
        tlfx, tlfy = self._getcornerVerticies(xCorner, yCorner, rf, -1, -1)                
        tlfx = tlfx[::-1]
        tlfy = tlfy[::-1]        
        
        x = tLeg_x + trfx + trwx + brwx + brfx + bLeg_x + blfx + blwx + tlwx + tlfx
        y = tLeg_y + trfy + trwy + brwy + brfy + bLeg_y + blfy + blwy + tlwy + tlfy        
        
        return list(np.array(x) + x0), list(np.array(y) + y0)    



@dataclass
class PlotDisplayProps:
    """
    XXX
    A class that represents possible display propreties for the 
    """
    c:str = '#B3CFE5'
    maxFigsize:float = 8


class SectionPlotter:
    
    plotOffset = 0.05
    
    
    def __init__(self, geom:GeometryParameters, displayProps:PlotDisplayProps):
        
        self.geom = geom
        self.maxFigsize = displayProps.maxFigsize
        self.c = displayProps.c
        
    def setGeom(self, goem:GeometryParameters):
        pass
        
    
    def _getPlotLimits(self, x:list[float], y:list[float]):

        dx = max(x) - min(x)
        dy = max(y) - min(y)
        xmin = min(x) - self.plotOffset*(1+dx)
        xmax = max(x) + self.plotOffset*(1+dx)
        
        ymin = min(y) - self.plotOffset*(1+dy)
        ymax = max(y) + self.plotOffset*(1+dy)
        
        return (xmin, xmax), (ymin, ymax)
     
    def _getPlotSize(self, xlims:list[float], ylims:list[float]):
        dx = xlims[1] - xlims[0]
        dy = ylims[1] - ylims[0]
        self.dx = dx
        self.dy = dy
        dmax = max(dy, dx)
        return dx / dmax * self.maxFigsize, dy / dmax * self.maxFigsize
    
    def plot(self, *args, **kwargs):
        x, y = self.geom.getPlotVerticies()
        xlims, ylims = self._getPlotLimits(x,y)
        
        xplot, yplot = self._getPlotSize(xlims, ylims)
        
        # Set the dimensions / aspect ratio of the plot
        fig, ax = plt.subplots(figsize=(xplot, yplot))
        
        # Set the dimensions /     
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        
        fig.set
        ax.fill(x, y, self.c, *args, **kwargs)
        ax.plot()
        
        return fig, ax
    
    def _plotInformation(infoDict):
        pass
    
    def plotDesignInfo(self, fig, ax, infoDict):
        # x0 = np.average(ax.get_xlim())
        # y0 = np.average(ax.get_ylim())
        
        x0 = ax.get_xlim()[-1] + self.dx / 20
        y0 = ax.get_ylim()[-1]
        
        text = "Section Information.\n"
        for item in infoDict:
            text += item +": " + str(round(infoDict[item])) + "\n"
        ax.text(x0, y0, text)
        
    
    def plotSectionInfo():
        pass


def _plotGeomFactory(section:SectionAbstract, *args) -> (GeometryParameters, PlotDisplayProps):
    """
    Gets the appropriate geometry and dispalay propreties 

    """
    if isinstance(section, SectionRectangle):
        geom = GeomRectangle(section.b, section.d, *args)
        defaultDisplayProps = PlotDisplayProps()        
    elif isinstance(section, SectionSteel):
        geom, defaultDisplayProps = _plotFactorySteel(section, *args)
        {'Ix':section.Ix, 'Sx':section.Sx, 'Zx':section.Zx,
         'Iy':section.Ix, 'Sy':section.Sy, 'Zx':section.Zy,}
    else:
        raise Exception
        
    return geom, defaultDisplayProps



def _plotFactorySteel(section:SectionSteel, *args):
    
    if SteelSectionTypes.w == section.typeEnum:
        # If there is information about the rounded section, plot that
        if hasattr(section, 'r1') and hasattr(section, 'r2'):
            geom = GeomIbeamRounded(section.d, 
                                    section.tw, 
                                    section.bf, 
                                    section.tf,  
                                    section.r1,  
                                    section.r2,  
                                    *args)
            defaultDisplayProps = PlotDisplayProps()
        # If there is information about the rounded section, plot that
        else:
            geom = GeomIbeam(section.d, 
                             section.tw, 
                             section.bf, 
                             section.tf,  
                             *args)
            defaultDisplayProps = PlotDisplayProps()

    return geom, defaultDisplayProps


def _setupSummaryDict(listIn, ):
    pass


def plotSection(section:SectionAbstract, 
                xy0: tuple[float,float] = (0,0), 
                dispProps: PlotDisplayProps = None,
                summarizeGeometry: bool|list[str]=False):
    """
    Creates a plot of the section centered at xy0.
    
    The figure propreties can be set by using a custom PlotDisplayProps object.

    Parameters
    ----------
    section : SectionAbstract
        The sectin to be plotted.
    xy0 : float, optional
        The x/y point to use for the center of the plot. The default is (0,0).
    dispProps : PlotDisplayProps, optional
        The display propreties to use. The default is None.
    summarizeGeometry : bool|list[str], optional
        DESCRIPTION. The default is False.

    Returns
    -------
    fig : matplotlib figure
        The output matplotlib figure.
    ax : matplotlib axis
        The output matplotlib axis.

    """
    
    geom, defaultDispProps = _plotGeomFactory(section, xy0[0], xy0[1])

    if not dispProps:
        dispProps = defaultDispProps    

    plotter = SectionPlotter(geom, dispProps)
    fig, ax = plotter.plot()
    
    # if summarizeGeometry:
    #     summaryAttrList = {'Iy':section.Iy, 'Ix':section.Ix}
    #     plotter.plotDesignInfo(fig, ax, summaryAttrList)
    
    return fig, ax
