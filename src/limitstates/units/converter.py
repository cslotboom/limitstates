"""
A unit converter that can both represent units and convert between units of
different types.
"""

from abc import ABC
from dataclasses import dataclass

__all__= ["UnitConverter","ConverterLength", "ConverterLengthImperialinch",
          "ConverterForce","ConverterStress","ConverterDensity"]

@dataclass
class Unit:
    name:str
    factor:float

class UnitConverter(ABC):
    """
    The base unit converter class, contains interfaces all unit converter
    classes use.
    """
    unitDict = {}
    
    def _unsupportedException(self, unit):
        raise Exception(f'Unit {unit} is unspported, expected one of '\
                        f'{list(self.unitDict.keys())}')
    
    def _checkInDict(self, unit):
        if unit in self.unitDict:
            return True
        else:
            self._unsupportedException(unit)
    
    def convert(self, inputUnit:str, outputUnit:str, value:float):
        """
        Converts the value of one unit to another unit.


        Parameters
        ----------
        inputUnit : str
            A string representing the input unit. Must be one of the units in 
            the the unit converter 'unitDict' attribute.
        outputUnit : str
            A string representing the output unit. Must be one of the units in 
            the the unit converter 'unitDict' attribute.
        value : float
            The current value to be converted.

        Returns
        -------
        float
            The "value" converted from the input unit to the output unit.

        """

        return value * (self.getConversionFactor(inputUnit, outputUnit))
        
    def getConversionFactor(self, inputUnit:str, outputUnit:str):
        """
        Finds the conversion factor between two units.

        Parameters
        ----------
        inputUnit : str
            A string representing the input unit. Must be one of the units in 
            the the unit converter 'unitDict' attribute.
        outputUnit : str
            A string representing the output unit. Must be one of the units in 
            the the unit converter 'unitDict' attribute.

        Returns
        -------
        cfactor: float    
            The conversion factor between units.

        """
        #!!! Consider returning 1 if the units are the same. Check the performance of this.
        
        # Most of the time we expect units to work, so we use try and except.
        try:
            return self.unitDict[inputUnit] / self.unitDict[outputUnit]
        # In the rare case they do not work, find out what went wrong.
        except:
            self._checkInDict(inputUnit)
            self._checkInDict(outputUnit)       
        
    def getFactorUnit(self, unit:str):
        """
        Returns the conversion factor for a given unit.

        Parameters
        ----------
        outputUnit : str
            The input unit type, must be unit from the unit dictionary.

        Returns
        -------
        float
            The output conversion factor.

        """
        
        self._checkInDict(unit)
        return self.unitDict[unit]     
        
        
class ConverterLength(UnitConverter):
    """
    A converter for length units. Supports: 'm', 'mm', 'in', 'ft'
    """
    type = 'length'
    unitDict = {'m':1, 'mm':0.001, 'in':0.0254, 'ft':0.0254*12}
           
class ConverterLengthImperialinch(UnitConverter):
    type = 'length'
    unitDict = {'m':39.37, 'mm':0.03937, 'in':1, 'ft':12}
    
class ConverterForce(UnitConverter):
    """
    A converter for length units. Supports: 'N', 'kN', 'lbf'.
    """
    type = 'force'
    unitDict = {'N':1, 'kN':1000, 'lbf':4.44822162}
        
class ConverterStress(UnitConverter):
    type = 'stress'
    unitDict = {'Pa':1, 'kPa':1000, 'MPa':1e6, 'GPa':1e9, 
                'psi':0.0001450377, 'psf':0.020885434273039}
        
class ConverterDensity(UnitConverter):
    type = 'mass'
    unitDict = {'kg/m3':1, 'lbm/ft3':0.062427960576145, 'N/m3':9.8066500286389, 
                'kN/m3':9.8066500286389 / 1000}


