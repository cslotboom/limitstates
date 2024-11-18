"""
This example shows how a multi-span glulam beam can be checked for Moment.


The base limitstates library is imported for object manipulation.
The design library for csa o86's is imported for specific objects and checks
The library Planesections is used for beam analysis.
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
width = 175 # Section width in mm
depth = 608 # Section depth in mm
length = 8  # Beam length in m
supportPositions = [0, 6.]

myMat       = o86.loadGlulamMaterial('SPF', '20f-E')
mySection   = ls.SectionRectangle(myMat, width, depth)


"""
Because the beam in this example is multi-span, the typical initization 
functions do not apply. Instead we'll build up a custom member using a set
of nodes and lines.
"""
# We set up a custom member
pinSupport    = ls.SupportTypes2D.PINNED.value
rollerSupport = ls.SupportTypes2D.ROLLER.value
freeSupport     = ls.SupportTypes2D.FREE.value

n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
n2 = ls.Node([supportPositions[1], 0.], 'm', support = rollerSupport)
n3 = ls.Node([length, 0.], 'm', support = freeSupport)
line1  = ls.getLineFromNodes(n1, n2)
line2  = ls.getLineFromNodes(n2, n3)
member = ls.Member([n1, n2, n3], [line1, line2])


designProps = o86.DesignPropsGlulam19(Lx=[5,3], 
                                      kexB=[1.92, 1.92], 
                                      lateralSupport=[True, False])
myElement   = o86.BeamColumnGlulamCsa19(member, mySection, designProps)

myElement.eleDisplayProps.configObject.originLocation = 3
ls.plotElementSection(myElement)

"""
Define the beam nodes loads
"""

beamPs      = ls.convertBeamColumnToPlanesections(myElement)
kN = 1000
q = [0.,-35*kN]
beamPs.addVerticalLoad(length, -70*kN, label='A')
beamPs.addVerticalLoad(3, -70*kN, label='C')
beamPs.addDistLoad(0, length, q, label='B') 
ps.plotBeamDiagram(beamPs, labelForce=True, plotForceValue=True)

"""
Run the analysis
"""
analysis = ps.PyNiteAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)


"""
Plot the shear force, and show labeling.
"""
ps.plotVertDisp(beamPs)
ps.plotShear(beamPs,  0.001, labelPOI=True, yunit='kN')
ps.plotMoment(beamPs, 0.001, labelPOI=True, yunit='kNm')

xyBMD = beamPs.getBMD()

diagram = ls.DesignDiagram(np.column_stack(xyBMD))
xCoords = diagram.getIntersectionCoords()

# Check the capacity of the beam assuming it is laterally supported.
Mr = o86.checkMrGlulamBeamSimple(myElement)
Vr = o86.checkVrGlulamBeamSimple(myElement)

# Check the capacity of the beam assuming it is a multispan beam.
MrMulti, xSpans, kz, kL = o86.checkMrGlulamBeamMultiSpan(myElement, diagram)

