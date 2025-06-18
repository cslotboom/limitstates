# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 19:45:05 2025

@author: Christian
"""

from limitstates import Rebar
import limitstates.design.csa.a23.c24 as c24
from time import time
from copy import deepcopy

N = int(1e5)
fy = 400
matRebar = c24.MaterialRebarCSA24(fy)

{}


testRebar = Rebar(matRebar, '30M', 30, 31, 700, 'mm')

t1 = time()
for ii in range(N):
     newRebar = deepcopy(testRebar)
t2 = time()

for ii in range(N):
     newRebar = Rebar(matRebar, '30M', 30, 31, 700, 'mm')

t3 = time()


print('New Variable', t3 - t2)
print('Copy', t2 - t1)