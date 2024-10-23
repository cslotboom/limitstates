"""
This example showcases features limitstate has for plotting structural 
elements. All plotting is done through matplotlib's pyplot library.

We start by importing some material libraries

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import limitstates.design.csa.o86.c19 as o86

# BASIC PLOTTING HOW-TO
"""
It's possible to plot sections directly throught the "plotSection" function,
or through the "plotElementSection" function.

The plotsection function makes some basic assumption, but mostly leaves 
customizing the plot to the user.

The "plotElementSection" has access to design information, and uses these to 
make more complicated plots with less user input. 

A basic example is shown below.

"""
myMat = ls.MaterialElastic(200*1000)
section = ls.getSteelSections(myMat, 'us', 'aisc_16_si', 'W')[0]
member  = ls.initSimplySupportedMember(6, 'm')
element = s16.BeamColumnSteelCsa24(member, section)

fig, ax = ls.plotElementSection(element)
fig, ax = ls.plotSection(section)

"""
Parts of plots can be controlled with the "PlotConfigCanvas", which configures
the plot's canvas, and "PlotConfigObject", which configures the appearance of 
an individual objects.
"""

customObjConfig = ls.PlotConfigObject('#97bcfc', originLocation=2)
customCanvasConfig = ls.PlotConfigCanvas(10)
fig, ax = ls.plotSection(section, 
                         canvasConfig = customCanvasConfig, 
                         objectConfig = customObjConfig)

"""
The plotSection function can also be customized using kwargs for matplotlib's 
ax.fill object. Any propreties given to the kwargs will overwrite propreties set
in the configuration objects.
"""

fig, ax = ls.plotSection(section, hatch = '/', 
                         edgecolor='#084250', c = '#97bcfc', linewidth = 3)



"""
Element plotting has less direct user customization, but can be used to easily
make more complicated plots.

All design elements Elements have a "EleDisplayProps" object, which stores a
"PlotConfigCanvas", and "PlotConfigObject". Design specific plotting 
information is also stored in these.

The element will also store a section and member object. By default the 
section and member used will be the same as the section/member used by design, 
but these could be overwritten to display different sections.

"""

customObjConfig = ls.PlotConfigObject('#97bcfc', originLocation=2)
customCanvasConfig = ls.PlotConfigCanvas()

customEleProps = ls.EleDisplayProps(section, member, 
                                    customObjConfig, customCanvasConfig)

element.setEleDisplayProps(customEleProps)
fig, ax = ls.plotElementSection(element)


# SPECIAL PLOT TYPES
# Glulam members with fire sections
"""
plotElementSection will include special propreties with each element. For 
example, glulam elements with a fire section will have the char plotted.

They will also include a fill, estimating where laminations would be.
Note that while the glulam lamination height it doesn't have any
physical meaning right now.

"""
L  = 6 
myMat       = ls.MaterialElastic(9.5*1000)
section     = ls.SectionRectangle(myMat, 215, 456)
myElement   = o86.getBeamColumnGlulamCsa19(L, section, 'm')

FRR = 60
FRR = o86.getFRRfromFireConditions(FRR, 1)
o86.setFireSectionGlulamCSA(myElement, FRR)   

fig, ax     = ls.plotElementSection(myElement)


# CLT sections
"""
CLT sections and their char layers can also be plotted. If the section is 
burned, the plotElementSection will attempt to plot the burned section.
"""

section = o86.loadCltSections()[11]

firePortection  = o86.GypusmFlatCSA19('15.9mm')
designProps     = o86.DesignPropsClt19(firePortection)
member          = ls.initSimplySupportedMember(6, 'm')

clt = o86.BeamColumnCltCsa19(member, section, designProps = designProps)
FRR = 120
o86.setFireSectionCltCSA(clt, FRR)
knet = o86.kdfi*o86.kfi['cltV']

Mr = o86.checkMrCltBeam(clt, knet, useFire = True) 

ls.plotSection(clt.section)
ls.plotElementSection(clt)

