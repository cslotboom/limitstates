"""
A basic example showing how structural objects can be loaded and acted on by 
design codes.
"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

L = 6
Fy = 350
sectionName = 'W310X118'

# Define the material, in this case a code specific steel with Fy = 350
mat = s16.MaterialSteelCsa19(Fy)

# Define a steel from a database, in this case csa's cisc 12 for w sections.
steelSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
section         = ls.getByName(steelSections, sectionName)

# make a member, in this case a simplely supported beam 6m long beam.
member = ls.initSimplySupportedMember(L, 'm')

# Make a design object
beam = s16.BeamColumnSteelCSA24(member, section)

# Check capacity using CSA's s16 material standard.
Mr = s16.checkBeamMrSupported(beam) / 1000

