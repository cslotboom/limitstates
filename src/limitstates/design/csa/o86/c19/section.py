"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import _loadSectionRectangular, SectionDBConfig, _loadSectionsCLT
from .material import MaterialGlulamCSA19, loadCltMatDB
from limitstates import SectionRectangle, SectionCLT


def loadGlulamSections(mat:MaterialGlulamCSA19, 
                       db:str = 'csa-19.csv') -> list[SectionRectangle]:
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
    config = SectionDBConfig('csa', 'glulam', db)
    return _loadSectionRectangular(mat, config, lUnit = 'mm')

def loadCltSections(db:str = 'clt_prg320_2019.csv', **sectionkwargs) -> list[SectionCLT]:
    """
    Loads all CLT sections in the given database.

    Parameters
    ----------
    dbType : str
        The type of database to read from, can be 'si', or 'us'.

    Returns
    -------
    sections : list
        A list of the desired clt sections.

    """
    
    # Load the material dictionary
    mats = loadCltMatDB(db)
    
    # Set up the config and load the raw dictionary.
    config = SectionDBConfig('csa', 'clt', db)
        
    return _loadSectionsCLT(mats, config, lUnit = 'mm', **sectionkwargs)