"""
This example shows how a simply supported W steel element can be checked for 
moment when the beam is laterally supported, or unsupported.  
A 6m long beam is analyzed with two point loads as shown bellow. 
A plot of the beam analyzed is output as part of this example. 
The beam is assessed in three conditions: 
    continuous lateral support is provided to the beam, 
    the beam is unsupported and loaded on it's top flange, and 
    the loaded at it's shear center.
"""

"""
The capacity of the section is determined by limitstates, and compared
to forces from an analyzed beam using the planesections library.

First the base limitstates library is imported, then s16 steel design library. 
The library planesections is imported to run the beam analysis.

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import planesections as ps
import numpy as np

"""
Next the beam is created. First a material with 345MPa steel is set up, and the
W530x72 section is loaded from the aisc library, using si units.

"""
beamName = 'W530x72'
L  = 6
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
MrUnSup = s16.checkBeamMrUnsupportedW(beam, 1) / 1000

"""
To analyze the beam, it is converted convert it to a planesections beam object, 
then apply our loading. A convert function in limistates can be used to 
directly transfer our beam over. A plot  is also create a figure of the beam 
diagram. Refer to planesections documentation to see how to analyze an 
arbitrary beam.
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
The strength of the beam is then determined assuming it's loaded at it's shear
center. This would be the case if purlins were framing into the side of the
beam, and the loading was balanced, i.e. there was a purlin on either side of
the beam.
"""

props  = s16.DesignPropsSteel24(Lx = L)
beam   = s16.BeamColumnSteelCsa24(member, section, props)

xyBMD = beamPs.getBMD()
bmd = ls.DesignDiagram(np.column_stack(xyBMD))
omega = s16.getOmega1FromDesignDiagram(bmd)

MrShearCenter = s16.checkBeamMrUnsupportedW(beam, omega) / 1000
print(MrSup, MrUnSup, MrShearCenter)


"""
Based on our analysis:
    - If the beam is laterally supported, it passes easily. 
    - If the beam is laterally unsupported and loaded on it's top flange, it fails by a large margin
    - If the beam is laterally unsupported and loaded at it's shear center, it barely passes.

"""