"""
This example shows how to check a steel column for compression.
"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
from limitstates.objects.read import getSteelSections

beamName = 'W530x72'
L = 6
Fy = 345

mat = s16.MaterialSteelCsa24(Fy)
steelWSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')

section = ls.getByName(steelWSections, 'W310x107')
column  = s16.getBeamColumnSteelCsa24(6, section)
Cr      = s16.checkColumnCr(column) / 1000

    

