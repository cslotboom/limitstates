"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import DBConfig
from limitstates.objects.section.rebar import RebarFactory, Rebar

from .material import MaterialRebarCSA24


def loadRebarFactory(matRebar:MaterialRebarCSA24,
                      db:str = 'rebar', lUnit = 'mm') -> RebarFactory:
    """
    Reads the standard CSA A23. rebar, i.e. One of 10M, 15M, 20M, 25M, 30M, 
    35M, 45M, 55M.

    Rebar bends are based on ACI tables 25.3.1

    Parameters
    ----------
    dbType : str
        The type of database to read from.

    Returns
    -------
    rebarFactory : RebarFactory
        The output rebar factory for the databae.

    """
    
    # Set up the config and load the raw dictionary.
    config = DBConfig('csa', 'rebar', db)
    rebarFactory  = RebarFactory(matRebar, config, lUnit)
    
    return rebarFactory


REBARFACTORY = loadRebarFactory(MaterialRebarCSA24(400))


def getStandardRebar(barName:str, 
                     matRebar:MaterialRebarCSA24 = None,
                     xy:tuple = None,
                     lUnit:str = 'mm') -> Rebar:
    """
    Gets a standard CSA rebar.
    Rebar bends are based on ACI tables 25.3.1

    Parameters
    ----------
    barName : str
        The rebar size. One of 10M, 15M, 20M, 25M, 30M, 35M, 45M, 55M.
    matRebar : MaterialRebarCSA24, optional
        The rebar material to use. By default a 400MPa material is used. 
        The default is None.
    xy : tuple, optional
        The xy position of the rebar. The default is None.
    lUnit : tuple, optional
        The length units position of the rebar. The default is None.

    Returns
    -------
    rebar : Rebar
        A rebar object at the input location.

    """
    
    if not xy:
        xy = (0,0)
            
    rebar = REBARFACTORY.getRebar(barName, xy, lUnit)
    
    if matRebar:
        rebar.mat = matRebar
    
    if lUnit != 'mm':
        rebar.convertUnits(lUnit)
    
    return rebar


        

# class SectionNASolverCSA24(SectionNASolver):
#     """
#     Attempts to solves for the neutral axis of a section. Assumes all 
#     bars use the same material.
    
#     Solves for the neutral axis within a section.
#     The neutral axis is measured from the top of the section.

#     Parameters
#     ----------
#     section : SectionConcrete
#         The concrete section to solve the NA of.        
#     Pf : float, optional
#         A axial force applied to the section. The default is 0.
#     yForce : bool, optional
#         A flag that specifies if moment is applied in the y or x direction. 
#         The default is True, for moment being applied about the x axis.
#     posForce : bool, optional
#         A flag that specifies if moment is positive or negative. Positive
#         moment is defined as moment that creates tension at the "bottom"
#         of the beam. e.g. a simply supported beam has positive bending.
        
#         If set to true, then the NA will be measured from the "bottom" of the
#         section, which will be assumed to be in compression.
        
#         The default is True.
#     tol : float, optional
#         The tolerance required for convergence, i.e. the difference between
#         the calcualted concrete and steel force. The default is 1e-3.
#     maxIter : float, optional
#         The maximum number of iterations needed before convergence is 
#         reached. The default is 100.
#     logging : bool, optional
#         A flag that turns on or off logging. Currently is inactive. 
#         The default is True.

#     Returns
#     -------
#     None.

#     """
#     def __init__(self, section: SectionConcrete, 
#                  Pf:float = 0, yForce: bool = True, 
#                  posForce: bool = True, NAtrial: float = None,
#                  tol: float = 1e-3, maxIter: float = 100,
#                  logging:bool = True):
#         super().__init__(section, getSectionCr, getSectionSr,
#                          Pf, yForce, posForce, 
#                          NAtrial, tol, maxIter, logging)
        
# # TODO, move this function into it's own folder?
# def solveForNA(section: SectionConcrete, 
#              Pf:float = 0, yForce: bool = True, 
#              posForce = True, NAtrial: float = None,
#              tol: float = 1e-3, maxIter: float = 100):
#     """
#     Attempts to solves for the neutral axis of a section. Assumes all 
#     bars use the same material.
    
#     Solves for the neutral axis within a section.
#     The neutral axis is measured from the top of the section.

#     Parameters
#     ----------
#     section : SectionConcrete
#         The concrete section to solve the NA of.        
#     Pf : float, optional
#         A axial force applied to the section. The default is 0.
#     yForce : bool, optional
#         A flag that specifies if moment is applied in the y or x direction. 
#         The default is True, for moment being applied about the x axis.
#     posForce : bool, optional
#         A flag that specifies if moment is positive or negative. Positive
#         moment is defined as moment that creates tension at the "bottom"
#         of the beam. e.g. a simply supported beam has positive bending.
        
#         If set to true, then the NA will be measured from the "bottom" of the
#         section, which will be assumed to be in compression.
        
#         The default is True.
#     tol : float, optional
#         The tolerance required for convergence, i.e. the difference between
#         the calcualted concrete and steel force. The default is 1e-3.
#     maxIter : float, optional
#         The maximum number of iterations needed before convergence is 
#         reached. The default is 100.
#     logging : bool, optional
#         A flag that turns on or off logging. Currently is inactive. 
#         The default is True.

#     Returns
#     -------
#     None.

#     """
    
#     naSolver = SectionNASolverCSA24(section, Pf, yForce, posForce, NAtrial,
#                                tol, maxIter)

#     return naSolver.calcNA()

