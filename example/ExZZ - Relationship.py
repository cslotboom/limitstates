"""
Tests if the unit library is working correctly.
"""

import limitstates as ls
import limitstates.design.csa.o86.c19 as csa

O1 = ls.slab
O2 = ls.beam

mysystem = ls.DesignSystem(O1, O2)