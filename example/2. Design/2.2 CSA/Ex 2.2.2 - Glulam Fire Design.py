"""
This example shows how a basic glulam element can be checked for shear and
moment in fire conditions with fire portection.
"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

"""
For convience some units, and the section dimensions are defined.
By default materials are in units of MPa, sections are in units of mm,
and length is in units of m.
"""
MPa = 1
width = 356 # Section width in mm
depth = 600 # Section depth in mm
length = 6  # Beam length in m

"""
We define a beam per example 2.2.1.
"""
myMat     = csa.loadGlulamMaterial('SPF', '20f-E')
mySection = ls.SectionRectangle(myMat, width, depth) 
myBeam = csa.getBeamColumnGlulamCsa19(length, mySection, 'm')

"""
We define fire portection using a gypsum object, and assign it to our section.
all design propreties will live in the design propreties class, see example 
2.1.1 for more details on design propreties
"""
firePortection = csa.GypusmRectangleCSA19('12.7mm')
myBeam.designProps.firePortection = firePortection

"""
We get the fire demands on our condition, in this case a beamcolumn.
The section will be exposed for 60 minutes on all 3 sides, and 12.7mm layer
of gypsum on it.
"""
# Define the fire demand for a beamcolumn
FRR      = csa.getFireDemands(60, csa.FireConditions.beamWithPanel)
# Define the fire potection
firePortection = csa.getGypsumFirePortection(csa.FireConditions.beamWithPanel, "12.7mm")

"""
Burn the section!
"""
csa.setFireSectionGlulamCSA(myBeam, FRR)

"""
The output fire section is now accessable in the beam design propreties 
"""

fireSection = myBeam.designProps.fireSection

"""
We can also define a knet for the section, and 
"""
knet = csa.kdfi * csa.kfi['glulam']

"""
Finally, we check the section in fire.
"""
Mr = csa.checkMrGlulamBeamSimple(myBeam, knet, useFire=True)
Vr = csa.checkVrGlulamBeamSimple(myBeam, knet, useFire=True )

