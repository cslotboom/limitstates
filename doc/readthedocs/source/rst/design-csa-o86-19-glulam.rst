CSA o86-2019 Glulam Design
==========================

Limitstates currently contains code for working with glulam and CLT.
Objects also exist for representing fire portection, and burning sections according to Annex B of csa o86.


 
.. autoclass:: limitstates.design.csa.o86.c19.element.DesignPropsGlulam19
   :members:
   :undoc-members:
   :show-inheritance:
 
.. autoclass:: limitstates.design.csa.o86.c19.element.BeamColumnGlulamCsa19
   :members:
   :undoc-members:
   :show-inheritance:

   
.. automodule:: limitstates.design.csa.o86.c19.element
	:members: getBeamColumnGlulamCsa19
	
.. automodule:: limitstates.design.csa.o86.c19.glulam
	:members: checkCb, checkBeamCb, checkKL, checkKzbg, checkGlulamMr, checkMrGlulamBeamSimple
	

   
.. automodule:: limitstates.design.csa.o86.c19.glulam
	:members: checkGlulamShearSimple, checkGlulamWr, checkVrGlulamBeamSimple, checkWrGlulamBeamSimple
	

.. automodule:: limitstates.design.csa.o86.c19.glulam
	:members: checkColumnCc, checkKci, checkKzcg, checkGlulamPr, checkPrGlulamColumn
	
   
.. automodule:: limitstates.design.csa.o86.c19.glulam
	:members: checkPE, checkPEColumn, checkInterTimberGeneric, checkInterEccPf, checkInterEccPfGlulam