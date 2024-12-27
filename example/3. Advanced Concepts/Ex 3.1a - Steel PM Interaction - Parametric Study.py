"""
This example runs a parametric study on a series of steel beam columns, with
the goal of finding out when each set of checks (cross section strength, 
overal member strength, lateral torsional buckling) governs. 

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

from parametricHelpers import getParametricPlot, runParametericAnalysis

# Set up the material.
mat = s16.MaterialSteelCsa24(345)

# Get a set of members by name.
steelWSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
sectionsW310 = ls.filterByName(steelWSections, 'W310')
sectionsW460 = ls.filterByName(steelWSections, 'W460')

steelHssSections  = ls.getSteelSections(mat, 'csa', 'cisc_12', 'hss')
sectionsHss = ls.filterByName(steelHssSections, '254')


# =============================================================================
# Inputs
# =============================================================================

# Define a set of inputs x*Cy, y*Mf, kx, ω1
inputDict = {'High P':                       [0.8, 0.2, 1.0, 1],
             'Balanced':                     [0.5, 0.5, 1.0, 1],
             'High M':                       [0.2, 0.8, 1.0, 1],
             'High P, ${ω_1}$=0.4':          [0.8, 0.2, 1.0, 0.4],
             'Balanced, ${ω_1}$=0.4':        [0.5, 0.5, 1.0, 0.4],
             'High M, ${ω_1}$=0.4':          [0.2, 0.8, 1.0, 0.4],
             'High P, k=0.5':                [0.8, 0.2, 0.5, 1],
             'Balanced, k=0.5':              [0.5, 0.5, 0.5, 1],
             'High M, k=0.5':                [0.2, 0.8, 0.5, 1],
             'High P, ${ω_1}$=0.4, k=0.5':   [0.8, 0.2, 0.5, 0.4],
             'Balanced, ${ω_1}$=0.4, k=0.5': [0.5, 0.5, 0.5, 0.4],
             'High M, ${ω_1}$=0.4, k=0.5':   [0.2, 0.8, 0.5, 0.4]}

# The lengths to use in the analysis.
lengths = [3, 5, 7, 9, 11, 13, 15]

# set up the sections to run the analysis on.
sections = [sectionsW310[1], sectionsW310[11], 
            sectionsW460[1], sectionsW460[12],
            sectionsHss[0], sectionsHss[-12], sectionsHss[-3]]
labels = list(inputDict.keys())

# =============================================================================
# Analysis
# =============================================================================

for sec in sections:
    
    # Run the analysis
    govCases, govUts, slender = runParametericAnalysis(sec, lengths, inputDict)
    
    # Create the plot using the outputs
    fig, ax = getParametricPlot(sec, slender, labels, govCases, govUts)
    
