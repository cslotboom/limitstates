"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import DBConfig
from limitstates.objects.section.rebar import (RebarFactory, Rebar, 
                                               StirrupTypeEnum, Stirrup, 
                                               StirrupGroup)

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


def getStandardStirrup(barName: str, 
                        barType: StirrupTypeEnum = StirrupTypeEnum.Closed,
                        Nlegs: int = 2,
                        spacing = 200,
                        matRebar: MaterialRebarCSA24 = None,
                        lUnit: str = 'mm') -> Rebar:
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
            
    rebar = getStandardRebar(barName, matRebar, lUnit = lUnit)
    
    return Stirrup(rebar, barType, Nlegs, spacing, lUnit)


        
def getStandardStirrupGroup(barName: str, 
                            barType: StirrupTypeEnum = StirrupTypeEnum.Closed,
                            Nlegs: int = 2,
                            spacing:float = 200,
                            Nstirrups: int = 1,
                            matRebar: MaterialRebarCSA24 = None,
                            ID:str = None,
                            lUnit: str = 'mm') -> StirrupGroup:
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
                
    stirrups = [None]*Nstirrups
    for ii in range(Nstirrups):
        stirrups[ii] = getStandardStirrup(barName, barType, Nlegs, spacing, 
                                          matRebar, lUnit)
    return StirrupGroup(stirrups, ID)



