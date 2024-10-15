"""
This example shows how clt can be initialized and checked for fire design.
It is a work in progress!
"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

section = o86.loadCltSections()[11]

firePortection = o86.GypusmFlatCSA19('15.9mm')
designProps = o86.DesignPropsClt19(firePortection)

member = ls.initSimplySupportedMember(6, 'm')

clt = o86.BeamColumnCltCsa19(member, section, designProps = designProps)
FRR = 120
o86.setFireSectionCltCSA(clt, FRR)
knet = o86.kdfi*o86.kfi['cltV']

Mr = o86.checkMrCltBeam(clt, knet, useFire = True) 
