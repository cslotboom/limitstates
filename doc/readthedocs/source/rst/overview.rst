Overview
========

There are four main parts of the limitstates library: units, objects, design, analysis.

The units library is a light-weight module for unit conversions. 
All structural objects in the limitstates libary are dependant on the unit library for conversions. 
See :ref:`units <units>`: for more detail.

The objects library contains generic classes that represent and manipulate structural elements. 
Members of the object library are not specific to any code, for example a W530x150 cross section has the same geometry for American and Canadian codes.
See :ref:`objects <objects>`: for more detail.

The design library contains specialized objects for a particular design code, and functions that act on them. 
For example,   "BeamColumnSteelCsa24" is a code specific implementations of the generic "BeamColumn" class, 
and the function "checkBeamMrSupported", acts on it to determine a sections unsupported moment. 
Design libraries are divided by country and material standard. Currently, content only exists for Canadian design codes.
See :ref:`design <design>`: for more detail.

The Analysis library will contain functions that act on structural objects to analyze them. 
The analysis Library is a work in progress.


