"""
Contains functions for sorting collections of limitstate objects
"""


from operator import attrgetter

__all__ = ["sortByAttr", "filterByAttrRange", "filterByName"]


def sortByAttr(sectionList:list, attr:str, reverse:bool = False):
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


def filterByAttrRange(sectionList:list, attr:str, 
                         lowerLim =None, upperLim = None):
    """
    Filter a list of objects using an upper and lower limit.

    Parameters
    ----------
    sectionList : list
        The sections to sort.
    attr : str
        The attribute to sort by.
    lowerLim : bool, optional
        The lower limit of the attribute.
    upperLim : bool, optional
        The upper limit of the attribute.
        
    Returns
    -------
    list
        The filtered list.

    """
    if upperLim and lowerLim:
        return [item for item in sectionList if (item.__dict__[attr] <= upperLim and lowerLim <= item.__dict__[attr])]
    elif upperLim:
        return [item for item in sectionList if item.__dict__[attr] <= upperLim]
    elif lowerLim:
        return [item for item in sectionList if lowerLim <= item.__dict__[attr]] 
    else:
        return sectionList
    
def filterByAttrVal(sectionList:list, attr:str, filterVal:str):
    """
    Filter a list of sections using an upper and lower limit.

    Parameters
    ----------
    sectionList : list
        The sections to sort.
    attr : str
        The attribute to sort by.
    filterVal : str, optional
        The value to short by 
        
    Returns
    -------
    list
        The filtered list.

    """
    
    return [item for item in sectionList if (filterVal in attrgetter(attr)(item))]

def filterByName(sectionList:list, filterVal:str):
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
        The filtered list.

    """
    
    return filterByAttrVal(sectionList, 'name', filterVal)
    
