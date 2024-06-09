"""
Contains functions for managing sections specific to CSAo86-19
"""

from limitstates.objects.read import _loadSectionRectangular, SectionDBConfig
from .material import MaterialGlulamCSA19
from limitstates import SectionRectangle


def loadGlulamSections(mat:MaterialGlulamCSA19, 
                       db:str = 'csa-19.csv') -> list[SectionRectangle]:
    """
    Loads the glulam materials for a specific database. By default loads the
    glulam sections for columns in CSAo86-19.

    Parameters
    ----------
    mat : MatCLTLayer_c19
        The material to be used.

    Returns
    -------
    list
        DESCRIPTION.

    """
    config = SectionDBConfig('csa', 'glulam', db)
    return _loadSectionRectangular(mat, config, lUnit = 'mm')