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

dispProps = csa.EleDisplayPropsGlulam19()
# my
