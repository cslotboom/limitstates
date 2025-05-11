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
sectionsW310 = ls.filterByName(steelWSections, 'W360')

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


trialGoverningCases = []
slendernesses = []
# cratio, Mratio, kx, omegax1 = inputDict['highCompression']

kx = 1

Fout = []
dictOut = {}
for section in steelWSections:
    name = section.EDI_Std_Nomenclature
    dictOut[name] = {}
    for L in lengths:
        # create the beam column using the input variables.
        # It's assumed the brace point will brace both axes.
        beamColumn = s16.getBeamColumnSteelCsa24(L, section, kx = kx, ky = kx)
        slenderness = s16.checkElementSlenderness(beamColumn)

        Fex = s16.checkColumnFeDirection(beamColumn)
        Fey = s16.checkColumnFeDirection(beamColumn, False)
        Fez = s16.checkColumnFeTorsion(beamColumn)     
    
        
        # skip the case 3 check
        F = [round(Fex), round(Fey), round(Fez)]
        Fout.append(F)
        
        # Get the governign load combineation
        ind = np.argmin(F)
        Fe  = np.min(F)
        
            
        if ind == 2:
            pass
        
        # lam = (Fy/Fe)**0.5

        
        # find if there are any ties. If there are skip them
        # inds = np.where(np.abs(u - ut) < 0.01)[0]
        # if len(inds) >=2:
        #     # print(inds)
        #     ind = min(inds) + max(inds)/10 +0.1
        dictOut[name][L] = F
        dictOut[name]['A'] = section.A

        # set the outputs
        trialGoverningCases.append(ind)
        slendernesses.append(slenderness)

