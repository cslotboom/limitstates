"""
An example showing how CLT elements can be manually defined, or imported from
section libraries.
"""


import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

mm = 0.001
m = 1
MPa = 1
# Length = 6*m


# =============================================================================
# Import sections using a design library
# =============================================================================

"""
The easiest way to load sections, is to use functions that load them directly
from the design libary..
"""

mySections = csa.loadCltSections()

# =============================================================================
# Manually create elements
# =============================================================================

"""
We could also define our elements directly from first priciples.
"""
# We define some elements using elastic materials.
Es = 11700*MPa
Gs = 731*MPa
myMatS = ls.MaterialElastic(Es, Gs)
myMatS.E90 = Es/30
myMatS.G90 = Gs/13
myMatS.fb = 28*MPa
myMatS.grade = 'strong axis'

Ew = 9000
Gw = 731
myMatW = ls.MaterialElastic(Es, Gs)
myMatW.E90 = Ew/30
myMatW.G90 = Gw/13
myMatS.fb = 11*MPa
myMatW.grade = 'weak axis'

# t = 35
layer1 = ls.LayerClt(35, myMatS)
layer2 = ls.LayerClt(35, myMatW, False)
layer3 = ls.LayerClt(20, myMatS)

layerGroup = ls.LayerGroupClt([layer1, layer1, layer2, layer1, layer3])

