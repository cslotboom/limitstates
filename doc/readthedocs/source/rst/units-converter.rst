Unit Converters
===============

The unit converts are embeded in objects with units. 
Each instance of the class stores a base unit, and the ratio between that unit and other possible units. 
The base UnitConverter class is referenced below. 
Specific UnitConverter classes exist that inherit from the base class. 
This includes for most common units used in structural analysis, for example, length, force, and stress. 

.. autoclass:: limitstates.units.converter.UnitConverter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: limitstates.units.converter.ConverterLength
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: limitstates.units.converter.ConverterForce
   :members:
   :undoc-members:
   :show-inheritance:
        

.. autoclass:: limitstates.units.converter.ConverterStress
   :members:
   :undoc-members:
   :show-inheritance:
        

.. autoclass:: limitstates.units.converter.ConverterDensity
   :members:
   :undoc-members:
   :show-inheritance:
        
