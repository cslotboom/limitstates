"""
Author: CS
Description:
    Common classes for representing rebar and stirrups.

"""

import collections
from abc import ABC
from dataclasses import dataclass
from typing import Iterable, Union
from enum import IntEnum

import numpy as np

from .section import SectionMonolithic
from ..material import MaterialElastic
from ..read import DBConfig, _loadSectionDBDict
from ...units import ConverterLength


__all__ = ['Rebar', 'RebarGroup', 'RebarLayer', 'RebarCollection', 
           'RebarFactory', 'StirrupTypeEnum', 'Stirrup', 'StirrupGroup']

class Rebar(SectionMonolithic):
    def __init__(self, mat: MaterialElastic, name: str, d: float, dnet: float,  
                 A: float, xy: tuple = None, rcurve: float = None, 
                 rhook: float = None, lUnit: str = 'mm'):
        """
        Represents rebar, which is typically placed within a concrete section
        as longditudinal bars or stirrups.

        Parameters
        ----------
        mat : MaterialElastic
            The material to use for the rebar.
        name : str
            The name of the bar used for the rebar, i.e. 15M.
        d : float
            The nominal diameter of the rebar.
        dnet : float
            The net diameter of the reabar.
        A : float
            The area of the rebar.
        xy : tuple, optional
            The position of the rebar within it's section. The default is None.
        rcurve : float, optional
            The radius of the rebar curve. The default is None.
        rhook : float, optional
            The radius of the rebar hook curve. The default is None.
        lUnit : str, optional
            The units the rebar uses. The default is 'mm'.

        Returns
        -------
        None.

        """
        self.mat = mat
        self.name = name
        self.A = A
        self.d = d
        self.dnet = dnet
        self.xy = xy
        self.rcurve = rcurve
        self.rhook  = rhook
        self.lenght:float = None
        
        self._initUnits(lUnit)

    def __repr__(self):
        return f"<limitstates Rebar Group with: {len(self)} bars>" 

    def setxy(self, xy:tuple):
        self.xy = xy
        
    def getA(self, lUnit:str = 'mm'):
        """
        Used to return the area of the rebar in the input set of units.

        Parameters
        ----------
        lUnit : str, optional
            The units the rebar uses. The default is 'mm'.

        Returns
        -------
        float
            The rebar area.

        """
        lfactor = self.lConvert(lUnit)
        return self.A * lfactor**2

    def getd(self, lUnit:str = 'mm'):
        """
        Used to return the diameter of the rebar in the input set of units.

        Parameters
        ----------
        lUnit : str, optional
            The units the rebar uses. The default is 'mm'.

        Returns
        -------
        float
            The rebar diameter.

        """
        lfactor = self.lConvert(lUnit)
        return self.d * lfactor

    def convertUnits(self, lUnit:str):
        """
        Converts the rebar length units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            The units to convert the section to.

        """
        # Do nothing is no there is no change.
        if self.lUnit == lUnit:
            return None
        
        cfactor = self.lConvert(lUnit)
        self.lUnit = lUnit
        self.A = self.A*cfactor**2
        self.d = self.d*cfactor
        self.dnet = self.dnet*cfactor
        self.xy = (self.xy[0]*cfactor, self.xy[1]*cfactor)
        
    def setMat(self, mat: MaterialElastic):
        self.mat = mat
        
    def _getRepString(self):
        return f'{self.name} Rebar'
    
    def __repr__(self):
        return f'<limitstates {self._getRepString()}>'
        
class RebarGroup(collections.UserList):
    def __init__(self, iterable: Iterable[Rebar], ID: str = None):
        """
        A rebar group is a list of rebar, which can have an ID, and has methods
        for returning rebar propreties as a collection.

        Parameters
        ----------
        iterable : Iterable
            A iterable of rebar.
        ID : str, optional
            An optional ID for the rebar group. The default is None.


        """
        super().__init__(item for item in iterable)
        self.ID = ID
        self.Nbars = len(self)

    def __repr__(self):
        return f"<limitstates rebar group with {self.Nbars} bars.>"
        
    @property
    def mat(self):
        return self[0].mat
    
    @property
    def coords(self):
        return self.getAttr('coords')
    
    def listAttrs(self) -> list:
        """
        Returns list all possible attributes of the rebar could have.

        Returns
        -------
        float
            A list of all possible attributes.

        """

        return self[0].__dict__.keys()
    
    def getAttr(self, attribute: str) -> np.ndarray:              
        """
        Returns an array of the specific input attribute for every bar within
        the rebar group.

        Parameters
        ----------
        attribute : str
            The attribute to get from each rebar.

        Returns
        -------
        float
            A list of the input rebar for each item in the group.

        """     
        attrs = []
        for bar in self:
            attrs.append(bar.__dict__[attribute])
        return np.array(attrs)    
    
    def getCoords(self, lUnit: str = 'mm') -> np.ndarray:
        """
        Returns an array of the rebar coordinants for each rebar in the group.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        np.ndarray
            The output xy coordinates.

        """
        lfactor = self[0].lConvert(lUnit)
        return self.getAttr('xy') * lfactor
    
    
    def getyCoords(self, lUnit: str = 'mm') -> np.ndarray:
        """
        Returns an array of the rebar y coordinants for each rebar in the group.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        np.ndarray
            The output y coordinates.

        """
        return self.getCoords(lUnit)[:,1]
        
    def getxCoords(self, lUnit: str = 'mm') -> np.ndarray:
        """
        Returns an array of the rebar x coordinants for each rebar in the group.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        np.ndarray
            The output x coordinates.

        """
        return self.getCoords(lUnit)[:,0]
    
    def getyAvg(self, lUnit: str = 'mm') -> float:
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        float
            The average depth of the rebar within the group in the y direction.

        """

        return np.average(self.getyCoords(lUnit))


    def getxAvg(self, lUnit: str = 'mm') -> float:
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.


        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
            
        Returns
        -------
        float
            The average depth of the rebar within the group in the x direction.

        """
        return np.average(self.getxCoords(lUnit))
        
    def getNetArea(self, lUnit:str = 'mm') -> float:
        """
        Calcualtes the total area of the rebar group in the specified units.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
            
        Returns
        -------
        float
            The total area of rebar within the group.

        """
        
        
        lfactor = self[0].lConvert(lUnit)        
        return np.sum(self.getAttr('A')) * lfactor**2
            
    def getAreas(self, lUnit:str = 'mm') -> np.ndarray:
        """
        Returns the total area for each bar within the group.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
            
        Returns
        -------
        float
            The total area of rebar within the group.

        """
        
        lfactor = self[0].lConvert(lUnit)        
        return self.getAttr('A') * lfactor**2
    
    
    def convertUnits(self, lUnit:str):
        """
        Converts the section units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        for bar in self:
            bar.convertUnits(lUnit)

class RebarLayer(RebarGroup):
    """
    A represents a group of rebar that is specifically placed in a layer, 
    i.e., all of the bars share either a x or y coordinate.
    The group is a list of rebar, which can have an ID, and has methods
    for returning rebar propreties as a collection.

    Parameters
    ----------
    iterable : Iterable
        A iterable of rebar.
    ID : str, optional
        An optional ID for the rebar group. The default is None.


    """
    
    _orientationSet = False
    def _setOrientation(self):
        bar1 = self[0]
        bar2 = self[1]
        
        if bar1.xy[0] == bar2.xy[0]:
            self.xOrientation = True
            self._o = 'y'
            self.layerHeight = bar1.xy[0]
        else:
            self.xOrientation = False
            self._o = 'x'
            self.layerHeight = bar1.xy[1]    
        self._orientationSet = True
        
    def __repr__(self):
        # The orientation may not get set if the user initalizes an empty 
        # Rebar layer. If so, then return the str of the super class.
        if not self._orientationSet:
            try:
                self._setOrientation()
            except:
                return str(super())        
        return f"<limitstates rebar layer: {len(self)} bars at {self._o} = {self.layerHeight}>" 


    def getyAvg(self, lUnit: str = 'mm'):
        """
        Calcualtes the effective depth of a rebar group in the y direction,
        which is the average position of the rebar.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        float
            The average depth of the rebar within the group in the y direction.

        """
        
        bar = self[0]
        lfactor = bar.lConvert(lUnit)     
        
        return bar.xy[1] * lfactor

    def getxAvg(self, lUnit: str = 'mm'):
        """
        Calcualtes the effective depth of a rebar group in the y direction,
        which is the average position of the rebar.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        float
            The average depth of the rebar within the group in the y direction.

        """
        
        bar = self[0]
        lfactor = bar.lConvert(lUnit)     
        return bar.xy[0] * lfactor

class RebarCollection:
    
    def __init__(self, groups:list[RebarGroup]):
        """
        A rebar collection is a group of rebar groups. It can be used to 
        easily delineate between different layers of bars, or top / bottom 
        bars.

        Parameters
        ----------
        groups : list[RebarGroup]
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.groups = groups
        self._updateSelfOnBarChange()
        # self.Nbars = sum([len(group) for group in self.groups])
    
    def addBars(self, groups:list[RebarGroup]):
        """
        Adds a group of rebar to the collection.

        Parameters
        ----------
        groups : list[RebarGroup]
            A input list of rebar groups..

        """
        if not self.groups:
            self.groups = groups
        else:
            self.groups += groups
        self._updateSelfOnBarChange()

    def removeGroups(self, inds: Union[int, list[int]]):
        """
        Removes the groups at the input indicies from the collection.


        Parameters
        ----------
        inds : Union[int, list[int]]
            The index / indicies of rebar groups to remove..

        Returns
        -------
        None.

        """

        if isinstance(inds, int):
            inds = [inds]
        newGroups = []
        for ii, group in enumerate(self.groups):
            if ii in inds:
                continue
            newGroups.append(group)
        
        self.groups = newGroups
        self._updateSelfOnBarChange()
    
    def _updateSelfOnBarChange(self):
        self.Nbars = sum([len(group) for group in self.groups])

        
    def getBarByID(self, ID:str) -> RebarGroup|None:
        """
        Returns a rebar group by a given ID from the collection.

        Parameters
        ----------
        ID : str
            The ID used to match the input rebar.

        Returns
        -------
        group : RebarGroup
            The rebar group that that matches the input ID.

        """
        
        for group in self.groups:
            if ID ==  group.ID:
                return group
        else:
            return None
                
        
    def __len__(self):
        return len(self.groups)
    
    @property
    def mat(self):
        return self.groups[0].mat
    
    @property
    def coords(self):
        coordsTmp = []
        for group in self.groups:
            coordsTmp.append(group.getAttr('xy'))
        return coordsTmp
        # return np.array(coordsTmp)
    
    @property
    def coordsFlat(self):
        return np.concatenate(self.coords)
        
    def listAttrs(self) -> list:
        """
        Returns list all possible attributes of the rebar could have.

        Returns
        -------
        float
            A list of all possible attributes.

        """
        return list(self.group[0].listAttrs())
        
    def getAttr(self, attribute:str, flatten:bool=False) -> list[np.ndarray]:
        """
        For each rebar group, returns an array of the values of the input 
        attribute. If flatten is specified, a single array is returned the data
        from all groups combined.

        Parameters
        ----------
        attribute : str
            the attribute.
        flatten : boolean, optional
            A flag that specifies if the data should be flattened. 
            The default is False.

        Returns
        -------
        attrs : list[np.ndarray]
            A list of arrays for each rebar, or a list with a single array for
            all groups if flatten is true.

        """
 
        attrs = []
        if flatten:
            for group in self.groups:
                attrs += list(group.getAttr(attribute))            
        else:
            for group in self.groups:
                attrs.append(group.getAttr(attribute))

        return attrs  
    
    def getCoords(self, lUnit = 'mm', flatten=False) -> np.ndarray:
        """
        For each rebar group, returns an array of the values of the coordinates 
        If flatten is specified, a single array is returned the data
        from all groups combined.
    
        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
        flatten : boolean, optional
            A flag that specifies if the data should be flattened. 
            The default is False.
    
        Returns
        -------
        attrs : list[np.ndarray]
            The coordinates of each rebar, either grouped by rebar group, or
            as a single flat array if flatten is true.
    
        """
        coords = []        
        for group in self.groups:
            coords.append(group.getCoords(lUnit))
        
        if flatten:
            return np.concatenate(coords)
        else:
            return np.array(coords)
            
    
    def _getDirCoords(self, ind,  lUnit = 'mm', flatten=False):
        """ Returns an array of the rebar coordinants. """
        if flatten:
            return self.getCoords(lUnit, flatten)[:,ind]
        else:
            return self.getCoords(lUnit, flatten)[:,:,ind]
    
    def getyCoords(self,  lUnit = 'mm', flatten=False) -> np.ndarray:
        """
        For each rebar group, returns an array of the y coordinates 
        If flatten is specified, a single array is returned the data
        from all groups combined.
    
        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
        flatten : boolean, optional
            A flag that specifies if the data should be flattened. 
            The default is False.
    
        Returns
        -------
        attrs : list[np.ndarray]
            The coordinates of each rebar, either grouped by rebar group, or
            as a single flat array if flatten is true.
    
        """
        return self._getDirCoords(1, lUnit, flatten)
        
    def getxCoords(self, lUnit = 'mm', flatten=False) -> np.ndarray:
        """
        For each rebar group, returns an array of the x coordinates 
        If flatten is specified, a single array is returned the data
        from all groups combined.
    
        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
        flatten : boolean, optional
            A flag that specifies if the data should be flattened. 
            The default is False.
    
        Returns
        -------
        attrs : list[np.ndarray]
            The coordinates of each rebar, either grouped by rebar group, or
            as a single flat array if flatten is true.
    
        """
        return self._getDirCoords(0, lUnit, flatten)

    def getyAvg(self, lUnit: str = 'mm') -> float:
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        float
            The average depth of the rebar within the group in the y direction.

        """
        
        dA = 0
        A = 0
        for group in self.groups:
            Atemp = group.getNetArea(lUnit)
            dA += group.getyAvg(lUnit) * Atemp
            A  += Atemp
        return dA / A
    
    def getxAvg(self, lUnit: str = 'mm') -> float:
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.

        Returns
        -------
        float
            The average depth of the rebar within the group in the x direction.

        """
        
        dA = 0
        A = 0
        for group in self.groups:
            Atemp = group.getNetArea(lUnit)
            dA += group.getxAvg(lUnit) * Atemp
            A  += Atemp
        return dA / A  
    
    def getAreas(self, lUnit = 'mm', flatten = False) -> np.ndarray:
        """
        Returns the total area for each bar within the collection.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
        flatten : boolean, optional
            A flag that specifies if the data should be flattened. 
            The default is False.
            
        Returns
        -------
        float
            The total area of rebar within the group.

        """
        areas = []
        for group in self.groups:
            areas.append(group.getAreas(lUnit))
        
        if flatten:
            return np.concatenate(areas)
        else:
            return areas
        
    def getNetArea(self, lUnit = 'mm') -> float:
        """
        Calcualtes the total area of the rebar collection in the specified units.

        Parameters
        ----------
        lUnit : str, optional
            The units to output coordinates in. The default is 'mm'.
            
        Returns
        -------
        float
            The total area of rebar within the group.

        """
        areaGroups = self.getAreas(lUnit)
        area = 0
        for aGroup in areaGroups:
            area += sum(aGroup)
        return area

class RebarFactory:
    """
    The rebar factory can be used to create rebar objects, based on some 
    database. Given the input databae file

    Parameters
    ----------
    mat : MaterialElastic
        The material that the produced rebar will use.
    dbConfig : DBConfig
        The database configuration object, which defines which database
        to use.
    lUnit : str
        The units to interpret the database with.

    Returns
    -------
    None.

    """
    
    def __init__(self, mat: MaterialElastic, dbConfig: DBConfig, lUnit: str):

        self.mat = mat
        self._loadDB(dbConfig)
        self._initUnits(lUnit)
        
        self.dbcFactor = 1
        
    def _initUnits(self, lUnit: str = None):
        """
        Initiates units of the cross sections. Cross sections have length units
        only.

        Parameters
        ----------
        lUnit : str, optional
            The length unit to use. The default is 'mm'.
        """
        if not lUnit:
            lUnit = 'mm'
        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit: str):
        """
        Get the conversion factor from the current unit to the output unit
        for lengths.
        
        Parameters
        ----------
        outputUnit : str
            The unit to get the conversion factor to.

        Returns
        -------
        float
            The conversion factor between the current length unit and the
            target output length unit.

        """

        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
        
    def _loadDB(self, config: DBConfig):
            
        matdb = _loadSectionDBDict(config)   
        tmpDict = matdb.to_dict(orient='index')
        self.dbDict = {tmpDict[key]['name']:tmpDict[key] for key in tmpDict}
        self.barTypes = [tmpDict[key]['name'] for key in tmpDict]

    def getRebar(self, barType: str, xy: tuple = None, 
                 lUnit: str = None) -> Rebar:
        """
        Gets a rebar of the input bar type, with propreties from the rebar
        database.
        Units in the database will be overwritten by the specified unit if 
        they are different.

        Parameters
        ----------
        barType : str
            The bar type to create.
        xy : tuple, optional
            The location of the rebar from the bottom left point in the secton. 
            The default is None.
        lUnit : str, optional
            The output units desired for the rebar. The default is None.
            Units in the database will be overwritten by the specified unit
            if they are different.


        Returns
        -------
        Rebar
            An output rebar object.

        """
        
        try:
            barParams = self.dbDict[barType]
        except:
            raise Exception(f'{barType} not found in database')
        
        cFactor = self.dbcFactor
        if lUnit and self.lUnit != lUnit:
            cFactor *= self.lConverter.getConversionFactor(self.lUnit, lUnit)
            
        rebar = Rebar(self.mat, 
                        barParams['name'], 
                        barParams['d'] * cFactor, 
                        barParams['dnet'] * cFactor, 
                        barParams['A'] * cFactor**2,
                        rcurve = barParams['rcurve'] * cFactor,
                        lUnit = self.lUnit)
     
        if xy:
            rebar.setxy(xy)
        return rebar
        
    def setMaterial(self, mat:MaterialElastic):
        self.mat = mat
        
    def setLunit(self, lUnit):
        self.dbcFactor = self.lConverter.getConversionFactor(self.lUnit, lUnit)
        self.lUnit = lUnit


class StirrupTypeEnum(IntEnum):
    """
    An enumeration that represents stirrup types. Closed stirrups will have at 
    least two legs, open stirrups will have only one.
    """
    Open = 1
    Closed = 2
       

class StirrupPosition:
    """
    A class representing the position of the stirrup.
    """
    xy0: tuple[float, float] = None
    xy: tuple[list, list] = None
        
    
@dataclass
class StirrupPositionLine(StirrupPosition):
    """
    Represents the position of a open stirrup using a line.
    """
    h: float
    yDir: bool
    xy0: tuple[float, float] = None
    xy: tuple[list, list] = None

    def setPosition():
        pass

@dataclass
class StirrupPositionBox(StirrupPosition):
    """
    Represents the position of a closed stirrup using a box.
    """
    h:float
    b:float
    xy0: tuple[float, float]
    xy: tuple[list, list] = None

    
    def setPosition():
        pass
    
    
def stirrupPositionFactory(stirrupType: StirrupTypeEnum):
    if stirrupType == 1:
        return StirrupPositionLine
    else:
        return StirrupPositionBox
            

class Stirrup:
    def __init__(self, rebar: Rebar, 
                 stirrupType: StirrupTypeEnum = 2,
                 Nleg: int = 2,
                 spacing:float = 200, 
                 position: StirrupPosition = None, 
                 lUnit: str = 'mm'):
        """
        Representa a stirrup.  If a length unit is provided, the rebar length 
        units will be overwritten.
        
        Rebar is fully contained by the position variable.

        Parameters
        ----------
        rebar : Rebar
            The rebar to be used for the stirrup.
        stirrupType : StirrupTypeEnum
            An ennumeration that specifies the type fo stirrup used..
        Nleg : int
            The number of legs the stirrup has in the direction of interst, 
            typically 2 or 1.
        spacing : float, optional
            The spacing for the stirrup along the section. The default is 200.
        position : StirrupPosition, optional
            A object that represents the stirrup position, depending on the
            stirrup type given. Closed stirrups are represented by a box, while
            open stirrups are represented with a line. The default is None.
        lUnit : str, optional
            The length units for the stirrup. The default is 'mm'.

        Returns
        -------
        None.

        """
        
        self.rebar = rebar
        self.rebar.xy = None
        self.rebar.convertUnits(lUnit)

        self.stirrupType = stirrupType
        self.Nleg = Nleg
        self.spacing = spacing
               
        self._initUnits(lUnit)
        
        self.position = position
    
    def _initUnits(self, lUnit: str = 'mm'):
        """
        Initiates units of the cross sections. Cross sections have length units
        only.

        Parameters
        ----------
        lUnit : str, optional
            The length unit to use. The default is 'mm'.
        """

        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit: str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        
        Parameters
        ----------
        outputUnit : str
            The unit to get the conversion factor to.

        Returns
        -------
        float
            The conversion factor between the current length unit and the
            target output length unit.

        """

        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
    
    @property
    def A(self):
        return self.rebar.A   
        
    @property
    def d(self):
        return self.rebar.d
    
    #TODO: test
    def convertUnits(self, lUnit: str):
        """
        Converts the rebar length units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        if self.lUnit != lUnit:
            cfactor = self.lConvert(lUnit)
            self.xy = ([x*cfactor for x in self.xy[0]], 
                       [y*cfactor for y in self.xy[1]])
            self.spacing = self.spacing * cfactor
        
        self.rebar.convertUnits(lUnit)
        
    def getAv(self, lUnit: str = 'mm'):
        cfactor = self.rebar.lConvert(lUnit)
        return self.rebar.A * self.Nleg * cfactor**2
    
    @property
    def mat(self):
        return self.rebar.mat
        
        
    def _getRepString(self):
        return f'{self.rebar.name} Type {self.stirrupType} Stirrup'
    
    def __repr__(self):
        return f'<limitstates {self._getRepString()}>'
    
    def setPosition(self, position: StirrupPosition):
        self.position = position
          
class StirrupGroup(collections.UserList):
    """
    A rebar group is a list of rebar, which can have an ID, and has methods
    for returning rebar propreties as a collection.
    
    Rebar are assumed to have the same spacing for all bars.

    Parameters
    ----------
    iterable : Iterable
        A iterable of rebar.
    ID : str, optional
        An optional ID for the rebar group. The default is None.

    """
    def __init__(self, iterable: Iterable[Stirrup], ID: str = None):

        self._validateInputs(iterable)
        super().__init__(item for item in iterable)
        self.ID = ID
        self.Nbars = len(self)

    def __repr__(self):
        return f"<limitstates stirrup group with {self.Nbars} stirrups.>"

    def _validateInputs(self, iterable: Iterable[Stirrup]):
        d = iterable[0].d
        s = iterable[0].spacing
        for bar in iterable:
            if bar.d != d:
                raise Exception('All rebar must have the same diameter.')
            if bar.spacing != s:
                raise Exception('All rebar must have the same spacing.')

    def getBarDiameter(self):
        """Returns the bar diameter"""
        return self[0].d
        
    @property
    def mat(self):
        return self[0].mat
    
    @property
    def spacing(self):
        return self[0].spacing
    
    def listAttrs(self):
        """        Lists the rebar attributes.        """
        stirrupAttrs = list(self[0].__dict__.keys())
        rebarAttrs   = list(self[0].reabr.__dict__.keys())
        
        return stirrupAttrs + rebarAttrs
    
    def _getStirrupAttr(self, attribute: str) -> np.ndarray:
        attrs = []  
        for bar in self:
            attrs.append(bar.__dict__[attribute])
        return np.array(attrs)       
    
    def _getRebarAttr(self, attribute: str) -> np.ndarray:
        attrs = []
        for bar in self:
            attrs.append(bar.rebar.__dict__[attribute])
        return np.array(attrs)
    
    def getAttr(self, attribute: str) -> np.ndarray:
        """  Gets outputs from the rebar attributes. """        
        
        if attribute in list(self[0].__dict__.keys()):
            return self._getStirrupAttr(attribute)
        else:
            return self._getRebarAttr(attribute)
            
    def convertUnits(self, lUnit: str):
        """
        Converts the section units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        for bar in self:
            bar.convertUnits(lUnit)
        
    def getCoords(self, lUnit: str = 'mm') -> np.ndarray:
        """
        Returns an array of the rebar coordinants.

        Parameters
        ----------
        lUnit : str, optional
            The units for the outputs. The default is 'mm'.

        Returns
        -------
        list[list[float]]
            The output xy coordinates as a nd.array.

        """
        lfactor = self[0].lConvert(lUnit)
        return self.getAttr('xy') * lfactor
    
    def getAvNet(self, lUnit: str = 'mm') -> float:
        """
        Returns the sum of all Av in the stirrup group.

        Parameters
        ----------
        lUnit : str, optional
            The units for the outputs. The default is 'mm'.

        Returns
        -------
        float
            The summ of all rebar area within the group in the output units.

        """
 
        Anet = 0
        for stirrup in self:
            Anet += stirrup.getAv(lUnit)
        return Anet
    
    def getSpacing(self, lUnit: str = 'mm'):
        """
        Gets the spacing of the rebar in the group. All stirrups are assumed
        to have the same spacing.

        Parameters
        ----------
        lUnit : str, optional
            The units for the outputs. The default is 'mm'.

        Returns
        -------
        float
            The summ of all rebar area within the group in the output units.

        """
        lfactor = self[0].lConvert(lUnit)
        return self[0].spacing * lfactor

