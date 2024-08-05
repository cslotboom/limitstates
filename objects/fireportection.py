"""
These classes represent fire portection that can be applied to sections.
"""

from dataclasses import dataclass
import numpy as np

__all__ = []


class FirePortection:
    portectionTypes:dict[str:float]
    portection:list[str]
    Nside:int
    
    def __init__(self, portectionTypes:list[str]):
        self.portection = portectionTypes
        self.Nside = len(portectionTypes)
    
    def setPortectionTime(self):
        portTime = []
        for item in self.portection:
            portTime.append(self.portectionTypes[item])
        self.portectionTime = portTime
        
    def getPortectionTime(self):
        return self.portectionTime

    def _validateInput(self, portectionTypes):
        NsideIn = len(portectionTypes)
        if self.Nside != NsideIn:
            raise Exception(f'Input fire porection has {NsideIn} entries, but {self.Nside} is required.')




