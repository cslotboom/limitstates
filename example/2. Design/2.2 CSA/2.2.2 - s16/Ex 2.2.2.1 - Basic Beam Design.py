"""
This example shows how a simply supported steel element can be checked for 
moment.
"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls
from limitstates.objects.read import getSteelSections

import planesections as ps

beamName = 'W530x72'
L = 6
Fy = 345

mat = s16.MaterialSteelCsa24(Fy)
steelSections = getSteelSections(mat, 'us', 'aisc_16_si', 'W')
section = ls.getByName(steelSections, beamName)

# Initilize a simply supported beam member
member = ls.initSimplySupportedMember(L, 'm')
props = s16.DesignPropsSteel24(Lx = L, kx = 1)
beam = s16.BeamColumnSteelCsa24(member, section, props)

# Find the moment assuming the beam is a laterally supported or unsupported.
MrSup = s16.checkBeamMrSupported(beam) / 1000
Mr    = s16.checkBeamMrUnsupportedW(beam) / 1000

# Make a plot
ls.plotElementSection(beam)

# Create a planesections beam object
beamPs      = ls.convertBeamColumnToPlanesections(beam)

# Apply some loading to the beam - we assume it's factored.
kN = 1000
q = [0.,-35*kN]
beamPs.addVerticalLoad(L/3, -70*kN, label='A')
beamPs.addVerticalLoad(2*L/3, -200*kN, label='B')

# Make a diagram of the beam
ps.plotBeamDiagram(beamPs, labelForce=True, plotForceValue=True)

# Analyze the beam using pynite
analysis = ps.PyNiteAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)

# Plot a bendign moment diagram
ps.plotMoment(beamPs, 0.001, labelPOI=True, yunit='kNm')