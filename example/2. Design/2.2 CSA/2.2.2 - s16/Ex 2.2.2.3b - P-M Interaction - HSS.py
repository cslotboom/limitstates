"""
This example shows some
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

kN = 1000
m = 1
MPa = 1


# beamName = '304.8X203.2X9.5'
beamName = '305x203x9.5'
L   = 4*m
Fy  = 350*MPa
Cf  = 1600*kN
Mfx = 100*kN*m

mat = s16.MaterialSteelCsa24(Fy)
steelSections = ls.getSteelSections(mat, 'csa', 'cisc_12', 'hss')

section = ls.getByName(steelSections, beamName)
column  = s16.getBeamColumnSteelCsa24(L, section)

omegax1 = 1 # Assume positive curvature and 100kNm on either end.

uts = s16.checkBeamColumnCombined(column, Cf, Mfx, 
                                  omegax1 = omegax1, isBracedFrame= True)


fig, ax = ls.plotElementSection(column)
