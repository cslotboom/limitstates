"""
Contains a number of converters that can be used to export beams

"""

import planesections as ps
import numpy as np
# from limitstates import Node, Support

from .. section import SectionMonolithic
from .. element import BeamColumn



def convertBeamColumnToPlanesections(element: BeamColumn, meshSize: int = 100,
                                     lUnit = 'm', sUnit = 'Pa'):
    """
    All output elements will be lines
    
    The input line must have nodes along the x axis only.
    """
    
    # Create the secton
    section  = element.section
    
    if not isinstance(section, SectionMonolithic):
        raise Exception('Only Monolotihic sections can currently be converted.')
    
    # Convert the section regular propreties
    sfactor = element.section.mat.sConvert(sUnit)
    E = element.section.mat.E * sfactor
    G = element.section.mat.G * sfactor
    
    # Convert the section geometry propreties
    slfactor = element.section.lConvert(lUnit)
    A  = element.section.A  * slfactor ** 2
    Ix = element.section.Ix * slfactor ** 4
    Iy = element.section.Iy * slfactor ** 4
    J  = element.section.J  * slfactor ** 4
    analysisSection = ps.SectionBasic(E, G, A, Ix, Iy, J)

    # begin beam construction
    beam  = ps.EulerBeam(section = analysisSection)
    
    nodes  = element.member.nodes
    xNodes = [node.p1[0] for node in nodes]
    L = max(xNodes)
    
    # Add the base meshpoints
    x       = np.linspace(0, L, meshSize)
    beam.addNodes(x)
    
    # Add the special nodes with fixity
    fixities = [list(node.support.fixity) for node in nodes]
    labels   = [node.label for node in nodes]
    
    beam.addNodes(xNodes, fixities, labels)

    
    return beam

# analysisBeam = o86.
    
    
        
# import planesections as ps

# ps.
