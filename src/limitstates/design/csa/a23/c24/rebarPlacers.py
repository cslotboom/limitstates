"""
Contains functions for managing sections specific to CSAo86-19
"""

# from limitstates.objects.read import DBConfig
from limitstates.objects.section import SectionConcrete, RebarLocationEnum
from limitstates.objects.section.concrete import RebarPlacerRow, RebarSpacingConfig
from .material import MaterialRebarCSA24

from .beamColumn import getSectionCr, getSectionSr, getSmin
from .section import REBARFACTORY


class RebarPlacerRowCSA24(RebarPlacerRow):
        
    def __init__(self, section: SectionConcrete, 
                 designProps: None, 
                 rebarMat = MaterialRebarCSA24|None, 
                 lUnit:str = 'mm'):
        
        rebarFactory = REBARFACTORY
        if lUnit != 'mm':
            rebarFactory.setLunit(lUnit)
        
        if isinstance(rebarMat, None):
            pass
        else:
            rebarFactory.setMaterial(rebarMat)
            
        super().__init__(section, rebarFactory)
        
    
    def _getSpacingRules(self, barType, designProps) -> RebarSpacingConfig:
        
        
        archetypeBar = self.factory.getRebar(barType, lUnit='mm')
        d = archetypeBar.d
        rcurve = archetypeBar.rcurve

        
        # TODO review this material
        lFactor = self.section.concrete.mat.lConvert('mm')
        amax    = self.section.concrete.mat.Amax * lFactor
        
        
        s = getSmin(d, amax)
        c = designProps.cover
        
        # TODO: guarentee this is in mm
        if self.section.stirrups:
            dstirrup = self.section.stirrups.rebar.d
        else:
            dstirrup = 0
        
        RebarSpacingConfig(s, c, dstirrup, rcurve)
        
        
    def place(self, Nbars:int, barType:str, location:RebarLocationEnum): 
        
        config = self._getSpacingRules()
        self.setSpacingConfig(config)

               
        self.section.addBars(self._place(Nbars, barType, location))
         
        
        
        
        
    