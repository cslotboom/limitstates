# limitstates
<p align="center">
  <img src="https://github.com/cslotboom/limitstates/raw/main/doc/logo/logo-text.jpg" width="500">
</p>
A structural design and representation library.

## XXXXX limitstates is currently in early development XXXXX
It should only be used for testing purposes.

# Overview
limitstates is a python library that can represent and design structural 
elements according to code and material standards from various countries. Limit states has two main components: 
a set of classes that representations structural objects, e.g. A Ibeam that is 6m long made or steel; 
and design libraries that can act on elements and determine capacities, e.g. Canada's CSA s16 steel material standard.
**Limitstates is currently incomplete and in public beta testing.**
**Expect breaking changes before the final release.**

A simple script is shown below where a structural object is created and used.


```Python
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

L = 6
Fy = 350
sectionName = 'W310X118'

# Define the material, in this case a code specific steel with Fy = 350 MPa
mat = s16.MaterialSteelCsa24(Fy, sUnit='MPa')

# Define a steel section from a database, in this case a cisc 12 w section.
steelSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
section         = ls.getByName(steelSections, sectionName)

# make a member, in this case a simplely supported beam 6m long beam.
member = ls.initSimplySupportedMember(L, 'm')

# Make a element, which the design library can act on.
beam = s16.BeamColumnSteelCsa24(member, section)

# Check capacity assuming it's laterally supported using CSA's s16 standard.
Mr = s16.checkBeamMrSupported(beam) / 1000
```

# Installation

`
pip install limitstates
`

# Library Organization
There are four main parts of the limitstates library: units, objects, design, analysis.

The units library is a light-weight module for unit conversions. 
All structural objects in the limitstates libary are dependant on the unit library for conversions. 
See XXX for more detail.

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
