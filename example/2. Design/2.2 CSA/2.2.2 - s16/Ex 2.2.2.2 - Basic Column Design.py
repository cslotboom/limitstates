"""
This example shows how a hss and W steel section are checked for compression.

First the base limitstates library is imported, then s16 steel design library 
for csa o86.
"""

import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

"""
Next the column is created. First a material with 345MPa steel is set up, and the
W310x107 section is loaded from the aisc library, using si units.
"""
columnName = 'W310x107'
L = 6
Fy = 345
mat = s16.MaterialSteelCsa24(Fy)
steelWSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'W')
section = ls.getByName(steelWSections, columnName)

"""
The B/t limits can be recalled for the section. These limits are automatically
checked when determing the column's capacity, but it's sometimes useful to pull
out the propreties directly.
"""
flangeRatio, webRatio = s16.getCompressionThicknessRatioW(section)

"""
The column is created, and Cr is checked for it and converted to kNm
"""
column  = s16.getBeamColumnSteelCsa24(6, section)
Cr      = s16.checkColumnCr(column) / 1000


"""
The process is repeated for Hss sections
"""

columnName = 'HSS127x127x7.9'
mat = s16.MaterialSteelCsa24(Fy)
steelHssSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'hss')
section = ls.getByName(steelHssSections, columnName)

column  = s16.getBeamColumnSteelCsa24(6, section)
Cr      = s16.checkColumnCr(column) / 1000

    

    

