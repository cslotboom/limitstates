"""
Creates some images of CLT sections to showcase plotting functionality

"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

# Load a member
section = o86.loadCltSections()[1]
firePortection = o86.GypusmFlatCSA19('15.9mm')
dProps = o86.DesignPropsClt19(firePortection)
member = ls.initSimplySupportedMember(6, 'm')

configCanvas = ls.PlotConfigCanvas(showAxis=False)

# Make a typical section
clt = o86.BeamColumnCltCsa19(member, section, designProps = dProps)
ls.plotSection(section, canvasConfig=configCanvas)
ls.plotElementSection(clt)


# Burn a section and plot
section = o86.loadCltSections()[11]
clt = o86.BeamColumnCltCsa19(member, section, designProps = dProps)
clt.eleDisplayProps.configCanvas = configCanvas
FRR = 120
o86.setFireSectionCltCSA(clt, FRR)
ls.plotElementSection(clt)


# Burn a section
clt = o86.BeamColumnCltCsa19(member, section, designProps = dProps)
clt.eleDisplayProps.configCanvas = configCanvas
FRR = 90
o86.setFireSectionCltCSA(clt, FRR)
ls.plotElementSection(clt)


# Make a custom section
Es = 11700
Gs = 731
myMatS = ls.MaterialElastic(Es, Gs)
myMatS.E90 = Es/30
myMatS.G90 = Gs/13
myMatS.name = 'strong axis'
myMatS.grade = 'test'

L1 = ls.LayerClt(35, myMatS)
L2 = ls.LayerClt(35, myMatS, False)
    
layerGroup = ls.LayerGroupClt([L1, L1, L2, L1, L1])
section = ls.SectionCLT(layerGroup)

clt = o86.BeamColumnCltCsa19(member, section, designProps = dProps)
clt.eleDisplayProps.configCanvas = configCanvas


ls.plotElementSection(clt)
