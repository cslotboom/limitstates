"""
Tests if the unit library is working correctly.
"""

import limitstats as ls

mm = 0.001
m = 1
width = 356*mm
depth = 600*mm

Length = 6*m

# Define Element
myMat       = ls.MatGlulamCSA19()
mySection   = ls.SectionRectangle(width, depth, myMat)
myElement   = ls.BeamColumn(Length, mySection)
myGlulamEle = ls.BeamColumnGlulamCSA19(myElement)


Mr = myGlulamEle


# =============================================================================
# 
# =============================================================================

import limitstates.design.code.csa.o86.c19 as code

mat = code.getGlulamMat('matString')
section = code.getGlulamSection('matString', width, depth)
designElement = code.getGlulamElement(Length, section)




# =============================================================================
# 
# =============================================================================


import limitstats as ls

E = 9.5
G = E/16

myMat = ls.MatElastic(E, G)
mySection = ls.SectionRectangle(width, depth, myMat)
myElement = ls.BeamColumn(Length, mySection)