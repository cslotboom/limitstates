"""
This example runs a parametric study on a series of steel beam columns, with
the goal of finding out when each set of checks (cross section strength, 
overal member strength, lateral torsional buckling) governs. 

First the base library is imported, along wtih the CSA s16 2024 steel library.
The section to be checked is defined, and loaded. The demands on the section
are also checked.

Note, if the beam was in positive curvature, then the moments would have 
opposite signs.
"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16

import matplotlib.pyplot as plt
import numpy as np

# Get a set of members by name.
mat = s16.MaterialSteelCsa24(345)
# steelWSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'w')
# sectionsFiltered = ls.filterByName(steelWSections, 'W460')

# # Get the 'column' class 460 setionssections. Sections bigger than this value
# # have a wide flange and are intended for bending
# sectionsFiltered = ls.filterByAttrRange(sectionsFiltered, 'W', lowerLim = 106)

steelWSections   = ls.getSteelSections(mat, 'csa', 'cisc_12', 'hss')
sectionsFiltered = ls.filterByName(steelWSections, '254x254')
sectionsFiltered = ls.filterByAttrRange(sectionsFiltered, 't', lowerLim = 7)

# =============================================================================
# 
# =============================================================================

L   = 8
omega1x = 1
kx = 0.5
# dProps = s16.DesignPropsSteel24(kx = 0.5)


uOut = []
WOut = []
tOut = []
for section in sectionsFiltered:

    beamColumn  = s16.getBeamColumnSteelCsa24(L, section, kx = kx)
    Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
    Cf = Cr*0.2
    try:
        Mp = s16.checkBeamMrSupported(beamColumn, omega1x, Cf=Cf)
    except:
        Mp = 0
    Mfx = Mp*0.3
    print(Mfx)
        
    try:
        u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
                                        omegax1=omega1x, isBracedFrame = True)
        u = list(u)
    except:
        u = [0,0,0,0]
    uOut.append(u)
    WOut.append(section.W)
    tOut.append(section.t)


uOut = np.array(uOut)
uOut = np.array(uOut)
tOut = np.array(tOut)

fix, ax =  plt.subplots()
ax.plot(tOut, uOut[:,:3])
ax.set_ylim([0,2])
plt.show()




# =============================================================================
# 
# =============================================================================

# # cLevels = [0.3, 0.5, 0.7]
# # lengths = [3, 6, 9]
# # omega = [0.4]
# # Fy  = 345
# # Cf  = 4400*kN
# # Mfx_top = 500*kN
# # Mfx_bottom = 400*kN
# # Mfx = Mfx_top

# uOut = []
# IOut = []
# dOut = []
# # sections = 

# # ls.filterByAttrRange(objectList, attr)
# # Cf = 2000*kN
# # Mfx = 300*kN
# # Mfy = 300*kN
# for section in steelWSections:
# # for section in steelWSections[11:15]:
# # for section in steelWSections[150:200]:
# # for section in steelWSections[25:100]:
    
    
    
#     omega1x = 1
#     beamColumn  = s16.getBeamColumnSteelCsa24(L, section)

#     Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
#     Cf = Cr*0.5
#     try:
#         Mp = s16.checkBeamMrUnsupported(beamColumn, omega1x, Cf=Cf)
#         # Mp = s16.checkBeamMrSupported(beamColumn, omega1x, Cf=Cf)
#     except:
#         Mp = 0
#     # Mp = s16.checkBeamMrSupported(beamColumn, omega1x, Cf)
#     Mfx = Mp*0.2
    

#     loadingCondition = s16.Omega1LoadConditions.noLoads
#     try:
#         u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
#                                         omegax1=omega1x, isBracedFrame = True)
#         u = list(u)
#     except:
#         u = [0,0,0,0]
    
#     L
#     rx = section.rx *1e-3
#     uOut.append(u)
#     IOut.append(L/rx)
#     dOut.append(section.d)
#     section.name
#     # except:
#     #     pass


# uOut = np.array(uOut)

# IOut = np.array(IOut)
# inds = np.where(uOut[:,0] != 0)
# Iout = IOut[inds]
# dOut = np.array(dOut)[inds]
# uOut = uOut[inds,:][0]

# fix, ax =  plt.subplots()

# # ax.plot(uOut[:,0])
# # ax.plot(uOut[:,1])
# # ax.plot(Iout, uOut[:,2])
# # ax.plot(IOut, uOut[:,3] ,'.')
# ax.plot(uOut[:,:2])
# # ax.plot(dOut, uOut[:,2])
# plt.show()



