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
sectionsFiltered = ls.filterByName(steelHssSections, '254x254')
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
    MpSup = s16.checkBeamMrUnsupported(beamColumn, omega2)

    Mout.append(MpSup / M0)
    slendernesses.append(slenderness)
    Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
    Cf = Cr*0.35

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
             'highCompression_TorsionBracing':   [0.5, 0.5, 0.5, 1],
             'mediumCompression_TorsionBracing': [0.35, 0.5, 0.5, 1],
             'lowCompression_TorsionBracing':    [0.2, 0.8, 0.5, 1]}



labels = ['0.5Cr, 0.5Mr, k = 1, ω = 1', '0.35Cr, 0.65Mr, k = 1, ω = 1', '0.2Cr, 0.8Mr, k = 1, ω = 1',
          '0.5Cr, 0.5Mr, k = 1, ω = 0.4', '0.35Cr, 0.65Mr, k = 1, ω = 0.4', '0.2Cr, 0.8Mr, k = 1, ω = 0.4',
          '0.5Cr, 0.5Mr, k = 0.5, ω = 1', '0.35Cr, 0.65Mr, k = 0.5, ω = 1', '0.2Cr, 0.8Mr, k = 0.5, ω = 1']

labels = ['0.5Cr, 0.5Mr, k = 1, ω = 1', '0.35Cr, 0.65Mr, k = 1, ω = 1', '0.2Cr, 0.8Mr, k = 1, ω = 1',
          '0.5Cr, 0.5Mr, k = 1, ω = 0.4', '0.35Cr, 0.65Mr, k = 1, ω = 0.4', '0.2Cr, 0.8Mr, k = 1, ω = 0.4',
          '0.5Cr, 0.5Mr, k = 0.5, ω = 1', '0.35Cr, 0.65Mr, k = 0.5, ω = 1', '0.2Cr, 0.8Mr, k = 0.5, ω = 1']




lengths = [4, 6, 8, 10, 12, 14, 16]
lengths = [3, 5, 7, 9, 11, 13, 15]

# 4 = no case governs

# section = sectionsW460[13]
# section = sectionsFiltered[0]
for section in steelHssSections:
    governingCases = []
    governingUts = []
    ii=0
    for key in inputDict:
            
        cratio, Mratio, kx, omegax1 = inputDict[key]
        
        trialGoverningCases = []
        trialGoverningUts = []
        slendernesses = []
        for L in lengths:
    
            beamColumn  = s16.getBeamColumnSteelCsa24(L, section, kx = kx)
            # print(section.rx)
            slenderness = s16.checkElementSlenderness(beamColumn, False)
        
            Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
            Crslender = s16.checkColumnCr(beamColumn)
            Crslender = s16.checkColumnCeDirection(beamColumn, True)
            Cf = Cr*cratio
            
            # if 1 <= (Cf / Crslender):
            #     trialGoverningCases.append(4)
            #     trialGoverningUts.append(None)
            #     slendernesses.append(slenderness)
            #     continue
            
            
            Mp = s16.checkBeamMrSupported(beamColumn, omegax1, Cf=Cf)
            MpSup = s16.checkBeamMrUnsupported(beamColumn, omegax1, Cf=Cf)
            Mfx = Mp*Mratio
            # if 1 <= (Mfx / MpSup):
            #     trialGoverningCases.append(5)
            #     trialGoverningUts.append(None)
            #     slendernesses.append(slenderness)
            #     continue
            
            # u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
            #                                 omegax1=omega1x)            
            
            u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
                                            omegax1=omegax1, isBracedFrame = True)          
            # try:
            #     Mp = s16.checkBeamMrSupported(beamColumn, omega1x, Cf=Cf)
            # except:
            #     Mp = 0
            # Mfx = Mp*0.5
            # print(Mfx)
                
            # try:
            #     u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
            #                                     omegax1=omega1x, isBracedFrame = True)
            #     u = list(u)
            # except:
            #     u = [0,0,0,0]
            u = u[:3]
            print(u)
            
            ind = np.argmax(u)
            ut = np.max(u)
            utmin = np.min(u)
            if utmin <0:
                print(ii)
            
            inds = np.where(u == ut)[0]
            
            # trialGoverningCases.append(inds)
            trialGoverningCases.append(ind)
            trialGoverningUts.append(round(ut,2))
            slendernesses.append(slenderness)
        print()
    
    
        governingCases.append(trialGoverningCases)
        governingUts.append(trialGoverningUts)
    
    
    
    
    titles = list(inputDict.keys())
    slendernesses = list(slendernesses)
    slendernesses = [round(x,1) for x in slendernesses]
    
    governingUts = np.round(governingUts, 1)
    
    print(governingCases)
    governingCases = np.array(governingCases)
    
    
    fig, ax = plt.subplots()
    im = ax.imshow(governingCases)
    
    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(slendernesses)), labels=slendernesses)
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations.
    for i in range(len(labels)):
        for j in range(len(slendernesses)):
            if governingUts[i, j] < 10:
                text = ax.text(j, i, governingCases[i, j],
                               ha="center", va="center", color="w")
    
    ax.set_title("Governing Check")
    fig.tight_layout()
    plt.show()
    








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



