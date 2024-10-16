"""
This example showcases limitstate section / material libraries.

This example is a work in progress and will be improved.

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import limitstates.design.csa.o86.c19 as o86


"""
Steel sections can be loaded using the inputs 'code', 'standard-type', 
'section type'. Steel sections are often code independant, and the 'neutral'
function getSteelSections is ised to read them.

"""

mat = s16.MaterialSteelCsa24(345)
# The aisc 16 library in metric
aiscWSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'W')

# The aisc 16 library in imperial
aiscWimperialSections = ls.getSteelSections(mat, 'us', 'aisc_16_us', 'W')

# The aisc 16 library in metric for hss sections.
aiscHSSSections = ls.getSteelSections(mat, 'us', 'aisc_16_us', 'hss')

# CISC W sections
ciscSteelSections = ls.getSteelSections(mat, 'csa', 'cisc_12', 'W')



"""
For timber materials, sections are supplier and buildign code dependant.
These materials and sections are accessed through a design library.

The input will be the specific material library to load. 
see
https://limitstates.readthedocs.io/en/latest/rst/objects-section-db.html
"""

glMat     = o86.loadGlulamMaterial('SPF', '20f-E')
sections  = o86.loadGlulamSections(glMat)

cltSections = o86.loadCltSections('prg320_2019')