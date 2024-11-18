"""
This example shows how a simply supported W steel element can be checked for 
moment when the beam is unsupported. 
A plot of the beam analyzed is output as part of this example.
"""

"""
The capacity of the section is determined by limitstates, and compared
to forces from an analyzed beam using the planesections library.

First the base limitstates library is imported, then s16 steel design library 
for csa o86. The library planesections is imported to run the beam analysis.

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import planesections as ps


"""
Next the beam is created. First a material with 345MPa steel is set up, and the
W530x72 section is loaded from the aisc library, using si units.
"""
beamName = 'W530x72'
L = 6
Fy = 345

mat = s16.MaterialSteelCsa24(Fy)
steelSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'W')
section = ls.getByName(steelSections, beamName)

"""
A simply supported member is initialized, and the design propreties of the beam
are set. For the unsupported loading condition, it's assumed that forces are 
applied to the top chord, and the simplied method of analysis will be used.
Therefor, in this design the factors ω = 1, and kx = 1.2 is used.
"""
member = ls.initSimplySupportedMember(L, 'm')
props  = s16.DesignPropsSteel24(Lx = L, kx = 1.2)
beam   = s16.BeamColumnSteelCsa24(member, section, props)

"""
The capacity of the beam is determined assuming it has continous lateral 
support (c.l. 13.5), and no lateral support (c.l. 13.6)
"""
MrSup = s16.checkBeamMrSupported(beam) / 1000
Mr    = s16.checkBeamMrUnsupportedW(beam) / 1000
print (MrSup, Mr)


"""
Next the beam is analyzed. Using the library planesections. Refer to 
planesections for more documentation of beam analysis.
"""
# Make a plot
ls.plotElementSection(beam)

# Create a planesections beam object
beamPs      = ls.convertBeamColumnToPlanesections(beam)

# Apply some loading to the beam - assume it's factored.
kN = 1000
q = [0.,-35*kN]
beamPs.addVerticalLoad(L/3, -70*kN, label='A')
beamPs.addVerticalLoad(2*L/3, -200*kN, label='B')

# Make a diagram of the beam
ps.plotBeamDiagram(beamPs, labelForce=True, plotForceValue=True)

# Analyze the beam using pynite
analysis = ps.PyNiteAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)

# Plot a bending moment diagram
ps.plotMoment(beamPs, 0.001, labelPOI=True, yunit='kNm')

"""
Based on the output bending moment diagram
"""