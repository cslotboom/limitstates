"""
This example shows how a the rebar can be placed within a simply supported,
single span concrete beam. A input factored moment is provided to the beam, and
the bars are placed such that the output moment is greater.

The capacity of the section is determined by limitstates, and compared
to forces from an analyzed beam using the planesections library.

First the base limitstates library is imported, then c24 concrete design 
library. 

"""
import limitstates as ls
import limitstates.design.csa.a23.c24 as a23

"""
Next the beam section is defined. A concrete material is created, as well as
a section and set of stirrups.
"""
fc = 25
c = 30
L = 5
h = 900 
b = 450

barType = '30M'
Mf = 1100

mat         = a23.MaterialConcreteCSA24(fc)
section     = ls.SectionRectangle(mat, b, h)
stirrupBar  = a23.getStandardRebar('10M')
stirrups    = ls.StirrupGroup(stirrupBar)
concreteSection = ls.SectionConcrete(section, stirrups = stirrups)

"""
Rebar information, such as cover, has to be defined manually, and is a 
design proprety of the section.
"""

designProps = a23.DesignPropsConcrete24(cover= c)

member = ls.initSimplySupportedMember(L, 'm')
beam   = a23.BeamColumnConcreteCsa24(member, concreteSection, designProps) 


"""
The Bottom steel of the section is then defined.
"""
status = a23.designBottomSteelForMr(Mf, beam, barType)
ls.plotSection(beam.section)


"""
We check the moment within the section and confirm it meets expectations.
"""
Mr = a23.getSectionMr(beam.section) / 1000


print('Overrienforced:', status)
print(Mf, Mr)
