"""
This example shows how a simply supported W steel element can be checked for 
moment when the beam is unsupported. 
A plot of the beam analyzed is output as part of this example.
"""

"""
The capacity of the section is determined by limitstates, and compared
to forces from an analyzed beam using the planesections library.

First the base limitstates library is imported, then s16 steel design library 
for csa o86. The library planesections is imported to run the beam analysis.

"""

"""
This example shows how to check a steel column for compression.
"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

beamName = 'W530x72'
L = 6
Fy = 345

mat = s16.MaterialSteelCsa24(Fy)
steelWSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'W')

section = ls.getByName(steelWSections, 'W310x107')
column  = s16.getBeamColumnSteelCsa24(6, section)
Cr      = s16.checkColumnCr(column) / 1000

    

