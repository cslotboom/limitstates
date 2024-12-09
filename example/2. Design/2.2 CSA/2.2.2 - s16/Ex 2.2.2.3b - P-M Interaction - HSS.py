"""
This example shows how a HSS sections can be checked for P-M moment interaction

A 305x203x9.5 section in a braced frame is checked for combined 
bending / compression. It's assumed that:
    - The element is 6m tall
    - Cf = 1600
    - Mf = 100kNm at the top
    - Mf = -100kNm at the bottom, (single curvature bending)
    - CSA G40.20 steel is used with My = 350MPa
    - P-Delta effects have been included in the analysis.



"""

"""
First the base library is imported, along wtih the CSA s16 2024 steel library.
The section to be checked is defined, and loaded. The demands on the section
are also checked.

Note, if the beam was in positive curvature, then the moments would have 
opposite signs.
"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

kN = 1000
m = 1
MPa = 1
beamName = '305x203x9.5'
L   = 4*m
Fy  = 350*MPa
Cf  = 1600*kN
Mfx = 100*kN*m

"""
The section is generated, default support conditions are used for the beam.
The interaction is then checked using checkBeamColumnCombined
"""
mat = s16.MaterialSteelCsa24(Fy)
steelSections = ls.getSteelSections(mat, 'csa', 'cisc_12', 'hss')
section = ls.getByName(steelSections, beamName)
column  = s16.getBeamColumnSteelCsa24(L, section)

omegax1 = 1 # Assume positive curvature and 100kNm on either end.
uts = s16.checkBeamColumnCombined(column, Cf, Mfx, omegax1 = omegax1, 
                                  isBracedFrame= True)
