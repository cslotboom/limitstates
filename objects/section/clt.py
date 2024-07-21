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
    lUnit = 'mm'

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
        return f"<limitstates CLT layer {self.t}{self.lUnit} {self.mat.name}.>"
    
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
    
    def getEI(self, parallelToStrong:bool = True, 
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
        
        EI = 0
        lMid = self._getLayerMidpointsRelative(parallelToStrong)
        for ii, layer in enumerate(self.layers):
            E = layer.getLayerE(parallelToStrong)
            EI += layer.t**3 * E / 12
            EI += layer.t * lMid[ii]**2  * E
        
        sfactor = self.sConvert(sunits)
        lfactor = self.lConvert(lunits)
        return EI * sfactor * lfactor**3
    
    def getGA(self, parallelToStrong:bool = True, NlayerNet:int = None,
              lunits:str = 'm', sunits:str = 'Pa'):
        """
        Gets GA for the layer group in the given globabl orientation.

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
            GA for the section in the input units.

        """
        
        layers = self.layers
        Nlayer = len(layers)
        
        if not NlayerNet:
            NlayerNet = Nlayer
        
        denom = 0
        h = 0
        
        # Get the first terms of the denominator.
        G0 = layers[0].getLayerG(parallelToStrong)
        t0 = layers[0].t/2
        denom += t0/G0 
        h += t0
        
        # account for the final layer if it's present.
        if NlayerNet == Nlayer:
            GN = layers[NlayerNet-1].getLayerG(parallelToStrong)
            tN = layers[NlayerNet-1].t/2
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
        lMid = self._getLayerMidpointsRelative(parallelToStrong)
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

    sLayers:LayerGroupClt
    wLayers:LayerGroupClt
    def __init__(self, layers:LayerGroupClt, lUnit = 'mm'):
        """
        Represents a layered CLT object. Layers can have strong axis direction
        and weak axis direction.

        Assumes that the input layer group has the same units as the section.


        Parameters
        ----------
        layers : list[LayerClt]
            DESCRIPTION.
        w : float, optional
            DESCRIPTION. The default is 1000.
        lUnit : TYPE, optional
            DESCRIPTION. The default is 'mm'.

        Returns
        -------
        None.

        """
        
        self.sLayers = LayerGroupClt(getActiveLayers(layers,True))
        self.wLayers = LayerGroupClt(getActiveLayers(layers,False))
        
        self.lUnit = lUnit
    
    def getEAs(self, sunit='Pa', lunit='m'):
        raise NotImplementedError('EA has not been defined yet')
    
    def getEAw(self, sunit='Pa', lunit='m'):
        raise NotImplementedError('EA has not been defined yet')
    
    def getEIs(self, sunit='Pa', lunit='m'):
        return self.sLayers.getEI(True, sunit, lunit)
    
    def getEIw(self, sunit='Pa', lunit='m'):
        return self.wLayers.getEI(False, sunit, lunit)
    
    def getGAs(self, sunit='Pa', lunit='m'):
        return self.sLayers.getGA(True, sunit, lunit)
    
    def getGAw(self, sunit='Pa', lunit='m'):
        return self.sLayers.getGA(False, sunit, lunit)

