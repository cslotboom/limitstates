"""
This example shows how a multi-span beam can be checked. A beam will be 
examined with the fillowing propreties:
    - A W460x89 section is used
    - The beam has two spans, one 5m long and one 3m long
    - A continous load of 75kN/m is applied to the beam  
    
Four lateral support cases are considered:
    - The beam is continously laterally braced.
    - The beam is unbraced, and load applied to the shear center
    - The beam is unbraced, and Load is applied to the top flange
    - The beam is unbraced, load is applied to the top flange, 
    and an intermediate brace point is used in the middle of the first span
"""

"""

First the base limitstates library is imported, then s16 steel design library. 
The library planesections is imported to run the beam analysis, and numpy is 
used to do some numerical analysisl

"""
import limitstates.design.csa.s16.c24 as s16
import limitstates as ls

import planesections as ps
import numpy as np

"""
The section is loaded in.
"""
beamName = 'W250X58'
mat = s16.MaterialSteelCsa24(345)
steelSections = ls.getSteelSections(mat, 'us', 'aisc_16_si', 'W')
section = ls.getByName(steelSections, beamName)

"""
A custom member is created that represents the beam as defined above.
The member is created by defining a set of limitstate nodes, assigning them a
support condition, then defining lines.
"""
L1 = 5
L2 = 8
supportPositions = [0, L1, L2]
L = supportPositions[-1]

pinSupport      = ls.SupportTypes2D.PINNED.value
rollerSupport   = ls.SupportTypes2D.ROLLER.value

n1 = ls.Node([supportPositions[0], 0.], 'm', support = pinSupport)
n2 = ls.Node([supportPositions[1], 0.], 'm', support = rollerSupport)
n3 = ls.Node([L, 0.], 'm', support = rollerSupport)

line1  = ls.getLineFromNodes(n1, n2)
line2  = ls.getLineFromNodes(n2, n3)
member = ls.Member([n1, n2, n3], [line1, line2])

beam    = s16.BeamColumnSteelCsa24(member, section)

"""
The beam analysis is set up and run. The base beam is converted to an analaysis
beam using planesections.
"""
beamPs      = ls.convertBeamColumnToPlanesections(beam)
kN = 1000
q = [0.,-75*kN]
beamPs.addDistLoad(0, L2, q, label='B') 

# Make a diagram of the beam
ls.plotElementSection(beam)
ps.plotBeamDiagram(beamPs, labelForce=True, plotForceValue=True)

# Analyze the beam using pynite
analysis = ps.PyNiteAnalyzer2D(beamPs)
analysis.runAnalysis(recordOutput=True)

# Plot a bendign moment diagram
ps.plotMoment(beamPs, 0.001, labelPOI=True, yunit='kNm')
xyBMD = beamPs.getBMD()
bmd = ls.DesignDiagram(np.column_stack(xyBMD))

"""
Case 1 for the analysis is run. In this case omega is not used and the capacity
of each beam is the same for each span.
"""
MrmultiC1, _, omegaC1 = s16.checkMrBeamMultiSpan(beam, bmd, 1)    

"""
Case 2 for the analysis is run. The multispan analysis also has a default 
analysis mode for this condition. The factor omega is used to increase the 
moment capacity of the section based on the bending moment diagram
"""
MrmultiC2, _, omegaC2 = s16.checkMrBeamMultiSpan(beam, bmd, 2)    

"""
Case 3 is also covered by the default analysis mode for multi span beams.
When the top flange is loaded, the simplified analysis method from c.l. 13.6 is
employed. A effective length factor of 1.4 is applied to the beam
"""
MrmultiC3, _, omegaC3 = s16.checkMrBeamMultiSpan(beam, bmd, 3)    

"""
For Case 4, a point of lateral support is introduced halfway between the 
supports in span 1. The design propreties have to be manually set to accomodate
this effective span length, so a new beam is created.

a new beam is required, that has custom design propreties. The 
effective length of each section is set.
"""
designProps = s16.DesignPropsSteel24(Lx=[L1/2, L1/2, (L2-L1)], 
                                     kx=[1.4, 1.4, 1.4], 
                                     lateralSupport=[False, False, False])
manualBeam = s16.BeamColumnSteelCsa24(member, section, designProps)

Mrmulti4, xout, omegaC4 = s16.checkMrBeamMultiSpan(manualBeam, bmd, 4)    

"""
Comparing results, it's clear that the lateral bracing has a significant effect
on beam strength! It's important to make sure unbraced lateral conditions
are proprely captured in any design.
"""

