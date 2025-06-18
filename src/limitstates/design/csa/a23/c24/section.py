"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import DBConfig, RebarFactory
from limitstates.objects.section.concrete import SectionConcrete
from .material import MaterialRebarCSA24
from limitstates import SectionRectangle, SectionCLT


def getConcreteSectionCSA24(
        
        db:str = 'csa_o86_2019') -> list[SectionRectangle]:
    """
    Loads the glulam materials for a specific database. By default loads the
    glulam sections for columns in CSAo86-19.

    Parameters
    ----------
    mat : MaterialGlulamCSA19
        The material to be applied to the section.

    Returns
    -------
    list
        A list of output sections.

    """
    config = DBConfig('csa', 'glulam', db)
    return _loadSectionRectangular(mat, config, lUnit = 'mm')

def loadRebar(matRebar:MaterialRebarCSA24,
              db:str = 'rebar', **sectionkwargs) -> list[SectionCLT]:
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
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    bar = rebarFactory.getRebar('30M')
    # return _loadSectionRectangular(mat, config, lUnit = 'mm')


    # return _loadSectionsCLT(mats, config, **sectionkwargs)