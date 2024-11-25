"""
These functions manages matplotlib plotting of sections.
"""
"""
Features of a plot:
    - Create a visualization of the section
    - Show a dictionary of common propreties Ix, Sx, Zx, etc.
    - Show a dictionary of results

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Circle, Polygon

from .. section import SectionAbstract, SectionRectangle, SectionSteel, SteelSectionTypes, SectionCLT
from .. element import BeamColumn
from .. display import MATCOLOURS, PlotConfigCanvas, PlotConfigObject, PlotOriginPosition
# from .model import GeomModel, GeomModelRectangle, GeomModelIbeam, GeomModelIbeamRounded, GeomModelGlulam
import limitstates.objects.output.model as md

import matplotlib.patches as mpatches
import matplotlib.path as mpath


class SectionPlotter:
    
    plotOffset = 0.05
    def __init__(self, baseGeom:md.GeomModel, canvasProps:PlotConfigCanvas):
        
        self.geom = baseGeom
        self.canvasConfig = canvasProps

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
        maxFigsize = self.canvasConfig.maxFigsize
        return dx / dmax * maxFigsize, dy / dmax * maxFigsize
    
    def initPlot(self):
        x, y = self.geom.getVerticies()
        xlims, ylims = self._getPlotLimits(x,y)
        
        xplot, yplot = self._getPlotSize(xlims, ylims)

        # Set the dimensions / aspect ratio of the plot
        fig, ax = plt.subplots(figsize=(xplot, yplot), dpi = self.canvasConfig.dpi)
        
        if self.canvasConfig.showAxis != True:
            ax.axis('off')
        
        # Set the dimensions /     
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        
        return fig, ax  
    
    def _getFillColour(self, objectConfig, kwargs):
        # overwrite teh colour if needed.
        if 'c' in kwargs:
            c = kwargs['c']
            kwargs.pop('c', None)
        else:
            c = objectConfig.c
        return c

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
    
    
    def plot(self, ax, xy, objectConfig, *args, **kwargs):
        """
        plot a set of xy points on the canvas.
        """
        
        c = self._getFillColour(objectConfig, kwargs)        
        objectPatch = Polygon(xy, *args, color = c, **kwargs)
        ax.add_patch(objectPatch)
        
        # Add the border line around the object
        if objectConfig.showOutline and (("linewidth" not in kwargs) or ("lw" not in kwargs)):
            ax.plot(xy[:,0], xy[:,1], 
                    linewidth = objectConfig.lineWidth, 
                    c=objectConfig.cLine)
        
        return ax
    
class SectionPlotterWithHole(SectionPlotter):
    
    def _getPatchWithHole(self, xyOutside, xyInside):
        """
        See https://matplotlib.org/stable/gallery/shapes_and_collections/donut.html
        """
    
        Nverts = len(xyOutside)
        lineCode = mpath.Path.LINETO
        codes = np.ones(Nverts, dtype=mpath.Path.code_type) * lineCode
        codes[0] = mpath.Path.MOVETO
    
        vertices = np.concatenate((xyOutside[::],
                                   xyInside[::-1]))
        
        drawingInstructions = np.concatenate((codes, codes))
        # Create the Path object
        path = mpath.Path(vertices, drawingInstructions)
        
        return path
    
    def plot(self, ax, xy, objectConfig, *args, **kwargs):
        """
        plot a set of xy points on the canvas.
        It's assumed that the inside and outside verticies are passed in with
        one array, xy. This array will '
        """
        
        # We assume that the two arrays have the same size
        xyOut, xyIn = np.split(xy, 2)
        
        c = self._getFillColour(objectConfig, kwargs)        
        path  = self._getPatchWithHole(xyOut, xyIn)
                
        patch = mpatches.PathPatch(path, *args, color = c, **kwargs)

        ax.add_patch(patch)
        
        # Add the border line around the object
        if objectConfig.showOutline and (("linewidth" not in kwargs) or ("lw" not in kwargs)):
            ax.plot(xyOut[:,0], xyOut[:,1], 
                    linewidth = objectConfig.lineWidth, 
                    c=objectConfig.cLine)
            ax.plot(xyIn[:,0], xyIn[:,1], 
                    linewidth = objectConfig.lineWidth, 
                    c=objectConfig.cLine)
        
        return ax

def _getPlotOrigin(option, b, d,  xy0):
    if option == PlotOriginPosition.centered:
        return (0 + xy0[0],   0 + xy0[1])
    elif option == PlotOriginPosition.bottomCenter:
        return (0 + xy0[0], d/2 + xy0[1])
    elif option == PlotOriginPosition.bottomLeft:
        return (b/2 + xy0[0], d/2 + xy0[1])
    
    else:
        raise Exception()



"""
We can combine the following two funcitons by assigning each section a plot
enumeration, i.e. 1 = glulam, 2 = steel, 3 = CLT,
Then checking against that enumeration.
This allow for slightly faster section checking behaviour
"""

def _defaultConfigFactory(section):
    
    
    if isinstance(section, SectionRectangle): # typical section
        defaultProps = PlotConfigObject(c = MATCOLOURS['glulam'], originLocation= 1)
    elif isinstance(section, SectionSteel): # steel section
        defaultProps = PlotConfigObject(c = MATCOLOURS['steel'],  originLocation= 1)
    elif isinstance(section, SectionCLT): # CLT section
        defaultProps = PlotConfigObject(c = MATCOLOURS['clt'], originLocation= 3)
        defaultProps.cFillLines = MATCOLOURS['black']
        defaultProps.cFillPatch = MATCOLOURS['cltWeak']
    else:
        raise Exception(f'Section of type {section} is not supported.')
    return defaultProps

def _plotGeomFactory(section: SectionAbstract, 
                     originLocation: int|PlotOriginPosition,
                     xy0) -> md.GeomModel:
    """
    A function that returns the appropriate geometry object given a section.
    
    A thought - why haven't we made this an object attribute?

    """

    if isinstance(section, SectionRectangle):
        b, d = section.b, section.d
        xy   = _getPlotOrigin(originLocation, b, d, xy0)
        geom = md.GeomModelRectangle(b, d, *xy)
    elif isinstance(section, SectionSteel):
        b, d  = section.bf, section.d        
        xy    = _getPlotOrigin(originLocation, b, d, xy0)
        geom  = _plotFactorySteel(section, *xy)
    elif isinstance(section, SectionCLT):
        b, layers = section.w, section.sLayers
        xy        = _getPlotOrigin(originLocation, b, layers.d, xy0)
        geom      = md.GeomModelClt(layers, b, *xy)
    else:
        raise Exception(f'Section of type {section} is not supported.')
        
    return geom



def _plotterFactory(section: SectionAbstract, 
                    geom: md.GeomModel,
                    canvasConfig: PlotConfigCanvas) -> SectionPlotter:
    """
    A function that returns the appropriate geometry object given a section.
    
    A thought - why haven't we made this an object attribute?

    """

    if isinstance(section, SectionSteel) and (section.typeEnum == SteelSectionTypes.hss):
        return SectionPlotterWithHole(geom, canvasConfig)
    else:
        return SectionPlotter(geom, canvasConfig)
        

def _plotFactorySteel(section:SectionSteel, *args):
    enum = section.typeEnum
    if SteelSectionTypes.w == enum:
        # If there is information about the rounded section, plot that
        if hasattr(section, 'r1') and hasattr(section, 'r2'):
            geom = md.GeomModelIbeamRounded(section.d, 
                                            section.tw, 
                                            section.bf, 
                                            section.tf,  
                                            section.r2,  
                                            section.r1,  
                                            *args)
        # If there is information about the rounded section, plot that
        else:
            geom = md.GeomModelIbeam(section.d, 
                                    section.tw, 
                                    section.bf, 
                                    section.tf,  
                                    *args)
            
    elif SteelSectionTypes.hss == enum:
        ro = section.ro
        ri = section.ri
        
        geom = md.GeomModelHss(section.d, section.bf, section.t, ro, ri, *args)
        
    
    return geom


def _setupSummaryDict(listIn, ):
    pass


def _plotfillLines(ax, geom, objectConfig):
    linex, liney = geom.getFillVerticies()
    lverts = [np.column_stack((x,y)) for x, y in zip(linex, liney)]
    lines = LineCollection(lverts, colors = objectConfig.cFillLines,
                           linewidth = 0.5)
    ax.add_collection(lines)


def _plotfillPatches(ax, geom, objectConfig):
    linex, liney = geom.getFillAreas()
    lverts = [np.column_stack((x,y)) for x, y in zip(linex, liney)]
    
    p = PatchCollection([Polygon(vert) for vert in lverts], color = objectConfig.cFillPatch)
    ax.add_collection(p)


def plotSection(section:SectionAbstract, 
                xy0: list[float,float] = None, 
                canvasConfig: PlotConfigCanvas = None,
                objectConfig: PlotConfigObject = None,
                summarizeGeometry: bool|list[str]=False,
                *args, **kwargs):
    """
    Creates a plot of the section centered at xy0.
    
    A default set of propreties will be chosen for the section depending on 
    it's type. Custom propreties can also be given to the canvas and object by passing in
    a canvasConfig object.
    
    The figure propreties can be set by using a custom PlotDisplayProps object.
    
    Steel sections will be plotted with rounded corners, if information about
    the corner radius exists in r1 / r2.
    
    Where additional arguemts passed to args and kwargs confict with arguments
    passed in the config object, the arg/kwargs will overwrite the config 
    objects.

    Parameters
    ----------
    section : SectionAbstract
        The sectin to be plotted.
    xy0 : float, optional
        The x/y point to use for the orign of the plot. The default is (0,0).
        Note that the object may be plotted at a different location
    dispProps : PlotDisplayProps, optional
        The display propreties to use. The default is None.
    summarizeGeometry : bool|list[str], optional
        XXX does not work currently.
        A list of the input attributes to summarize. The default is False.
    args  
        Additional arguments for matplotolib's ax.fill function
    kwargs  
        Additional arguments for matplotolib's ax.fill function
        

    Returns
    -------
    fig : matplotlib figure
        The output matplotlib figure.
    ax : matplotlib axis
        The output matplotlib axis.

    """
    if not canvasConfig:
        canvasConfig = PlotConfigCanvas()
            
    if not objectConfig:
        objectConfig = _defaultConfigFactory(section)        
    
    # Setup default xy0 plot center
    if xy0 is None:
        xy0 = [0,0]
        
    geom    = _plotGeomFactory(section, objectConfig.originLocation, xy0)
    plotter = _plotterFactory(section, geom, canvasConfig)
    
    fig, ax = plotter.initPlot()
    xyVerts = np.column_stack(geom.getVerticies())
    
    plotter.plot(ax, xyVerts, objectConfig, *args, **kwargs)

    if hasattr(geom, 'getFillVerticies'):
        _plotfillLines(ax, geom, objectConfig)

    if hasattr(geom, 'getFillAreas'):
        _plotfillPatches(ax, geom, objectConfig)

    ax.plot()

    return fig, ax




def _getFireSectionPositonGL(burnDims):
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


def _getFireSectionPositonCLT(burnDims):
    """
    Figures out how much to offset the fire section by.
    This will depend on the fire condition used.
    
    The if statement logic for this function may be too complex.
    In that case, a seperate way of tracking how much each side is burned
    will be needed.
    """
    dx = 0
    # dy = (burnDims[2] - burnDims[0]) / 2
    #TODO: this will need to be updated when we do walls.
    dy = burnDims[0]/2
    
    
    return dx, dy
    


def _hasFireSection(dispProps):
    return (hasattr(dispProps, 'sectionFire') and dispProps.sectionFire)

def _isCLTSection(dispProps):
    return isinstance(dispProps.section, SectionCLT)

def _isGlulamSection(dispProps):
    return hasattr(dispProps, 'sectionFire')



# def _isGlulamSection(dispProps):
#     return hasattr(dispProps, 'sectionFire')


# If the logic gets too complex here, then we should create a plotting objects
# that have a interface, "plot", and a factory for them.

def _plotFactory(dispProps):
    """
    Figures out what type of plot function to use.
    """    
    if _isCLTSection(dispProps):
        return _plotCLT(dispProps)
    if _isGlulamSection(dispProps):
        return _plotGlulam(dispProps)    
    else:
        return _plotBasic(dispProps)


def _plotBasic(dispProps):
    """
    Plots a basic section using the canvas plot configuration and canvas object
    configuration classes.
    """
    
    cPlotConfig = dispProps.configCanvas
    cObjConfig  = dispProps.configObject
    
    geom    = _plotGeomFactory(dispProps.section, cObjConfig.originLocation, [0,0])
    plotter = _plotterFactory(dispProps.section, geom, cPlotConfig)
    
    fig, ax = plotter.initPlot()
    
    xy = np.column_stack(geom.getVerticies())
    plotter.plot(ax, xy, cObjConfig)
    return fig, ax


def _plotGlulam(dispProps):
    """
    Plots a glulam section, showing the fire section in the center if it is
    present.
    
    We also show some fill lines for the 
    """
    
    cPlotConfig = dispProps.configCanvas
    section     = dispProps.section

    hasFireSection = _hasFireSection(dispProps)
    
    if hasFireSection:
        canvasObjConfig     = dispProps.configObjectBurnt
    else:            
        canvasObjConfig     = dispProps.configObject
    
    # Find the offset for the base section
    b, d = section.b, section.d
    dx0, dy0 = _getPlotOrigin(canvasObjConfig.originLocation, b, d, [0,0])

    # Get the geometry and initilziet the plot for the base section
    geom    = md.GeomModelGlulam(b, d, dx0 = dx0, dy0 = dy0)
    plotter = SectionPlotter(geom, cPlotConfig)
    fig, ax = plotter.initPlot()
    
    # Plot the base object
    plotter.plot(ax, np.column_stack(geom.getVerticies()), canvasObjConfig)
    
    # Plot the fire section.
    if hasFireSection:
        sFire  = dispProps.sectionFire
        
        
        
        dx, dy       = _getFireSectionPositonGL(dispProps.burnDimensions)
        dh           = dispProps.displayLamHeight
        geom         = md.GeomModelGlulam(sFire.b, sFire.d, dh, dx + dx0, dy + dy0)
        objectConfig = dispProps.configObject
        plotter.plot(ax, np.column_stack(geom.getVerticies()), objectConfig)
    
    # Plot the internal fill lines
    _plotfillLines(ax, geom, canvasObjConfig)

    
    return fig, ax

def _plotCLT(dispProps):
    
    cPlotConfig = dispProps.configCanvas
    section     = dispProps.section
    
    hasFireSection = _hasFireSection(dispProps)
       
    if hasFireSection:
        canvasObjConfig     = dispProps.configObjectBurnt
    else:            
        canvasObjConfig     = dispProps.configObject
    
        
    b, d = section.w, section.sLayers.d
    dx0, dy0 = _getPlotOrigin(canvasObjConfig.originLocation, b, d, [0,0])    
        
    geom    = md.GeomModelClt(section.sLayers, b, dx0 = dx0, dy0 = dy0)

    plotter = SectionPlotter(geom, cPlotConfig)
    fig, ax = plotter.initPlot()
    
    # Plot the base object
    plotter.plot(ax, np.column_stack(geom.getVerticies()), canvasObjConfig)
    
    if hasFireSection:
        sFire  = dispProps.sectionFire
        # plotLayers = _getPlotLayers(sFire)
        plotLayers = sFire.layers
        dx, dy       = _getFireSectionPositonCLT(dispProps.burnDimensions)
        geom         = md.GeomModelClt(plotLayers, b, dx + dx0, dy + dy0)
        objectConfig = dispProps.configObject
        
        plotter.plot(ax, np.column_stack(geom.getVerticies()), objectConfig)

    _plotfillLines(ax, geom, canvasObjConfig)
    _plotfillPatches(ax, geom, canvasObjConfig)
    
    return fig, ax

def _getPlotLayers(sFire):
    """
    Return the biggest between the strong/weak axis layer group
    """
    layersOut = [layer for layer in sFire.sLayers]
    if len(sFire.sLayers) == len(sFire.wLayers):
        return sFire.wLayers
    else:
        return sFire.sLayers


def plotElementSection(element:BeamColumn, 
                       summarizeGeometry: bool|list[str]=False):
    """
    Creates a plot of the section the element is using. Only applies to 
    elements that have a "eleDisplayProps" set.
    
    The figure propreties can be set by modifying or replacing the element's 
    eleDisplayProps object.
    
    If the element has a plot section set, that will be used for plotting
    instead of the base element.

    Parameters
    ----------
    element : BeamColumn
        The sectin to be plotted.
    summarizeGeometry : bool|list[str], optional
        XXX currently unused XXX
        If false, dispalys nothing.    
        If true, tries to find a default proprety list defined in the 
        element.eleDisplayProps
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

        
        
        
        
        
    
