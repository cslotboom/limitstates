"""
This example shows how both stirrups and longidtudinal bars can be manually
placed withn a section.

Stirrups and longditudinal bars are added, then the capacity of the beam is 
manually checked.

First the base limitstates library is imported, then c24 concrete design 
library. 
"""
import limitstates as ls
import limitstates.design.csa.a23.c24 as a23

"""
Next the beam section is defined. A concrete material is created, as well as
a section and set of stirrups.
"""

h = 900
b = 450
fc = 30
c = 40

mat         = a23.MaterialConcreteCSA24(fc)
section     = ls.SectionRectangle(mat, b, h)
concreteSection = ls.SectionConcrete(section)

"""
Rebar information, such as cover, has to be defined manually, and is a 
design proprety of the section.
"""
designProps = a23.DesignPropsConcrete24(cover= c)
member = ls.initSimplySupportedMember(5, 'm')
beam = a23.BeamColumnConcreteCsa24(member, concreteSection, designProps)
 
beam.eleDisplayProps.setPlotOrigin(3)

"""
Stirrups are placed in the element, and mannually given an offset with the
flag "dshift".
"""
a23.placeStirrupRowInElement(beam, 2, '10M', dshift = 40)

"""
Longditudinal bars are placed in the section. The flag "includeRadius" is used
to force rebar to avoid the stirrup radius.
"""
section     = beam.getSection()
designProps = beam.designProps

Nbar = 4
includeRadius = True
placer = a23.RebarPlacerRowCSA24(section, designProps)
placer.place(Nbar, '25M', 1, includeRadius=includeRadius)
placer.place(Nbar, '15M', 2, includeRadius=includeRadius)

"""
Create a plot of the secton
"""
fig, ax = ls.plotElementSection(beam)

# s2 = a23.getStandardStirrupGroup('10M')

Mr = a23.getSectionMr(beam.section) / 1000
Vr = a23.getElementVr(beam) / 1000

print('The Shear resistance is:', Vr)
print('The Moment resistance is:', Mr)
