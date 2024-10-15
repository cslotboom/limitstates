"""
All limistate objects that have units store the type of unit they use.
The following example showcases how the unit converters are embeded in 
different objects, and can be used.

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

# The material is defined in one set of units on initialization.
Fy = 350
mat = s16.MaterialSteelCsa24(Fy, sUnit='MPa')

# The stress unit is stored, and sConvert returns a conversion factor.
print(mat.sUnit)
ksiFactor = mat.sConvert('ksi')
Fyksi = mat.Fy * ksiFactor

# Similarly, the steel sections store the length they are in
L = 6
sectionName = 'W310X118'
steelSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
section         = ls.getByName(steelSections, sectionName)

# Return the current unit, in this case mm
print(section.lUnit)

# find the conversion factor for area between inches and mm.
lfactor = section.lConvert('in')
Ain = section.A * lfactor**2
