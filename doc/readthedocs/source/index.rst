
limitstates Documentation
==========================
Limitstates is a python library that can represent and design of structural elements 
according to code and material standards from various countries. 
Limit states has two main components: a set of classes that representations structural 
objects, e.g. A Ibeam that is 6m long made or steel; and design libraries that can 
act on elements and determine capacities, e.g. Canada's CSA s16 steel material standard.
**Limitstates is currently incomplete and in public beta testing.**
**Expect breaking changes before the final release.**

The following website documents all classes and functions the user can access in limitstates.


The units library is used to manage and convert between different unit systems.
The objects used represent structural objects.
The Diagram module is used to plot representations of the beam.
The Postprocess module is used to plot outputs of the analysis, including force diagrams and deflections

Note that the core classes and API are complete, but development is still in progress. Expect some sytax changes before final release, however deprication warnings
will be given for breaking changes.

Install using:

.. code :: python

	pip -m install limitstates

Install with optional dependancies for opensees solver using:

A simple script is shown below:

.. literalinclude:: /example/Ex1 - demo.py

.. toctree::
   :maxdepth: 3
   :numbered:
   
   rst/units
   rst/objects



Library Organization
======================
There are four main parts of the limitstates library: units, objects, design, analysis.

The units library is a light-weight module for unit conversions. 
All structural objects in the limitstates libary are dependant on the unit library for conversions. 
See :ref:`units <units>`: for more detail.

The objects library contains generic classes that represent and manipulate structural elements. 
Members of the object library are not specific to any code, for example a W530x150 cross section has the same geometry for American and Canadian codes.
See XXX for more detail.

The design library contains specialized objects for a particular design code, and functions that act on them. 
For example,   "BeamColumnSteelCsa24" is a code specific implementations of the generic "BeamColumn" class, 
and the function "checkBeamMrSupported", acts on it to determine a sections unsupported moment. 
Design libraries are divided by country and material standard. Currently, content only exists for Canadian design codes.
See XXX for more detail.

The Analysis library will contain functions that act on structural objects to analyze them. 
Currently content does not exist for this library.



=============
 Developed by
=============

*Christian Slotboom* `<https://github.com/cslotboom/limitstates>`_.

| M.A.Sc. Structural Engineering
| Engineer in Training 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
