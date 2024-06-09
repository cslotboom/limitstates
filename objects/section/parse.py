"""
Contains functions for sorting collections of limitstate objects
"""


from operator import attrgetter

__all__ = ["sortSectionsByAttr", "filterSectionsByAttr"]


def sortSectionsByAttr(sectionList:list, attr:str, reverse:bool = False):
    """
    Sort a list of sections by input attribute from smallest to largest.

    Parameters
    ----------
    sectionList : list
        The sections to sort.
    attr : str
        The attribute to sort by.
    reverse : bool, optional
        A flag that allows the list to be reversed. The default is True.

    Returns
    -------
    list
        The sorted list.

    """
            
    return sorted(sectionList, key=attrgetter(attr), reverse = reverse)


def filterSectionsByAttr(sectionList:list, attr:str, 
                         lowerLim =None, upperLim = None):
    """
    Filter a list of sections using an upper and lower limit.

    Parameters
    ----------
    sectionList : list
        The sections to sort.
    attr : str
        The attribute to sort by.
    upperLim : bool, optional
        A flag that allows the list to be reversed. The default is True.
    lowerLim : bool, optional
        A flag that allows the list to be reversed. The default is True.
        
    Returns
    -------
    list
        The sorted list.

    """
    if upperLim and lowerLim:
        return [item for item in sectionList if (item.__dict__[attr] <= upperLim and lowerLim <= item.__dict__[attr])]
    elif upperLim:
        return [item for item in sectionList if item.__dict__[attr] <= upperLim]
    elif lowerLim:
        return [item for item in sectionList if lowerLim <= item.__dict__[attr]] 
    else:
        return sectionList
    
    

