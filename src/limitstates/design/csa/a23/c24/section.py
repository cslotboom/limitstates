"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import DBConfig
from limitstates.objects.section.concrete import SectionConcrete
from limitstates.objects.section.rebar import RebarFactory, Rebar
from .material import MaterialRebarCSA24
from limitstates import SectionRectangle, SectionCLT


#TODO TEST
def loadRebarFactory(matRebar:MaterialRebarCSA24,
                      db:str = 'rebar', lUnit = 'mm') -> RebarFactory:
    """
    Reads the standard CSA A23. rebar.
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

#TODO TEST
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
    rebar : TYPE
        DESCRIPTION.

    """

    
    if not xy:
        xy = (0,0)
            
    rebar = REBARFACTORY.getRebar(barName, xy)
    
    if matRebar:
        rebar.mat = matRebar
    
    if lUnit != 'mm':
        rebar.convertUnits(lUnit)
    
    return rebar
        