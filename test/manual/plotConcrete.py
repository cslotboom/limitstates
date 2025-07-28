import pytest
import limitstates.design.csa.a23.c24 as c24
import limitstates as ls



Nbar = 7
barType = '30M'

matConc  = c24.MaterialConcreteCSA24(25)
matRebar = c24.MaterialRebarCSA24(400)

section  = ls.SectionRectangle(matConc, 400, 500)
configDB = ls.DBConfig('csa', 'rebar', 'rebar')

concreteSection = ls.SectionConcrete(section)
rebarFactory    = ls.RebarFactory(matRebar, configDB, 'mm')   

s = 1.4*30
c = 30
dstirrup = 10
configPlacement = ls.RebarSpacingConfig(s, c, dstirrup)

locationEnum = 1
placer = ls.RebarPlacerRow(concreteSection, configPlacement, rebarFactory)
placer.place(Nbar, barType, locationEnum)

ls.plotSection(placer.section)