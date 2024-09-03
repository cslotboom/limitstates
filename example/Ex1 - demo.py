"""
A basic example showing how structural objects can be loaded and acted on by 
design codes.
"""
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

# Make a design object
beam = s16.BeamColumnSteelCsa24(member, section)

# Check capacity assuming it's laterally supported using CSA's s16 standard.
Mr = s16.checkBeamMrSupported(beam) / 1000

