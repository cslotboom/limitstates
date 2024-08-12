"""
Classes that are used to represent CLT sections.


"""

from .section import SectionAbstract
from ..material import MaterialElastic
from ... units import ConverterStress, ConverterDensity, ConverterLength

from dataclasses import dataclass
import numpy as np

from typing import Protocol



class AbstractMaterialTimber(Protocol):
    fb: float
    fb90: float
    fv: float
    fv90: float
    E: float
    E90: float
    G: float
    G90: float

    def getE(self, isStrong:bool):
        pass

    def getG(self, isStrong:bool):
        pass
    
    def sConvert(self):
        pass

@dataclass
class LayerClt:
    t:float
    mat:AbstractMaterialTimber
    ymidfloat = None
    parallelToStrong:bool = True   
    lUnit:str = 'mm'

    def __post_init__(self):
        self._initUnits(self.lUnit)
        
    def _initUnits(self, lUnit):
        """Initiates the length unit used for the layer"""
        self.lUnit = lUnit
        self.lConverter = ConverterLength()   
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        """
        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
            
    def __repr__(self):
        return f"<limitstates CLT layer {self.t}{self.lUnit} {self.mat.lamGrade}.>"
    
    def getLayerE(self, checkInStrong:bool =True):
        """
        Returns the E value depending on the layers orientation, and if the
        layer is being checked in the strong axis or weak axis.
        
        If the layers orientation matches, i.e. the layer is orientated in 
        the weak direction and it's being checked in the weak direction,
        then the parallel elastic modulus is returned. Otherwise, the
        perpendicular to grain elastic modulus is returned.

        Parameters
        ----------
        globalOrientation : bool
            the angle of the global orientation in rad.

        """
        if self._layerMatchesDirection(checkInStrong):
            return self.mat.E
        else:
            return self.mat.E90
    
    def getLayerG(self, checkInStrong:bool =True):
        """
        Returns the G value for a global panel orientation.

        Parameters
        ----------
        globalOrientation : TYPE
            the angle of the global orientation in rad.

        """
        if self._layerMatchesDirection(checkInStrong):
            return self.mat.G
        else:
            return self.mat.G90
        
    def _layerMatchesDirection(self, checkInStrong):
        return checkInStrong == self.parallelToStrong

class LayerGroupClt:
    layers:list[LayerClt]
    ybar:float
    dnet:float
    grade:str
       
    def __init__(self, layers:list[LayerClt]):
        """
        Represents a group of CLT layers, and acts on them to find net section
        propreties.
        The CLT layers are numberd from top layer to bottom layer.

        Parameters
        ----------
        layers : list[LayerClt]
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.layers:list[LayerClt] = layers
        
        self._setLayerBoundaries()
        self._setLayerMidpointsAbs()        
        self.d = self.lBoundaries[-1]
        
        self.lunit = self.layers[0].lUnit
        self.lConvert = self.layers[0].lConvert
        self.sConvert = self.layers[0].mat.sConvert
        self.grade = self.layers[0].mat.grade

    def getLayerAttr(self, attr:str) -> np.ndarray:
        out = []
        for layer in self.layers:
            out.append(getattr(layer, attr))
        return np.array(out)
            
    def __repr__(self):
        return self.layers.__repr__()
    
    def __len__(self):
        return len(self.layers)
    
    def __getitem__(self, ii):
        return self.layers[ii]   
     
    def updateUnits(self, lUnit:str):
        """
        Updates all the layers to have the new unit.
        """
        self.lunit = lUnit
        scaleFactor = self.layers[0].lConvert(lUnit)
        for layer in self.layers:
            layer.lUnit = lUnit
            layer.t = layer.t* scaleFactor
            
        self._setLayerBoundaries()
        self._setLayerMidpointsAbs()        
        self.d = self.lBoundaries[-1]
     
    def _setLayerBoundaries(self):
        y0 = 0
        boundaries = [0]
        for layer in self.layers:
            y0 = y0 + layer.t
            boundaries.append(y0)      
        self.lBoundaries = boundaries
        
    def _setLayerMidpointsAbs(self):
        lMidpointsAbs = []
        for ii in range(len(self.layers)):
            lMidpointsAbs.append(self.lBoundaries[ii+1] - self.layers[ii].t/2)
        self.lMidpointsAbs = lMidpointsAbs
        
    def getYbar(self, checkInStrong:bool =True) -> float:
        EAy = 0
        EA = 0        
        for ii in range(len(self.layers)):
            layer = self.layers[ii]
            E = layer.getLayerE(checkInStrong)
            EAtemp = E * layer.t
            EA += EAtemp
            EAy += EAtemp*self.lMidpointsAbs[ii]
            
        return EAy / EA   
        
    def _getLayerMidpointsRelative(self, parallelToStrong:bool = True):
        lMidpointsRel = []
        
        ybar = self.getYbar(parallelToStrong)
        for ii in range(len(self.layers)):
            lMidpointsRel.append(ybar - self.lMidpointsAbs[ii])
        return lMidpointsRel
        
    def getYmax(self, parallelToStrong:bool = True) -> float:
        ybar = self.getYbar(parallelToStrong)
        r1 = abs(ybar  - self.lBoundaries[0])
        r2 = abs(ybar  - self.lBoundaries[-1]) 
        return max(r1, r2)
    
    def getEI(self, parallelToStrong:bool = True, sunits:str = 'Pa', 
              lunits:str = 'm'):
        """
        Gets EI for the layer group in the given global orientation.
        returns per unit, not net.

        Parameters
        ----------
        globalOrientation : float
            The orientation of the global direction to get EI in.
        lunits : str, optional
            The length units for EI. The default is 'm'.
        sunits : str, optional
            The stress units for EI. The default is 'Pa'.

        Returns
        -------
        float
            EI for the section.

        """
        
        EI = 0
        lMid = self._getLayerMidpointsRelative(parallelToStrong)
        for ii, layer in enumerate(self.layers):
            E = layer.getLayerE(parallelToStrong)
            EI += layer.t**3 * E / 12
            EI += layer.t * lMid[ii]**2  * E
        
        sfactor = self.sConvert(sunits)
        lfactor = self.lConvert(lunits)
        return EI * sfactor * lfactor**3
    
    def getGA(self, parallelToStrong:bool = True, NlayerTotal:int = None,
              lunits:str = 'm', sunits:str = 'Pa'):
        """
        Gets GA for the layer group orientation.

        Parameters
        ----------
        parallelToStrong : bool
            A flag that si set to true if we are looking in the strong axis.
        lunits : str, optional
            The length units for EI. The default is 'm'.
        sunits : str, optional
            The stress units for EI. The default is 'Pa'.

        Returns
        -------
        float
            GA for the section in the input units.

        """
        
        layers = self.layers
        Nlayer = len(layers)
        
        if not NlayerTotal:
            NlayerTotal = Nlayer
        
        denom = 0
        h = 0
        
        # Get the first terms of the denominator.
        G0 = layers[0].getLayerG(parallelToStrong)
        t0 = layers[0].t/2
        denom += t0/G0 
        h += t0
        
        # account for the final layer if it's present.
        if NlayerTotal == Nlayer:
            GN = layers[NlayerTotal-1].getLayerG(parallelToStrong)
            tN = layers[NlayerTotal-1].t/2
            denom += tN/GN
            h += tN
        
        # middle terms.
        for ii in range(1, Nlayer):
            layer = layers[ii]
            G = layer.getLayerG(parallelToStrong)
            denom += layer.t / G
            h += layer.t
        
        GA = h**2 / denom
        
        sfactor = self.sConvert(sunits)
        lfactor = self.lConvert(lunits)
        return GA * sfactor * lfactor

    
    def getEA(self, parallelToStrong:bool = True, 
              lunits:str = 'm', sunits:str = 'Pa'):
        """
        Gets EI for the layer group in the given global orientation.

        Parameters
        ----------
        globalOrientation : float
            The orientation of the global direction to get EI in.
        lunits : str, optional
            The length units for EI. The default is 'm'.
        sunits : str, optional
            The stress units for EI. The default is 'Pa'.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        EA = 0
        # lMid = self._getLayerMidpointsRelative(parallelToStrong)
        for ii, layer in enumerate(self.layers):
            E = layer.getLayerE(parallelToStrong)
            EA += layer.t * E 
        
        sfactor = self.sConvert(sunits)
        lfactor = self.lConvert(lunits)
        return EA * sfactor * lfactor
    
    
    
# =============================================================================
# 
# =============================================================================

class SectionLayered(SectionAbstract):
    """
    Represents a layered section, for example CLT.
    """
    
    def getEA(sunit='sunit', lunit='Pa'):
        pass    
    
    def getEIx(sunit='sunit', lunit='Pa'):
        pass
    
    def getEIy(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAx(sunit='sunit', lunit='Pa'):
        pass
    
    def getGAy(sunit='sunit', lunit='Pa'):
        pass



def _isPerpendicular(searchInStrong, layer):
    return searchInStrong != layer.parallelToStrong

def getActiveLayers(LayerGroupClt:LayerGroupClt, searchInStrong=True) -> LayerGroupClt:
    """
    
    A function that can be used to determine the "active" layers of CLT.
    Layers perpendicular to the direction of interest are neglected if they are
    on the outside of the CLT layer group.

    Parameters
    ----------
    LayerGroupClt : LayerGroupClt
        The input layer group to check.
    searchInStrong : bool, optional
        A flag that can be used to get active layers in either the strong or 
        weak direction are polling in the strong or
        weak axis directions.
    Returns
    -------
    LayerGroupClt
        DESCRIPTION.

    """
    
    #remove all empty layers, this is applicable in the case of a fire section.
    layers = [layer for layer in LayerGroupClt.layers if layer.t !=0]    
    Nlayers = len(layers)
        
    # Ignore all top layers that aren't parallel
    ii = 0
    while _isPerpendicular(searchInStrong, layers[ii]):
        ii += 1
        # Stop iterating when no layers are left.
        if ii == Nlayers:
            break

    # Ignore all bottom layers that aren't parallel
    jj = -1
    while _isPerpendicular(searchInStrong, layers[jj]):
        if jj == -Nlayers:
            break   
        jj -= 1  
        
    if jj == -1:
        return layers[ii:] 
    else:
        return layers[ii:(jj+1)]
    

class SectionCLT(SectionLayered):
    """
    Represents a layered CLT object. Layers can have strong axis direction
    and weak axis direction.
    CLT sections have two effective layer groups in each direction.
    
    If the user is representing a section that is reduced from the original 
    section dimensions, as is the case, then NlayersTotal needs to be set to
    the original number of layers the section has.
    
    Units of the CLT sectionare the same as the untis for the the layers used.

    If the length unit, lUnit is set be differnt than default, then the
    units of the layers will be updates as well.

    Parameters
    ----------
    layers : list[LayerClt]
        The group of CLT layers to use for the section.
    w : float, optional
        The width of the section to use for design propreties. 
        The default is a unit width, or 1000.
    wWeak : float, optional
        The width of the section to use for it's weak axis design 
        propreties. The default is to use the same width as the strong axis.
    lUnit : string, optional
        The width units to use for the section. The using 'default' sets units 
        to the same as the layer group. If another unit is specified, then 
        the units for each layer is converted to this new unit. 
    NlayerTotal : int, optional
        The total number of layers in the original section, pre-fire.
        GA is dependant on not just the layers that are active, but 
        the total number of layers in the CLT.
        
    Returns
    -------
    None.

    """
    sLayers:LayerGroupClt
    wLayers:LayerGroupClt
    def __init__(self, layers:LayerGroupClt, w:float = 1000, wWeak:float = None,
                 lUnit = 'default', NlayerTotal = None):

        # set the weak axis width equal to w if it's not set.
        if not wWeak:
            wWeak = w
        
        # use the same units as the layers if not set.
        if lUnit == 'default':
            self.lUnit = layers[0].lUnit
            self._initUnits(layers[0].lUnit)
        else:
            self.lUnit = lUnit
            self._initUnits(lUnit)
            # If the layers don't match, update them.
            if layers[0].lUnit != lUnit:
                layers.updateUnits(lUnit)
                
        self.w = w / self.lConvert('mm')
        self.wWeak = wWeak / self.lConvert('mm')
        
        if not NlayerTotal:
            NlayerTotal = len(layers)
        self.NlayerTotal = NlayerTotal
            
        self.sLayers = LayerGroupClt(getActiveLayers(layers,True))
        self.wLayers = LayerGroupClt(getActiveLayers(layers,False))
    
    def _initUnits(self, lUnit):
        """Initiates the length unit used for the layer"""
        self.lUnit = lUnit
        self.lConverter = ConverterLength()
    
    @property
    def name(self):
        return f'{self.sLayers.grade} {int(self.sLayers.d)}'
    
    def __repr__(self):
        return f'<limitstates CLT {self.name} Section>'
        
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        """
        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
    def _convertUnits(self, lUnit):
        """Initiates the length unit used for the layer"""
        self.lUnit = lUnit
        factor = self.lConvert('mm')
        self.w = self.w / factor
        self.wWeak = self.wWeak / factor
        self.sLayers.updateUnits(lUnit)
        self.wLayers.updateUnits(lUnit)
    
    def getEAs(self, sunit='Pa', lunit='m'):
        raise NotImplementedError('EA has not been defined yet')
    
    def getEAw(self, sunit='Pa', lunit='m'):
        raise NotImplementedError('EA has not been defined yet')
    
    def getEIs(self, sunit='Pa', lunit='m'):
        """
        Gets EI in units of sunit * lunit ^ 4
        """
        lconvertWidth = self.w*self.lConvert(lunit)
        return self.sLayers.getEI(True, sunit, lunit)*lconvertWidth
    
    def getEIw(self, sunit='Pa', lunit='m'):
        """
        Gets EI in units of sunit * lunit ^ 4
        """
        lconvertWidth = self.w*self.lConvert(lunit)
        return self.wLayers.getEI(False, sunit, lunit)*lconvertWidth
    
    def getGAs(self, sunit='Pa', lunit='m'):
        lconvertWidth = self.w*self.lConvert(lunit)
        Nlayer = self.NlayerTotal
        return self.sLayers.getGA(True, Nlayer, lunit, sunit)*lconvertWidth
    
    def getGAw(self, sunit='Pa', lunit='m'):
        lconvertWidth = self.w*self.lConvert(lunit)
        Nlayer = self.NlayerTotal
        return self.sLayers.getGA(False, Nlayer, lunit, sunit)*lconvertWidth

