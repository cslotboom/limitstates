Elements
========

**Elements**
Structural elements are a combination of sections and members. A structural element will have it's geometry fully defined, and contain element contains all the information needed to analyze and object.

**Design Elements**
Design elements are a combination of structural elements with their design information. These design elements are what users will work directly with, and live in specific design libraries. Many design libraries contain functions that can initialize a basic structural element. 
All design objects have the following "special" attributes dictionaries.

Design Props:
	- This is used to store any internal attributes limitstates need for design that are design code dependant. Examples include the fire portection used for glulam elements, or if a beam element is curved.
User Props:
	- This provides a safe place for users to store any additional information they want in design. The limitstates library will objects will not use this attribute.
Geometry Props
	- This is used to store information about output element geometry. Examples include making plots or rendering geometry.

Some elements, such as CLT, may have design geometry that differs from their analysis model. In the example of CLT, while it is a 2D plate, it is often modeled as if it was a beam.

Element1D
---------

.. autoclass:: limitstates.objects.element.element.Element1D
   :members:
   :undoc-members:
   :show-inheritance:

BeamColumn
----------

.. autoclass:: limitstates.objects.element.element.BeamColumn
   :members:
   :undoc-members:
   :show-inheritance:


getBeamColumn
-------------

.. autofunction:: limitstates.objects.element.element.getBeamColumn
      
