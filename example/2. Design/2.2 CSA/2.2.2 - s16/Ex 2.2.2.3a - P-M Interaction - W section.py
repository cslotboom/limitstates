"""
This example shows how a W beamcolumn can be checked for moment / compression
interaction.

A W360x237 section in a braced frame is checked for combined 
bending / compression. It's assumed that:
    - The element is 6m tall
    - Cf = 4400kN
    - Mf = 500kNm at the top
    - Mf = 400kNm at the bottom, (double curvature bending)
    - ASTM steel is used with My = 345MPa
    - P-Delta effects have been included in the analysis.
    
The example is broken into two parts. In the first part the combined bending
is checked. In the second part, a break down and explaination of each part of
the check is given, showing how results can be calcualted manually, and giving
an explanation on the code clauses used in each.

"""

"""
First the base library is imported, along wtih the CSA s16-24 steel library.
The section to be checked is defined, and loaded. The demands on the section
are also checked.

Note, if the beam was in positive curvature, then the moments would have 
opposite signs.
"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
kN  = 1000
beamName = 'W360x237'
L   = 6
Fy  = 345
Cf  = 4400*kN
Mfx_top = 500*kN
Mfx_bottom = 400*kN
Mfx = Mfx_top

mat = s16.MaterialSteelCsa24(345)
steelWSections = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
section     = ls.getByName(steelWSections, beamName)

"""
Default support conditions are used for the beam.
"""
beamColumn  = s16.getBeamColumnSteelCsa24(L, section)
ls.plotElementSection(beamColumn)

"""
The user inputs the loading condition. In this case, there are no intermediate
loads, so loading condition 1 is used.
The four load cases for combined loading is then checked using 
checkBeamColumnCombined - it's that easy! 
Note everything after this sections is for educational purposes only.
"""
loadingCondition = s16.Omega1LoadConditions.noLoads
omega1x = s16.getOmega1(loadingCondition, Mfx_top, Mfx_bottom)
u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
                                omegax1=omega1x, isBracedFrame = True)


"""
While the user will often default to using the checkBeamColumnCombined, for 
educational purposes it will be shown how to determine each of the four checks
run on the beamcolumn. 

The first check is total section strength, which looks at the strength of 
elements without any stability checks (13.8.2 a). This check ensures that
the cross section can withstand forces applied to it at any point on the beam,
and as such reducing omega factors are not considered.
The supported member strength is calculated, and the member strength is 
calculatd with lambda = 0. This means that buckling is not considered, and 
the compression strength is equal the sections gross yield strength.

The euler buckling capacity for the element is calculated, this will be used
later in equations. U1x is also calculated given the load factor (omega1x) 
that was calculated earlier.

"""

n = 1.34
Mrx = s16.checkBeamMrSupported(beamColumn, True, Cf)
Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
Cex = s16.checkColumnCeDirection(beamColumn, True)

U1x = max(s16.getU1(omega1x, Cf, Cex),1)
u1a  = Cf/Cr + 0.85*U1x*Mfx/Mrx

"""
limitstates also has a function to calculate u1 combined. 
"""
u1b = s16.checkCombinedCaseA(beamColumn, Cf, Mfx, 0, n, omega1=omega1x)

"""
The second case, B, is used to assess the overal member strength, which can
be thought of as the members "primary" axis bending strength. The in-plane
strength of the member is checked alone in the axis of bending.

This check will govern for large members that have intermediate lateral 
bracing which prevents torsion, but do not prevent bending.

Some notes; because buckling is considered in case B, the compression 
resistance Crb will always be smaller than check Cra. However, the moment 
utilization can be smaller than check A, because the term U1 will account for
moment gradient.

In this case, U1x is taken as 1 because the system is a brace frame. 
CSA S16 sets U1x = 1 because P-delta effects are considered to be small in sway 
frames, where the peak moment normally occurs at column.

In limitstates, in-plane behaviour is forced by artificially modifying the 
stiffness k factor.
"""

# Find the compression strength of the column about it's strong axis only.
beamColumn.designProps.setkz(0.0001)
beamColumn.designProps.setky(0.0001)
Cr  = s16.checkColumnCr(beamColumn)

# Calculate the supported Moment
Mrx = s16.checkBeamMrSupported(beamColumn, True, Cf)
U1x = s16.getU1(omega1x, Cf, Cex)

# Reset support factors
beamColumn.designProps.setkz(1)
beamColumn.designProps.setky(1)

u2a  = Cf/Cr + 0.85*U1x*Mfx/Mrx

"""
limitstates also has a function to calculate in-plane strength of the member
"""
u2b = s16.checkCombinedCaseB(beamColumn, Cf, Mfx, 0, n, omega1=omega1x, 
                             isBracedFrame=True)


"""
The next check is lateral torsional buckling. For beams that aren't braced, 
this check will almost always govern. The member is allowed to buckle in 
lateral torsion, and the unsupported member strength is used for bending.
"""
Cr = s16.checkColumnCr(beamColumn)
Mrx = s16.checkBeamMrUnsupported(beamColumn, True, Cf = Cf)

U1x = max(s16.getU1(omega1x, Cf, Cex),1)

u3a  = Cf/Cr + 0.85*U1x*Mfx/Mrx
u3b = s16.checkCombinedCaseC(beamColumn, Cf, Mfx, 0, n, omega1=omega1x)

"""
The final check is biaxial bending, which will be neglected because the member
only has bending in one axis.
"""










