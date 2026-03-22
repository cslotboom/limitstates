from enum import IntEnum
from typing import Union

import numpy as np


exposureConditons = ("beamColumn", "beamWithPanel", "panel")


class FireConditions(IntEnum):
    """
    A class that shows all possible options for fire conditions.
    These include:

    - 1 = beamColumn: exposed on 4 sides
    - 2 = beamWithPanel: exposed on all sides except it's top
    - 3 = panel: exposed only on it's bottom.

    """

    beamColumn = 1
    beamWithPanel = 2
    panel = 3


def getFireDemands(FRR:float, condition: Union[FireConditions, int]) :
    """
    A helper function used to returns the fire demands for common fire 
    conditions. These include:

    - 1 = beamColumn: exposed on 4 sides
    - 2 = beamWithPanel: exposed on all sides except it's top
    - 3 = panel: exposed only on it's bottom.

    A list can manually be created for the the FRR if the above options do not
    match the input conditions above.

    Parameters
    ----------
    condition : str
        The condition of the element from a list of typical conditions.
        The FireCondition Enumeration class can be used, or an integer.
    portection : FireConditions, int
        The type of gypusm portection to use. 
        One of "exposed", "12.7mm", "15.9mm", "15.9mmx2", "unexposed".

    Returns
    -------
    FRR : list
        The output FRR. For a rectangular section fire portection is input 
        in: [top, right, bottom, left]    
    """

    if condition == FireConditions.beamColumn:
        return [FRR, FRR, FRR, FRR]
    elif condition == FireConditions.beamWithPanel:
        return [0, FRR, FRR, FRR]
    elif condition == FireConditions.panel:
        return [FRR]
    else:
        raise Exception(f'Recived condition {condition}, expected one of {exposureConditons}')


def getFRRfromFireConditions(FRR:float, fireCon:FireConditions = 2):
    """
    A helper function used to get the appropriate FRR list from a set of 
    typical conditions.
    """

    if fireCon == FireConditions.beamWithPanel:
        FRR = np.array([0,FRR,FRR,FRR])
    elif fireCon == FireConditions.beamColumn:
        FRR = np.array([FRR,FRR,FRR,FRR])
    else:
        vals = [e.value for e in FireConditions]
        raise Exception(f'recieved {fireCon}, expected one of {vals} from FireConditions Enum')

    return FRR