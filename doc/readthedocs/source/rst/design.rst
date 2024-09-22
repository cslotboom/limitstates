Design
=======

Design libraries can be used to act on structural objects, and determine capacities. The also contain special design objects, which are code specific versions of generic objects.

The design libraries are stored in a hierarchy that starts with the building code region, for example US or Canada. For each building code area there are material codes, for example  Canada's timber code (CSA o86), then code iterations, for example 2019

Each material code iteration acts as a stand-alone library that can be imported by the user.

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

**Currently, only canadian codes are supported by limit states**


#. :doc:`design-csa`



.. toctree::
   :maxdepth: 3
   :hidden:
   
   design-csa.rst



