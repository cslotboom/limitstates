"""
Tests if the unit library is working correctly.
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

mm = 0.001
m = 1
MPa = 1
width = 356
depth = 600
Length = 6*m


# =============================================================================
# Manually create elements
# =============================================================================
# Define Element
matDict = {'E':9500*MPa, 'fb':25*MPa}
myMat       = csa.MaterialGlulamCSA19(matDict)
mySection   = ls.SectionRectangle(myMat, width, depth)   
myElement   = ls.getBeamColumn(Length, mySection, 'm')
# myGlulamEle = ls.BeamColumnGlulamCSA19(myElement)

firePortection = csa.GypusmRectangleCSA19('12.7mm')
myElement.designProps.firePortection = firePortection
# Mr = myGlulamEle


# =============================================================================
# Create elements using code functions
# =============================================================================

"""
The easiest way to, is to 
"""

myMat = csa.loadGlulamMaterial('SPF', '20f-E')
mySection   = ls.SectionRectangle(myMat, width, depth)   
myElement = csa.getBeamColumnGlulamCSA19(Length, mySection, 'm')

# section = code.getGlulamSection('matString', width, depth)
# designElement = csa.getGlulamElement(Length, section)

# Mr = csa.getGlulamMr(designElement)



# =============================================================================
# Annex D calculations
# =============================================================================

myMat = csa.loadGlulamMaterial('SPF', '20f-E')
mySection   = ls.SectionRectangle(myMat, width, depth)   
myElement = csa.getBeamColumnGlulamCSA19(Length, mySection, 'm')

FRR         = csa.getFireDemands(60, csa.FireConditions.beamColumn)
gypsum      = csa.getGypsumFirePortection(csa.FireConditions.beamColumn, "12.7mm")

fireSection = myElement.designProps.fireSection


# =============================================================================
# 
# =============================================================================


# import limitstats as ls

# E = 9.5
# G = E/16

# myMat = ls.MatElastic(E, G)
# mySection = ls.SectionRectangle(width, depth, myMat)
# myElement = ls.BeamColumn(Length, mySection)