"""
An example that overviews the special object propreties elements have,
in particular, the design propreties.

All structural sections have three objects, design sections

This example is a work in progress

"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

"""
For convience some units, and the section dimensions are defined.
By default materials are in units of MPa, sections are in units of mm,
and length is in units of m.
"""
MPa = 1
width = 356 # Section width in mm
depth = 600 # Section depth in mm
length = 6  # Beam length in m

"""
The simplest way to create a design element is to use helper functions, and
material libraries. 
For most problems, the default options assumed here will handle
Code specific materials and elements.
"""
# Load a code specific csa glulam material
myMat     = csa.loadGlulamMaterial('SPF', '20f-E')
# Load a section. Sections are code agnostic, a generic rectangle is used.
mySection = ls.SectionRectangle(myMat, width, depth) 
# Load a code specifi glulam beamcolumn element. 
# The default beam is simply supported and laterally suppored on the compression side
myElement = csa.getBeamColumnGlulamCsa19(length, mySection, 'm')


# my
