"""
This example shows how both stirrups and longidtudinal bars can be 
automatically set within a section.

First the base limitstates library is imported, then c24 concrete design 
library. 
"""
import limitstates as ls
import limitstates.design.csa.a23.c24 as a23

"""
Next the beam section is defined. A concrete material is created, as well as
a section and set of stirrups.
"""
kN = 1
m = 1

h = 900
b = 450
fc = 30
c = 40

Vr = 700*kN
Mr = 1100*kN*m

mat         = a23.MaterialConcreteCSA24(fc)
section     = ls.SectionRectangle(mat, b, h)
concreteSection = ls.SectionConcrete(section)

"""
Rebar information, such as cover, is to be defined manually. The beam element 
is then created from the section.
"""
designProps = a23.DesignPropsConcrete24(cover= c)
member = ls.initSimplySupportedMember(5, 'm')
beam = a23.BeamColumnConcreteCsa24(member, concreteSection, designProps)
 

"""
Stirrups are designed, then the bottom steel. If stirrups are set in the 
section, the bottom steel placed will respect the bar locations. 
By default, the curve radius of into the rebar position.
"""
a23.designStirrupsForVr(Vr, beam, barType='15M')
a23.designBottomSteelForMr(Mr, beam, barType='25M')


"""
Create a plot of the section, and output section capacities.
"""
fig, ax = ls.plotElementSection(beam)

Mr = a23.getSectionMr(beam.section) / 1000
Vr = a23.getElementVr(beam) / 1000

print('The Shear resistance is:', round(Vr), 'kN')
print('The Moment resistance is:', round(Mr), 'kNm')
