"""
Manages matplotlib plotting of sections.


Features of a plot:
    - Create a visualization of the section
    - Show a dictionary of common propreties Ix, Sx, Zx, etc.
    - SHow a dictionary of results


"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.patches import Polygon, Rectangle

from ..section import SectionAbstract, SectionRectangle, SectionSteel, SteelSectionTypes
from ..element import BeamColumn, DisplayProps

from .env import MATCOLOURS, CanvasPlotConfig, CanvasObjectConfig
from .model import GeomModel, GeomModelRectangle, GeomModelIbeam, GeomModelIbeamRounded


class SectionPlotter:
    
    plotOffset = 0.05
    def __init__(self, baseGeom:GeomModel, canvasProps:CanvasPlotConfig):
        
        self.geom = baseGeom
        self.maxFigsize = canvasProps.maxFigsize
                
    
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
    
    def initPlot(self):
        x, y = self.geom.getVerticies()
        xlims, ylims = self._getPlotLimits(x,y)
        xplot, yplot = self._getPlotSize(xlims, ylims)
        
        # Set the dimensions / aspect ratio of the plot
        fig, ax = plt.subplots(figsize=(xplot, yplot))
        
        # Set the dimensions /     
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        
        return fig, ax
    
    def plot(self, ax, xy, objectConfig, *args, **kwargs):
        """
        plot a set of xy points on the canvas.
        """
        c = objectConfig.c
        # x, y = self.geom.getPlotVerticies()
        ax.fill(xy[:,0], xy[:,1], *args, c = c, **kwargs)
        if objectConfig.showOutline:
            ax.plot(xy[:,0], xy[:,1], linewidth = objectConfig.lineWidth)
        
        return ax
    
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





def _plotGeomFactory(section:SectionAbstract, *args) -> (GeomModel, CanvasObjectConfig):
    """
    Gets the appropriate geometry and dispalay propreties 

    """
    
    # We could return an enumeration instead of using this factory, and have
    # a 'switch'
    if isinstance(section, SectionRectangle):
        geom = GeomModelRectangle(section.b, section.d, *args)
        defaultProps = CanvasObjectConfig(c = MATCOLOURS['glulam'])
    elif isinstance(section, SectionSteel):
        geom = _plotFactorySteel(section, *args)
        defaultProps = CanvasObjectConfig(c = MATCOLOURS['steel'])
    else:
        raise Exception
        
    return geom, defaultProps

def _plotFactorySteel(section:SectionSteel, *args):
    
    if SteelSectionTypes.w == section.typeEnum:
        # If there is information about the rounded section, plot that
        if hasattr(section, 'r1') and hasattr(section, 'r2'):
            geom = GeomModelIbeamRounded(section.d, 
                                         section.tw, 
                                         section.bf, 
                                         section.tf,  
                                         section.r1,  
                                         section.r2,  
                                         *args)
        # If there is information about the rounded section, plot that
        else:
            geom = GeomModelIbeam(section.d, 
                                  section.tw, 
                                  section.bf, 
                                  section.tf,  
                                  *args)
    return geom


def _setupSummaryDict(listIn, ):
    pass


def plotSection(section:SectionAbstract, 
                xy0: tuple[float,float] = (0,0), 
                canvasConfig: CanvasPlotConfig = None,
                objectConfig: CanvasObjectConfig = None,
                summarizeGeometry: bool|list[str]=False,
                *args):
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
        A list of the input attributes to summarize. The default is False.

    Returns
    -------
    fig : matplotlib figure
        The output matplotlib figure.
    ax : matplotlib axis
        The output matplotlib axis.

    """
    
    geom, defaultObjectConfig = _plotGeomFactory(section, xy0[0], xy0[1])

    if not canvasConfig:
        canvasConfig = CanvasPlotConfig()
        
    if not objectConfig:
        objectConfig = defaultObjectConfig

    plotter = SectionPlotter(geom, canvasConfig)
    fig, ax = plotter.initPlot()
    
    plotter.plot(ax, np.column_stack(geom.getVerticies()), objectConfig)

    
    # if summarizeGeometry:
    #     summaryAttrList = {'Iy':section.Iy, 'Ix':section.Ix}
    #     plotter.plotDesignInfo(fig, ax, summaryAttrList)
    
    
    # Make the plot display.
    ax.plot()

    
    return fig, ax






# class PlotDisplayConfig:
#     c = 
    

def plotElementSection(element:BeamColumn, 
                       summarizeGeometry: bool|list[str]=False):
    """
    Creates a plot of the section centered at xy0.
    
    The figure propreties can be set by using a custom PlotDisplayProps object.
    
    If the element has a plot section set, that will be used for plotting
    instead of the bas element.

    Parameters
    ----------
    section : SectionAbstract
        The sectin to be plotted.
    xy0 : float, optional
        The x/y point to use for the center of the plot. The default is (0,0).
    dispProps : PlotDisplayProps, optional
        The display propreties to use. The default is None.
    summarizeGeometry : bool|list[str], optional
        If false, dispalys nothing.    
        If true, tries to find a default proprety list defined in the 
        element.displayProps
        If a list, creates a summary of the given attributes. 
        The default is False.

    Returns
    -------
    fig : matplotlib figure
        The output matplotlib figure.
    ax : matplotlib axis
        The output matplotlib axis.

    """
    
    dispProps = element.displayProps
    
    # Use the display section if it is set.
    if dispProps.section:
        section = dispProps.section
    else:
        section = element.section
    
    # Plot the section
    fig, ax = plotSection(section, dispProps = dispProps)
    
    if hasattr(element.designProps, 'sectionFire'):
        pass
    
    #     geom, defaultDispProps = _plotGeomFactory(section, xy0[0], xy0[1])

    # plotter = SectionPlotter(geom, dispProps)
    # fig, ax = plotter.initPlot()
    # ax = plotter.plot(ax)
    # ax.plot()
    
    
    fig, ax = plotSection(section, dispProps = dispProps)
    
    
    
    
    return fig, ax
    # if hasattr(obj, name)
    
    # geom, defaultDispProps = _plotGeomFactory(section, xy0[0], xy0[1])

    # if not dispProps:
    #     dispProps = defaultDispProps    

    # plotter = SectionPlotter(geom, dispProps)
    # fig, ax = plotter.plot()
    
    # if summarizeGeometry:
    #     summaryAttrList = {'Iy':section.Iy, 'Ix':section.Ix}
    #     plotter.plotDesignInfo(fig, ax, summaryAttrList)
    
    # return fig, ax

