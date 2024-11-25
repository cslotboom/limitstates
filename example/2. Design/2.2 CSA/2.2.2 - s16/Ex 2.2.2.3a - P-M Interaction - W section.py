"""
This example shows how a W beamcolumn can be checked for moment /shear
interaction when the beam is unsupported. 

"""

"""
The capacity of the section is determined by limitstates, and compared
to forces from an analyzed beam using the planesections library.

First the base limitstates library is imported, then s16 steel design library 
for. The library planesections is imported to run the beam analysis.
"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
kN = 1000
beamName = 'W530x72'
L = 6
Fy = 345
Cf = 2000*kN
Mfx = 300*kN

mat = s16.MaterialSteelCsa24(345)
steelWSections = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')

section = ls.getByName(steelWSections, 'W310X118')
column  = s16.getBeamColumnSteelCsa24(6, section)
Cr      = s16.checkColumnCr(column) / 1000

beam = s16.getBeamColumnSteelCsa24(L, section)
omega1x = 0.4

u = s16.checkBeamColumnCombined(beam, Cf, Mfx, 
                                omegax1=omega1x, isBracedFrame = True)

