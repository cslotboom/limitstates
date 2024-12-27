"""
Functions that aid with running the analysis shown in 3.1

"""
import limitstates as ls
import limitstates.design.csa.s16.c24 as s16
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

# Set the matplotlib parameters so that subscript can be easily added.
params = {'mathtext.default': 'regular' }          
plt.rcParams.update(params)
# =============================================================================
# 
# =============================================================================

def _getOutputText(governingCase):
    hasDecimal = (governingCase * 10 % 10) != 0
    if hasDecimal:
        return '/'.join(str(governingCase).split('.'))
    else:
        return int(governingCase)


def getParametricPlot(section, slendernesses, labels, governingCases, governingUts):
    """
    A helper function to create the parameteric plot.
    """
        
    Nanalysis = len(labels)
    Nxvalues = len(slendernesses)
    
    # set up the base plot with two subplots
    fig, ax = plt.subplots(ncols = 2)
    
    # Define a norm and create an image
    Ncase = 6
    norm = Normalize(vmin=0, vmax=Ncase, clip=False)
    _ = ax[0].imshow(governingCases, norm = norm)
    
    # Show all ticks and label them with the respective list entries
    ax[0].set_xticks(np.arange(len(slendernesses)), labels=slendernesses)
    ax[0].set_yticks(np.arange(len(labels)), labels=labels)
    
    # Rotate the tick labels and set their alignment.
    plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    # Loop over each analysis and create text annotations in each cell.
    for ii in range(Nanalysis):
        for jj in range(Nxvalues):

            # If the force applied is greater than the , 
            # utilization will be very large
            if governingUts[ii, jj] < 10:
                text = _getOutputText(governingCases[ii, jj])
                ax[0].text(jj, ii, text, ha="center", va="center", color="w")

    # Plot the section
    _, ax2 = ls.plotSection(section, ax = ax[1])

    
    # Set the title for the section
    name = section.name.split(' ')[0]
    ax[1].set_title(name)
    
    # set up teh title the check plot, and some labels.
    ax[0].set_title("Governing Check")
    ax[0].set_xlabel("Slenderness Ratio")
    
    plt.show()
    return fig, ax

def runParametericAnalysis(section, lengths, inputDict):
    """
    Run the analysis on each section in the input dictionary.
    """
    
    # initialize the variables
    governingCases = []
    governingUts   = []
    
    # Iterate through each analysis input
    for key in inputDict:
        
        # Extract the input values
        cratio, Mratio, kx, omegax1 = inputDict[key]
        
        # Initialize containing variables for each input
        trialGoverningCases = []
        trialGoverningUts   = []
        slendernesses       = []
        
        # A number of different slenderness conditions are checked by using 
        # differnt lengths
        for L in lengths:
            
            # create the beam column using the input variables.
            # It's assumed the brace point will brace both axes.
            beamColumn = s16.getBeamColumnSteelCsa24(L, section, 
                                                     kx = kx, ky = kx)
            
            # Calcualte teh slenderness ratio for the beam
            slenderness = s16.checkElementSlenderness(beamColumn, False)
        
            # Calcualte the initial applied loads.
            Cr  = s16.checkColumnCr(beamColumn,  lam = 0)
            Cf  = Cr*cratio
            Mp  = s16.checkBeamMrSupported(beamColumn, Cf=Cf)
            Mfx = Mp*Mratio
            
            # Get the output utilizations.
            u = s16.checkBeamColumnCombined(beamColumn, Cf, Mfx, 
                                            omegax1 = omegax1, 
                                            isBracedFrame = True)          

            # skip the case 3 check
            u = u[:3]
            
            # Get the governign load combineation
            ind = np.argmax(u)
            ut = np.max(u)
            
            # find if there are any ties. If there are skip them
            inds = np.where(np.abs(u - ut) < 0.01)[0]
            if len(inds) >=2:
                # print(inds)
                ind = min(inds) + max(inds)/10 +0.1
            
            # set the outputs
            trialGoverningCases.append(ind)
            trialGoverningUts.append(round(ut,2))
            slendernesses.append(slenderness)
        
        # Set the output lists for each trial group.
        governingCases.append(trialGoverningCases)
        governingUts.append(trialGoverningUts)

    # Get the final outputs, and 
    governingCases = np.array(governingCases) + 1
    governingUts  = np.round(governingUts, 1)
    
    # remove cases where
    slendernessFailsInds = np.where(10<governingUts)
    
    governingCases[slendernessFailsInds] = 6

    slendernesses = list(slendernesses)
    slendernesses = [round(x,1) for x in slendernesses]


    return governingCases, governingUts, slendernesses




