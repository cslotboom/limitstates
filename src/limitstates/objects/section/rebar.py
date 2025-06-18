"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""

import collections
import numpy as np

from abc import ABC
from .section import SectionMonolithic
from ..material import MaterialElastic
from ..read import DBConfig, _loadSectionDBDict
from ...units import ConverterLength


__all__ = ['Rebar', 'RebarGroup', 'RebarCollection', 'RebarFactory',
           'RebarPlacer']

class Rebar(SectionMonolithic):
    def __init__(self, mat:MaterialElastic, name:str, d:float, dnet:float,  
                 A:float, xy:tuple = None, lUnit = 'mm'):
        self.mat = mat
        self.name = name
        self.A = A
        self.d = d
        self.dnet = dnet
        self.xy = xy
        
        self._initUnits(lUnit)
               
    def _initUnits(self, lUnit):
        """Initiates the length unit used for the layer"""
        self.lUnit = lUnit
        self.lConverter = ConverterLength()   

    
    def setxy(self, xy:tuple):
        self.xy = xy
        
    def getA(self, lUnit:str = ''):
        lfactor = self.lConvert(self._validateLunit(lUnit))
        return self.A * lfactor**2

    def getd(self, lUnit:str = ''):
        lfactor = self.lConvert(self._validateLunit(lUnit))        
        return self.d * lfactor**2

    def convertUnits(self, lUnit:str):
        """
        Converts the rebar length units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        cfactor = self.lConvert(lUnit)
        self.lUnit = lUnit
        self.A = self.A*cfactor
        self.d = self.d*cfactor
        self.dnet = self.dnet*cfactor
        self.xy = (self.xy[0]*cfactor,self.xy[1]*cfactor)

class RebarGroup(collections.UserList):
    
    @property
    def mat(self):
        return self[0].mat
    
    @property
    def coords(self):
        return self.getAttr('coords')
    
    def listAttrs(self):
        """        Lists the rebar attributes.        """
        return self[0].__dict__.keys()
    
    def getAttr(self, attribute):
        """  Gets outputs from the rebar attributes. """        
        attrs = []
        for bar in self:
            attrs.append(bar.__dict__[attribute])
        return np.array(attrs)    
    
    def getCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        lUnit = self[0]._validateLunit(lUnit)
        lfactor = self[0].lConvert(lUnit)
        return self.getAttr('xy') * lfactor
    
    
    def getyCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords(lUnit)[:,1]
        
    def getxCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords(lUnit)[:,0]
    
    def getdeff(self, direction:str = 'y', lUnit:str = ''):
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """

        if direction == 'y':
            return np.average(self.getyCoords(lUnit))
        elif direction == 'x':
            return np.average(self.getxCoords(lUnit))
        
    def getNetArea(self, lUnit = ''):
        lUnit = self[0]._validateLunit(lUnit)
        lfactor = self[0].lConvert(lUnit)        
        return np.sum(self.getAttr('A')) * lfactor**2
            
    def getAreas(self, lUnit = ''):
        lUnit = self[0]._validateLunit(lUnit)
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
    

    def getdeff(self, direction = 'y', lUnit = ''):
        """
        Returns the depth of a rebar layer in the input direction.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """
        
        bar = self[0]
        lUnit = bar._validateLunit(lUnit)
        lfactor = bar.lConvert(lUnit)     
        
        if direction == 'y':
            return bar.xy[1] * lfactor
        elif direction == 'x':
            return bar.xy[0] * lfactor

class RebarCollection:
    
    def __init__(self, groups:list[RebarGroup]):
        self.groups = groups
    
    @property
    def mat(self):
        return self.groups[0].mat
    
    @property
    def coords(self):
        coordsTmp = []
        for group in self.groups:
            coordsTmp.append(group.getAttr('coords'))
        return np.concatenate(coordsTmp)
    
    def listAttrs(self):
        """        Lists the rebar attributes.        """
        return self.group[0].listAttrs()
        
    def getAttr(self, attribute:str):
        """  For each group, return a list of the input attribute. """        
        attrs = []        
        for group in self.groups:
            attrs.getAttr(group.getAttr(attribute))

        return attrs  
    
    def getCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        coords = []        
        for group in self.groups:
            coords.append(group.getCoords(lUnit))
        
        return np.array(coords)
    
    
    def getyCoords(self):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords()[:,1]
        
    def getxCoords(self):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords()[:,0]
    
    def getdeff(self, direction = 'y', lUnit = ''):
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """
        
        dA = 0
        A = 0
        for group in self.groups:
            Atemp = group.getNetArea(lUnit)
            dA += group.getdeff(direction, lUnit) * Atemp
            A  += Atemp
            
        return dA / A
        # if direction == 'y':
        #     return np.average(self.getyCoords())
        # elif direction == 'x':
        #     return np.average(self.getxCoords())
            
    def getAreas(self, lUnit = ''):  
        areas = []
        for group in self.groups:
            areas.append(group.getAreas(lUnit))
            
        return areas

        
    def getNetArea(self, lUnit = ''):
        
        areaGroups = self.getAreas(lUnit)
        areas = []
        for aGroup in areaGroups:
            areas +=aGroup
        return np.sum(areas)

class RebarFactory:
    
    def __init__(self, mat:MaterialElastic, dbConfig:DBConfig, lUnit:str):
        self.mat = mat
        self.lUnit = lUnit
        self._loadDB(dbConfig)
        
    def _loadDB(self, config:DBConfig):
            
        matdb = _loadSectionDBDict(config)   
        tmpDict = matdb.to_dict(orient='index')
        self.dbDict = {tmpDict[key]['name']:tmpDict[key] for key in tmpDict}

    def getRebar(self, barType:str, xy:tuple = None) -> Rebar:
        
        try:
            barParams = self.dbDict[barType]
        except:
            raise Exception(f'{barType} not found in database')
        rebar = Rebar(self.mat, 
                            barParams['name'], 
                            barParams['d'], 
                            barParams['dnet'], 
                            barParams['A'],
                            self.lUnit)
     
        if xy:
            rebar.setxy(xy)
        return rebar
        
class RebarPlacer:
    

    def __init__(self, factory:RebarFactory):
        
        self.factory = factory
        

        self._setClearCover()
        # self.lUnit = section.lUnit


    def getBarsInRow(self, Nbar:int, barType:str, 
                     deff:float, width:float, direction:str='x'):
        """
        Evenly distributes a set of bars within a row.
        """
        
        if direction == 'x':
            positions = self._getBarPositon(Nbar, self.section.b)
            xyOut = [(x, deff) for x in positions]
        else:
            positions = self._getBarPositon(Nbar, self.section.d)
            xyOut = [(deff, y) for y in positions]
        
        bars = []
        for ii in range(Nbar):
            bars.append( self.factory.getRebar(barType, xyOut[ii]))
            
        return  RebarCollection(bars)
            
    def _getBarPositon(self, Nbar:int, width:float):
        if Nbar == 1:
            return [width/2]
        else:
            return list(np.linspace(0,1, Nbar)*width)



class StirrupGroup:
    rebar:Rebar
    rStirrup:float
    dstirrup:float




