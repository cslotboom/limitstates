"""
This example shows how a basic glulam element can be checked for shear and
moment.
"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

import planesections as ps
import numpy as np

"""
For convience some units, and the section dimensions are defined.
By default materials are in units of MPa, sections are in units of mm,
and length is in units of m.
"""
MPa = 1
width = 356 # Section width in mm
depth = 600 # Section depth in mm
length = 8  # Beam length in m
supportPositions = [0,5]

myMat       = o86.loadGlulamMaterial('SPF', '20f-E')
mySection   = ls.SectionRectangle(myMat, width, depth)

# We set up a custom member
pinSupport = ls.SupportTypes2D.PINNED.value
n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
n2 = ls.Node([supportPositions[1], 0.], 'm', support = pinSupport)

line1 = ls.getLineFromNodes(n1, n2)

member = ls.Member([n1,n2], [line1])


designProps = o86.DesignPropsGlulam19()
myElement   = o86.BeamColumnGlulamCsa19(member, mySection, designProps)

beamPs = ls.convertBeamColumnToPlanesections(myElement)


"""
Define the beam nodes loads
"""
kN = 1000
q = np.array([0.,-1*kN])
beamPs.addVerticalLoad(3, -5*kN)
beamPs.addDistLoad(0, length, q) 
ps.plotBeamDiagram(beamPs)

"""
Run the analysis
"""
analysis = ps.PyNiteAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)

"""
Plot results
"""
ps.plotDisp(beamPs, scale=1000, yunit = 'mm')
ps.plotRotation(beamPs, scale=1000, yunit = 'mrad')

"""
Plot the shear force, and show labeling.
"""
ps.plotVertDisp(beamPs)
ps.plotShear(beamPs,labelPOI=True)
ps.plotMoment(beamPs,labelPOI=True)









# """
# For convience some units, and the section dimensions are defined.
# By default materials are in units of MPa, sections are in units of mm,
# and length is in units of m.
# """
# MPa = 1
# width = 356 # Section width in mm
# depth = 600 # Section depth in mm
# length = 6  # Beam length in m

# """
# The simplest way to create a design element is to use helper functions, and
# material libraries. 
# For most problems, the default options assumed here will handle
# Code specific materials and elements.
# """
# # Load a code specific csa glulam material
# myMat     = csa.loadGlulamMaterial('SPF', '20f-E')
# # Load a section. Sections are code agnostic, a generic rectangle is used.
# mySection = ls.SectionRectangle(myMat, width, depth) 
# # Load a code specifi glulam beamcolumn element. 
# # The default beam is simply supported and laterally suppored on the compression side
# myElement = csa.getBeamColumnGlulamCsa19(length, mySection, 'm')

# # Check the output using the design library.
# Mr = csa.checkMrGlulamBeamSimple(myElement)
# Vr = csa.checkVrGlulamBeamSimple(myElement)

# # =============================================================================
# # Manually create elements
# # =============================================================================
# """
# It's also possible to manually define our beam. This can be useful for more
# complex problems.
# """
# # Manually define a custom material.
# matDict = {'E':9500*MPa, 'fb':25*MPa, 'fv':1.5*MPa}
# myMat   = csa.MaterialGlulamCSA19(matDict)

# # Define a section .
# mySection   = ls.SectionRectangle(myMat, width, depth)   

# # Define the member manually by creating a line and defining supports.
# myline  = ls.getLineFromLength(length, 'm')

# # We collect the nodes and assign them support conditions.
# # A more complex beam could also be defined here, with different support
# n1, n2  = myline.n1, myline.n2
# pinCondition    = ls.SupportTypes2D.PINNED.value
# rollerCondition = ls.SupportTypes2D.ROLLER.value
# n1.setSupportType(pinCondition)
# n2.setSupportType(pinCondition)

# # We define the member. 
# myMember = ls.Member([n1, n2], [myline], 'm')

# # Define the design element
# myGlulamEle = csa.BeamColumnGlulamCsa19(myMember, mySection)

# # Check the output using the design library.
# Mr = csa.checkMrGlulamBeamSimple(myGlulamEle)
# Vr = csa.checkVrGlulamBeamSimple(myGlulamEle)
