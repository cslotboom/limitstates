"""
This example runs a parametric study on a series of steel beam columns, with
the goal of finding out when each set of checks (cross section strength, 
overal member strength, lateral torsional buckling) governs. 

For a set of loading conditions, what is most likely to govern

First the base library is imported, along wtih the CSA s16 2024 steel library.
The section to be checked is defined, and loaded. The demands on the section
are also checked.

Note, if the beam was in positive curvature, then the moments would have 
opposite signs.
"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

from parametricHelpers import getParametricPlot, runParametericAnalysis

import matplotlib.pyplot as plt
import numpy as np

# Get a set of members by name.
mat = s16.MaterialSteelCsa24(345)
steelWSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
sectionsW460 = ls.filterByName(steelWSections, 'W460')

# # Get the 'column' class 460 setionssections. Sections bigger than this value
# # have a wide flange and are intended for bending
# sectionsFiltered = ls.filterByAttrRange(sectionsFiltered, 'W', lowerLim = 106)

steelHssSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'hss')
sectionsFiltered = ls.filterByName(steelHssSections, '254')
# sectionsFiltered += ls.filterByName(steelWSections, '203x203')
sectionsFiltered = ls.filterByAttrRange(sectionsFiltered, 't', lowerLim = 7)






# =============================================================================
# 
# =============================================================================


section = sectionsW460[1]

lengths = np.linspace(0,1,51)*45
omega2 = 1


beamColumn  = s16.getBeamColumnSteelCsa24(1, section)     
M0 = s16.checkBeamMrSupported(beamColumn, omega2)
# MpSup = s16.checkBeamMrUnsupported(beamColumn, omega1x)

fix, ax =  plt.subplots()

slendernesses = []
Mout = []
for L in lengths[1:]:

    beamColumn  = s16.getBeamColumnSteelCsa24(L, section)
    slenderness = s16.checkElementSlenderness(beamColumn)
    Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
    Cf = Cr*0.85

    MpSup = s16.checkBeamMrUnsupported(beamColumn, omega2,Cf=Cf)

    Mout.append(MpSup / M0)
    slendernesses.append(slenderness)


    # u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, isBracedFrame = True)    



ax.plot(slendernesses, Mout)
ax.set_ylim([0,1.1])
plt.show()



# =============================================================================
# 
# =============================================================================


inputDict = {'highCompression':  [0.5,  0.5,  1, 1],
             'MediumCompression':[0.35, 0.65, 1, 1],
             'lowCompression':   [0.2,  0.8,  1, 1],
             'highCompression_lowOmega':  [0.5,  0.5,  1, 0.4],
             'MediumCompression_lowOmega':[0.35, 0.65, 1, 0.4],
             'lowCompression_lowOmega':   [0.2,  0.8,  1, 0.4],
             'highCompression_TorsionBracing':   [0.5, 0.5, 0.2, 1],
             'mediumCompression_TorsionBracing': [0.35, 0.5, 0.2, 1],
             'lowCompression_TorsionBracing':    [0.2, 0.8, 0.2, 1]}

# labels = ['0.5Cr, 0.5Mr, k = 1, ω = 1', '0.35Cr, 0.65Mr, k = 1, ω = 1', '0.2Cr, 0.8Mr, k = 1, ω = 1',
#           '0.5Cr, 0.5Mr, k = 1, ω = 0.4', '0.35Cr, 0.65Mr, k = 1, ω = 0.4', '0.2Cr, 0.8Mr, k = 1, ω = 0.4',
#           '0.5Cr, 0.5Mr, k = 0.5, ω = 1', '0.35Cr, 0.65Mr, k = 0.5, ω = 1', '0.2Cr, 0.8Mr, k = 0.5, ω = 1']



labels = ['High P', 'Balanced', 'High M',
          'High P, ω2=0.4', 'Balanced, ω2=0.4', 'High M, ω2=0.4',
          'High P, k=0.5', 'Balanced, k=0.5', 'High M, k=0.5']

lengths = [3, 5, 7, 9, 11, 13, 15]

# 4 = no case governs



wSections = [sectionsW460[1], sectionsW460[12]]
for section in wSections:
   
    # titles = list(inputDict.keys())

    
    govCases, govUts, slendernesses = runParametericAnalysis(section, lengths)
    slendernesses = list(slendernesses)
    slendernesses = [round(x,1) for x in slendernesses]
    
    # col = s16.getBeamColumnSteelCsa24(1, section)
    fig, ax = getParametricPlot(section, slendernesses, labels, govCases, govUts)
    






# =============================================================================
# 
# =============================================================================

# L = 5
# omega1x = 1
# kx = 1
# # dProps = s16.DesignPropsSteel24(kx = 0.5)

# slenderness = []

# uOut = []
# WOut = []
# tOut = []
# for section in sectionsFiltered:

#     beamColumn  = s16.getBeamColumnSteelCsa24(L, section, kx = kx)
#     # print(section.rx)
#     # print(s16.checkElementSlenderness(beamColumn))

#     Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
#     Crslender  = s16.checkColumnCr(beamColumn)
#     Cf = Cr*0.5
    
#     if 1 <= (Cf / Crslender):
        
#         continue
    
    
#     try:
#         Mp = s16.checkBeamMrUnsupported(beamColumn, omega1x, Cf=Cf)
#     except:
#         Mp = 0
#     Mfx = Mp*0.5
#     print(Mfx)
        
#     try:
#         u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
#                                         omegax1=omega1x, isBracedFrame = False)
#         u = list(u)
#     except:
#         u = [0,0,0,0]
#     uOut.append(u)
#     WOut.append(section.W)
#     tOut.append(section.t)


# uOut = np.array(uOut)
# uOut = np.array(uOut)
# tOut = np.array(tOut)

# fix, ax =  plt.subplots()
# ax.plot(tOut, uOut[:,:3])
# ax.set_ylim([0,5])
# plt.show()




