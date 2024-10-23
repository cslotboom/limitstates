.. _objects:

Objects API Reference
=====================

The objects library is used to represent structural elements. 
This includes key object representations, and component objects.
It also includes 

There are five key classes of objects: materials, sections, members, elements, and design elements. Most objects are design agnostic, in that they have similar properties between all building codes. Users will mostly work directly with the highest level component, the design element. A more detailed break down of each element type is as follows:

Material
Materials represent the material properties of a solid, which includes at minimum it's elastic modulus. While base materials are design agnostic, most  material objects are specialized to design codes, and these these include section strengths as defined in those codes.

Section
Sections define the shape of a structural cross section. Sections can be uniform, or composite, in the case of CLT or concrete. Sections are design agnostic, in that their properties are not dependant on any material code

Members
Members define the Length, position, and shape of a structural element in space. They also define information needed to analyze that structure, such as support conditions. For example, glulam timber materials will contain bending strength, shear strength, etc.

Elements
Structural elements are a combination of sections and members. A structural element will have it's geometry fully defined, and contain element contains all the information needed to analyze and object.

Design Elements
Design elements are a combination of structural elements with their design information. These design elements are what users will work directly with, and live in specific design libraries. Many design libraries contain functions that can initialize a basic structural element. 
All design objects have the following "special" attributes dictionaries.

Design Props:
	- This is used to store any internal attributes limitstates need for design that are design code dependant. Examples include the fire portection used for glulam elements, or if a beam element is curved.
User Props:
	- This provides a safe place for users to store any additional information they want in design. The limitstates library will objects will not use this attribute.
Element Display Props
	- This is used to store information about output element geometry. Examples include making plots or rendering geometry.

Some elements, such as CLT, may have design geometry that differs from their analysis model. In the example of CLT, while it is a 2D plate, it is often modeled as if it was a beam.


#. :doc:`objects-material`
#. :doc:`objects-section`
#. :doc:`objects-geometry`
#. :doc:`objects-element`
#. :doc:`objects-helpers`
#. :doc:`objects-display`


.. toctree::
   :maxdepth: 2
   :hidden:
   
   objects-material.rst
   objects-section.rst
   objects-geometry.rst
   objects-element.rst
   objects-helpers.rst
   objects-display.rst


