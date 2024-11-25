"""
Contains functions for sorting collections of limitstate objects
"""


from operator import attrgetter

__all__ = ["sortByAttr", "filterByAttrRange", "filterByName", "getByName"]


def sortByAttr(objectList:list, attr:str, reverse:bool = False):
    """
    Sort a list of objects by input attribute from smallest to largest.

    Parameters
    ----------
    objectList : list
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
            
    return sorted(objectList, key=attrgetter(attr), reverse = reverse)


def filterByAttrRange(objectList:list, attr:str, 
                      lowerLim =None, upperLim = None):
    """
    Filter a list of objects using an upper and lower limit.

    Parameters
    ----------
    objectList : list
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
        return [item for item in objectList if (item.__dict__[attr] <= upperLim and lowerLim <= item.__dict__[attr])]
    elif upperLim:
        return [item for item in objectList if item.__dict__[attr] <= upperLim]
    elif lowerLim:
        return [item for item in objectList if lowerLim <= item.__dict__[attr]] 
    else:
        return objectList
    
def filterByAttrVal(objectList:list, attr:str, filterVal:str):
    """
    Returns a list of objects if the attribute "attr" contains the filter value
    "filterVal". For example, steel sections can be filtered by name to find W
    sections with attr = name and filterVal = 'W'

    Parameters
    ----------
    objectList : list
        The sections to sort.
    attr : str
        The attribute to sort by.
    filterVal : str, optional
        The value to be included in the attribute of each object attr.
        
    Returns
    -------
    list
        The filtered list.

    """
    
    return [item for item in objectList if (filterVal in attrgetter(attr)(item))]

def filterByName(objectList:list, filterVal:str):
    """
    Finds all sections that hve the string of filterVal in it's name.

    Parameters
    ----------
    objectList : list
        The sections to sort.
    filterVal : str
        The string to check if is in any names.

    Returns
    -------
    list
        The filtered list.

    """
    
    return filterByAttrVal(objectList, 'name', filterVal)
    

def getByName(objectList:list, filterVal:str):
    """
    Returns the first object that has the string of filterVal in it's name.
    Results are not case sensetive.

    Parameters
    ----------
    objectList : list
        The sections to sort.
    filterVal : str
        The string to check if is in any names.

    Returns
    -------
    list
        The filtered list.

    """
    filterVal = filterVal.lower()
    for ii in range(len(objectList)):
        if filterVal in objectList[ii].name.lower():
            return objectList[ii]
    
    raise Exception(f'No object with name {filterVal} found')