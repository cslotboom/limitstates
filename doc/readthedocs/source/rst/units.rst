.. _units:

Units API Reference
===================

While is often not used directly by the user, the units library is a core building block of limitstates. 
It provides a consistent way for tracking and converting between different units.

All objects that have dimension store the units they use, and have an imbedded "converter" objects that can return a conversion factor between different units. 
For example, a cross section will have an attribute "lUnit", and can return the conversion factor between it's current unit and another unit with the "lConvert" method. 


.. code-block:: python


	section.lUnit
	lfactor = section.lConvert('in')


#. :doc:`units-converter`


.. toctree::
   :maxdepth: 2
   :hidden:
   
   units-converter.rst

