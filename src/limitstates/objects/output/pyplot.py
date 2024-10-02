"""
Manages matplotlib plotting of sections.


Features of a plot:
    - Create a visualization of the section
    - Show a dictionary of common propreties Ix, Sx, Zx, etc.
    - SHow a dictionary of results

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from .. section import SectionAbstract, SectionRectangle, SectionSteel, SteelSectionTypes
from .. element import BeamColumn

from .. display import MATCOLOURS, PlotConfigCanvas, PlotConfigObject
from .model import GeomModel, GeomModelRectangle, GeomModelIbeam, GeomModelIbeamRounded, GeomModelGlulam


class SectionPlotter:
    
    plotOffset = 0.05
    def __init__(self, baseGeom:GeomModel, canvasProps:PlotConfigCanvas):
        
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

    
    def plotInterior(self, ax, xy, objectConfig, *args, **kwargs):
        """
        Plots the interior of an geometry. This could include line hashing
        indicating.
        
        It could also be a series of internal points
        """
        c = objectConfig.c
        # x, y = self.geom.getPlotVerticies()
        ax.fill(xy[:,0], xy[:,1], *args, c = c, **kwargs)
        if objectConfig.showOutline:
            ax.plot(xy[:,0], xy[:,1], linewidth = objectConfig.lineWidth)
        
        return ax
    
    
    def _getPlotLabel(infoDict):
        """
        Converts the in
        
        {'label':value, 'label2':value ...}
        
        label = 
        
        """
        
        label = r'mathbf{Section Summary}$ \n'
        for item in infoDict:
            line = str(item) + ' = ' + str(round(infoDict[item])) + '\n'
            label += line
        return label
    
    # def _plotInformation(infoDict):
    #     """
    #     """
        
    #     label = ''
    #     for item in infoDict:
    #         items = str(item) + ' ' for item in 
    #         label += 
    #     return label
    
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





def _plotGeomFactory(section:SectionAbstract, *args) -> (GeomModel, PlotConfigObject):
    """
    Gets the appropriate geometry and dispalay propreties 

    """
    
    # We could return an enumeration instead of using this factory, and have
    # a 'switch'
    if isinstance(section, SectionRectangle):
        geom = GeomModelRectangle(section.b, section.d, *args)
        defaultProps = PlotConfigObject(c = MATCOLOURS['glulam'])
    
    
    elif isinstance(section, SectionSteel):
        geom = _plotFactorySteel(section, *args)
        defaultProps = PlotConfigObject(c = MATCOLOURS['steel'])
    
    
    else:
        raise Exception(f'Section of type {section} is not supported.')
        
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
                canvasConfig: PlotConfigCanvas = None,
                objectConfig: PlotConfigObject = None,
                summarizeGeometry: bool|list[str]=False,
                *args):
    """
    Creates a plot of the section centered at xy0.
    
    A default set of propreties will be chosen for the section depending on 
    it's type.
    
    Custom propreties can also be given to the canvas and object by passing in
    a canvasConfig object.
    
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
        canvasConfig = PlotConfigCanvas()
        
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

def _getFireSectionPositon(burnDims):
    """
    Figures out how much to offset the fire section by.
    This will depend on the fire condition used.
    
    The if statement logic for this function may be too complex.
    In that case, a seperate way of tracking how much each side is burned
    will be needed.
    """
    dx = (burnDims[3] - burnDims[1]) / 2 
    dy = (burnDims[2] - burnDims[0]) / 2 
    
    return dx, dy
    
def _hasFireSection(dispProps):
    return (hasattr(dispProps, 'sectionFire') and dispProps.sectionFire)

def _isGlulamSection(dispProps):
    return hasattr(dispProps, 'sectionFire')
# If the logic gets too complex here, then we should create a plotting objects
# that have a interface, "plot", and a factory for them.

def _plotFactory(dispProps):
    
    if _isGlulamSection(dispProps):
        return _plotGlulam(dispProps)
    else:
        return _plotBasic(dispProps)


def _plotBasic(dispProps):
    """
    Plots a basic section.
    """
    
    canvasPlotConfig = dispProps.configCanvas
    canvasObjConfig  = dispProps.configObject
            
    geom, _ = _plotGeomFactory(dispProps.section)
    plotter = SectionPlotter(geom, canvasPlotConfig)
    
    fig, ax = plotter.initPlot()
    
    xy = np.column_stack(geom.getVerticies())
    plotter.plot(ax, xy, canvasObjConfig)
    return fig, ax
    

def _plotGlulam(dispProps):
    """
    Plots a glulam section, showing the fire section in the center if it is
    present.
    
    We also show some fill lines for the CLT
    """
    
    canvasPlotConfig = dispProps.configCanvas
    section = dispProps.section

    hasFireSection = _hasFireSection(dispProps)
    
    if hasFireSection:
        canvasObjConfig     = dispProps.configObjectBurnt
    else:            
        canvasObjConfig     = dispProps.configObject
            
    geom    = GeomModelGlulam(section.b, section.d)
    plotter = SectionPlotter(geom, canvasPlotConfig)
    fig, ax = plotter.initPlot()
    
    # Plot the base object
    plotter.plot(ax, np.column_stack(geom.getVerticies()), canvasObjConfig)
    
    if hasFireSection:
        sectionFire  = dispProps.sectionFire
        dx, dy       = _getFireSectionPositon(dispProps.burnDims)
        dh           = dispProps.displayLamHeight
        geom         = GeomModelGlulam(sectionFire.b, sectionFire.d, dh, dx, dy)
        objectConfig = dispProps.configObject
        plotter.plot(ax, np.column_stack(geom.getVerticies()), objectConfig)
    
    linex, liney = geom.getFillVerticies()
    lineVerts = [np.column_stack((x,y)) for x, y in zip(linex, liney)]
    line_collection = LineCollection(lineVerts, colors=dispProps.displayColorLines)
    ax.add_collection(line_collection)
    
    return fig, ax

def _plotCLT():
    pass


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

    dispProps = element.eleDisplayProps
    
    # Use the display section if it is set.
    if not dispProps.section:
        dispProps.section = element.section
    
    return _plotFactory(dispProps)

    # canvasPlotConfig = dispProps.configCanvas

    # hasFireSection = _hasFireSection(dispProps)
    # if hasFireSection:
    #     canvasObjConfig     = dispProps.configObjectBurnt
    # else:            
    #     canvasObjConfig     = dispProps.configObject
            
    # geom, _ = _plotGeomFactory(section)
    # plotter = SectionPlotter(geom, canvasPlotConfig)
    # fig, ax = plotter.initPlot()
    
    # # Plot the base object
    # plotter.plot(ax, np.column_stack(geom.getVerticies()), canvasObjConfig)
    
    # if hasFireSection:
    #     sectionFire = dispProps.sectionFire
    #     dx, dy  = _getFireSectionPositon(section, sectionFire)
    #     geom, _ = _plotGeomFactory(sectionFire, dx, dy)
    #     objectConfig = dispProps.configObject
    #     plotter.plot(ax, np.column_stack(geom.getVerticies()), objectConfig)
        
        
        
        
        
    