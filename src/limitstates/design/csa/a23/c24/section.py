"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import DBConfig
from limitstates.objects.section.concrete import SectionConcrete
from limitstates.objects.section.rebar import RebarFactory, Rebar
from .material import MaterialRebarCSA24
from limitstates import SectionRectangle, SectionCLT



def loadRebarFactory(matRebar:MaterialRebarCSA24,
              db:str = 'rebar', lUnit = 'mm') -> RebarFactory:
    """
    Loads all CLT sections in the given database.

    Parameters
    ----------
    dbType : str
        The type of database to read from.

    Returns
    -------
    sections : list
        A list of the desired clt sections.

    """
    
    # Set up the config and load the raw dictionary.
    config = DBConfig('csa', 'rebar', db)
    rebarFactory  = RebarFactory(matRebar, config, lUnit)
    
    return rebarFactory


rebarFactory = loadRebarFactory(MaterialRebarCSA24(400))

def getStandardRebar(barName:str, 
                     matRebar:MaterialRebarCSA24 = None,
                     xy:tuple = None,
                     lUnit:str = 'mm') -> Rebar:
    """
    Gets a standard CSA rebar.

    Parameters
    ----------
    barName : str
        The rebar size. One of 10M, 15M, 20M, 25M, 30M, 35M, 45M, 55M.
    matRebar : MaterialRebarCSA24, optional
        The rebar material to use. By default a 400MPa is used. 
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
            
    rebar = rebarFactory.getRebar(barName, xy)
    
    if matRebar:
        rebar.mat = matRebar
    
    if lUnit != 'mm':
        rebar.convertUnits(lUnit)
    
    return rebar
        