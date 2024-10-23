"""
This example shows how clt can be initialized and checked.
It is a work in progress!
"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as o86



section = o86.loadCltSections()[1]
member = ls.initSimplySupportedMember(6, 'm')
beamColumn = o86.BeamColumnCltCsa19(member, section)

Mr  = o86.checkMrCltBeam(beamColumn)
MrW = o86.checkMrCltBeam(beamColumn, useStrongAxis=False)

ls.plotSection(section)
ls.plotElementSection(beamColumn)