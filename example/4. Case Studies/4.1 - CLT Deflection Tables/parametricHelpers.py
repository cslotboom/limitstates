"""
Functions that aid with running the analysis shown in 3.1

"""
import pandas as pd
import planesections as ps
import numpy as np
import limitstates.design.csa.o86.c19 as c19


def runAllAnalysesPanel(Nspans:list[int], lengths:list[float], 
                        panel:c19.BeamColumnCltCsa19):
    """
    Runs a parametric analysis for the input number of spans and lengths
    for input panel.

    Parameters
    ----------
    Nspans : list[int]
        The list of span configurations to check.
    lengths : list[float]
        The list of span lengths to check.
    panel : BeamColumnCltCsa19
        The panel to use in the analysis.

    Returns
    -------
    uout : list[tuple]
        A list of deflections for a regular and timoshenko beam.

    """
    
    
    uout = {}
    for Nspan in Nspans:
        if Nspan not in uout:
            uout[Nspan] = []
        for L in lengths:
            uout[Nspan].append(runCLTAnalysisPanel(L, Nspan, panel))
            # uout.append(runCLTAnalysisPanel(L, Nspan, section))
            
    return uout


def runAllAnalyses(Nspans:list[int], lengths:list[float], EI:float, GA:float):
    """
    Runs a parametric analysis for a panel that uses the input EI and GA value.

    Parameters
    ----------
    Nspans : list[int]
        The list of span configurations to check.
    lengths : list[float]
        The list of span lengths to check.
    EI : float
        The EI for the panel. Units must be in a consistent set of units for 
        FEM that are also compatible with the length unit.
    GA : float
        The GA for the panel. Units must be in a consistent set of units for 
        FEM that are also compatible with the length unit.
        
    Returns
    -------
    uout : list[tuple]
        A list of deflections for a regular and timoshenko beam.

    """
    
    
    uout = {}
    for Nspan in Nspans:
        if Nspan not in uout:
            uout[Nspan] = []
        for L in lengths:
            uout[Nspan].append(runCLTAnalysis(L, Nspan, EI, GA))            
    return uout



def postProcessAnalysis(u:dict)->dict:
    """
    Post process the results by finding the shear deflection, flexure 
    deflection for the panel. Also returned is the percent shear is of total
    deflection, and how much deflection is increased by shear.

    Parameters
    ----------
    u : dict
        The input deflection, in the form of deflection[span] = list[(x1,x2)].

    Returns
    -------
    uOut : dict
        The output defection results, in the form:
            [[uShear1, uFlex1, shearPercent1, increaseFactor1],
             [uShear2, uFlex2, shearPercent2, increaseFactor2],...,]

    """

    uOut = {}
    
    for span in u:
        uTrial = u[span]
        uShear =  [item[0] - item[1] for item in uTrial]
        uFlex  =  [item[1] for item in uTrial]
   
    
        uShear = np.array(np.abs(uShear))
        uFlex  = np.array(np.abs(uFlex))
        
        shearPercent = uShear / (uShear + uFlex)
        increaseFactor = (uShear + uFlex) / uFlex
        
        uOut[span] = (uShear, uFlex, shearPercent, increaseFactor)

    return uOut




def saveToFile(u:dict, lengths:list[float], ind = 3, baseName = 'prg', ):
    """
    Inputs have form: 
        {panelType1: {span1: {r1, r2, r3, r4}, ...},
         panelType2: ....,} where 
        ri is a result for each length
    
    Outputs have the form:
        {span: {length: {r1, r2, r3, r4}}}, where 


    Parameters
    ----------
    u : dict
        The input postprocessed deflection file.
    lengths : list[float]
        A list of lengths.
    ind : int
        The index of the result to use.
        
    baseName : str
        The base name of the output file. A result is generated for each 
        span number
        

    Returns
    -------
    None.

    """
        

    uout = {}
    panelTypes = list(u.keys())
    
    for panelType in u:
        uSpan = u[panelType]
        
        for span in uSpan.keys():
            uLength = uSpan[span]
            
            # Intialize uout at the input span.
            if span not in uout:
                uout[span] = {}
                
            ii = 0
            for L in lengths:
                # Intialize uout at the input length.
                if L not in uout[span]:
                    uout[span][L] = []
                
                uout[span][L].append(uLength[ind][ii])
                ii+=1
            
            # uout[span][panelType] = 
    # Save rsults sorted by span.
    for span in uout:
        dictSpan = uout[span]
        df = pd.DataFrame(dictSpan, columns = lengths)
        df.index = panelTypes
        df.to_csv(f'{baseName}_{span}.csv')



def runCLTAnalysisPanel(L, Nspan, section):
    """
    Runs a CLT panel analysis, where the beam is analyzed as a timoshenko
    beam and euler beam, and returns the deflection for each.

    Units must be in a consistent set of units for FEM that are compatible 
    with the length unit.

    Parameters
    ----------
    L : TYPE
        THe length of the span.
    Nspan : TYPE
        The number of spans.
    section : TYPE
        THe CLT section used.


    Returns
    -------
    umaxTim : float
        The deflection of the beam as a timoshenko beam.
    umaxEul : float
        The deflection of the beam as a Euler beam.
    """

    EI = section.getEIs()
    GA = section.getGAs()

    return runCLTAnalysis(L, Nspan, EI, GA)



def runCLTAnalysis(L:float, Nspan:int, EI:float, GA:float):
    """
    Runs a CLT panel analysis, where the beam is analyzed as a timoshenko
    beam and euler beam, and returns the deflection for each.

    Units must be in a consistent set of units for FEM that are compatible 
    with the length unit.


    Parameters
    ----------
    L : float
        Units must be in a consistent set of units for FEM that are compatible 
        with the section EI/GA units.
    Nspan : int
        The number of spans in the analysis.
    EI : float
        Units must be in a consistent set of units for FEM that are compatible 
        with the length unit.
    GA : float
        Units must be in a consistent set of units for FEM that are compatible 
        with the length unit.

    Returns
    -------
    umaxTim : float
        The deflection of the beam as a timoshenko beam.
    umaxEul : float
        The deflection of the beam as a Euler beam.

    """

    xcoords     = np.linspace(0,1,101)*Nspan*L
    
    E = 9*10**9
    G = E
    Iz = EI / E
    Avx = GA / G
    
    psSection = ps.SectionBasic(E, G, Iz = Iz, Avx = Avx)
    beamTim = ps.TimoshenkoBeam(xcoords, section = psSection)
    beamEul = ps.EulerBeam(xcoords, section = psSection)
    
    pinned = [1,1,0]
    for ii in range(Nspan+1):
        beamTim.setFixity(ii*L, pinned)
    beamTim.addDistLoadVertical(0, L*Nspan, -1000)
    
    for ii in range(Nspan+1):
        beamEul.setFixity(ii*L, pinned)
    beamEul.addDistLoadVertical(0, L*Nspan, -1000)
    
    
    # Run the analysis
    analysisTim = ps.OpenSeesAnalyzer2D(beamTim)
    analysisTim.runAnalysis()
    umaxTim = float(min(ps.getDisp(beamTim, 1)[0]))
 
    
    # Run the analysis
    analysisTim = ps.OpenSeesAnalyzer2D(beamEul)
    analysisTim.runAnalysis()
    umaxEul = float(min(ps.getDisp(beamEul, 1)[0]))
    
    return umaxTim, umaxEul


def getBeamPlot(Nspan, L, section, dispScale = 100):
    """
    Creates an output beam plot.
    """
    
    EI = section.getEIs()
    GA = section.getGAs()
    
    
    xCoords     = np.linspace(0,1,101)*Nspan*L
    
    E = 9*10**9
    G = E
    Iz = EI / E
    Avx = GA / G
    
    psSection = ps.SectionBasic(E, G, Iz = Iz, Avx = Avx)
    beamTim = ps.TimoshenkoBeam(xCoords, section = psSection)
    
    pinned = [1,1,0]
    for ii in range(Nspan+1):
        beamTim.setFixity(ii*L, pinned)
    beamTim.addDistLoadVertical(0, L*Nspan, -1000)
    
    # Run the analysis
    analysisTim = ps.OpenSeesAnalyzer2D(beamTim)
    analysisTim.runAnalysis()
    disp, xCoordsOut = ps.getDisp(beamTim, 1)
    disp = [y*dispScale for y in disp]
    
    fig, ax = ps.plotBeamDiagram(beamTim)
    xplot =  ax.lines[-1].get_xydata()[:,0]
    
    dispScale =  (xplot[1] - xplot[0]) / (L*Nspan)
    xCoordsOut = [float(x)*dispScale for x in xCoordsOut]
    argMin = np.argmin(disp)
    
    ax.plot(xCoordsOut, disp)
    ax.scatter(xCoordsOut[argMin], disp[argMin], s=150, facecolors='none', edgecolors='r')
    
    return fig, ax
