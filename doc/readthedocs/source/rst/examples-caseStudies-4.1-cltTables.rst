.. _examples-caseStudies-4.1:

CLT Deflection Tables
=====================

CLT panels often have significant shear deflection because of shear deformation
in their cross layers. There are some reasources that exist for single span
clt, however, CLT is often used in multi-span conditions.

In this design example, a parametric study are run on a series of clt panels, 
and the outputs are used to create span tables. The parametric study evaluates
shear by analyzing each panel as both a Euler beam, and timoshenko beam.
Note that many helper functions are used from in the "parametricHelper" file, 
which has documentation for each function.

Also note that the actual pdf design reasource was created manually, using the
.csv outputs from this study.


.. raw:: html

	<iframe src="/en/latest/_static/4.1_CLT_Deflection_tables.pdf" width="100%" height="800px">
		This browser does not support PDFs. Please download the PDF to view it: 
		<a href="/en/latest/_static/4.1_CLT_Deflection_tables.pdf">Download PDF</a>.
	</iframe>
	
  
  
The first portion of the analysis creates the deflection tables for PRG-320 SPF 
sections. This is used to make the PRG deflection tables.
Initially sections are loaded using section databases, then a set of spans and 
span lengths are set up.

.. literalinclude:: ../../../../example/4. Case Studies/4.1 - CLT Deflection Tables/Ex 4.1 - CLT Deflection Tables.py
   :lines: 31-47

The second portion of the analysis finds the ratio of total deflection (flexural + shear), to
flexural deflection for panels with an abitary ratio of EI / GA.

.. literalinclude:: ../../../../example/4. Case Studies/4.1 - CLT Deflection Tables/Ex 4.1 - CLT Deflection Tables.py
   :lines: 58-67

Finally, plots of the section are made.

.. literalinclude:: ../../../../example/4. Case Studies/4.1 - CLT Deflection Tables/Ex 4.1 - CLT Deflection Tables.py
   :lines: 73-77


The full example is below:

 
.. literalinclude:: ../../../../example/4. Case Studies/4.1 - CLT Deflection Tables/Ex 4.1 - CLT Deflection Tables.py

.. literalinclude:: ../../../../example/4. Case Studies/4.1 - CLT Deflection Tables/parametricHelpers.py

