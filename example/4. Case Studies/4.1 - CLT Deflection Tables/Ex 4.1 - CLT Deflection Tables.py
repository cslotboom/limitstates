"""
CLT panels often have significant shear deflection because of shear deformation
in their cross layers. There are some reasources that exist for single span
clt, however, CLT is often used in multi-span conditions.

In this design example, a parametric study are run on a series of clt panels, 
and the outputs are used to create span tables. The parametric study evaluates
shear by analyzing each panel as both a Euler beam, and timoshenko beam.
Note that many helper functions are used from in the "parametricHelper" file, 
which has documentation for each function.

Also note that the actual pdf design reasource was created manually, using the
.csv outputs from this study.
"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as c19
import parametricHelpers as ph

# =============================================================================
# PRG panels
# =============================================================================

"""
The first portion of the analysis creates the deflection tables for PRG-320 SPF 
sections. This is used to make the PRG deflection tables.
Initially sections are loaded using section databases, then a set of spans and 
span lengths are set up.
 
"""

sections    = c19.loadCltSections()
E1Sections  = ls.filterByName(sections, 'E1')
V2Sections  = ls.filterByName(sections, 'V2')

spfCLT = E1Sections + V2Sections
Nspans = [1, 2, 3]
Lspans = [2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5]

outPuts = {}
for panel in spfCLT:
    EI = panel.getEIs()
    GA = panel.getGAs()
    
    u = ph.runAllAnalysesPanel(Nspans, Lspans, panel)
    outPuts[panel.name] = ph.postProcessAnalysis(u)

ph.saveToFile(outPuts, Lspans, ind=1, baseName='prg')


# =============================================================================
# Make The deflection modifcation tables
# =============================================================================
"""
An analysis is run on a arbitary set of CLT panels, where the ratio of EI/GA
is described in the ratio variable.
"""

EI0 = 8e6
ratios = [0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
outPutsRatio = {}

for r in ratios:
    GA = EI0 /r    
    u = ph.runAllAnalyses(Nspans, Lspans, EI0, GA)
    outPutsRatio[r] = ph.postProcessAnalysis(u)

ph.saveToFile(outPutsRatio, Lspans, ind=3, baseName='modification')

# =============================================================================
# Make some figures that will go along with the tables
# =============================================================================

L = 5
Nspans = [1,2,3]

for Nspan in Nspans:
    fig, ax = ph.getBeamPlot(Nspan, L, V2Sections[1])

