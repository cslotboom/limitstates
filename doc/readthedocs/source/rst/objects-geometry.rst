Geometry
========

The geometry module contains objects that help represent where structural elements are in space. Generally, a series of points are represented as nodes, with curves connecting them. Member objects are aggregates of this combination between curves and nodes. Also includes are classes that can represent structural support conditions.
 
 
Node
----
 
.. autoclass:: limitstates.objects.geometry.Node
   :members:
   :undoc-members:
   :show-inheritance:
 
Support
-------
 
.. autoclass:: limitstates.objects.geometry.Support
   :members:
   :undoc-members:
   :show-inheritance:

 
.. autoclass:: limitstates.objects.geometry.SupportTypes2D
   :members:
   :undoc-members:
   :show-inheritance:

  
Line
----

.. autoclass:: limitstates.objects.geometry.Line
   :members:
   :undoc-members:
   :show-inheritance:
   
Member
------
   
.. autoclass:: limitstates.objects.geometry.Member
   :members:
   :undoc-members:
   :show-inheritance:

   
Helper Functions
----------------
   
   
.. automodule:: limitstates.objects.geometry
	:members: getLineFromLength, getLineFromNodes, initSimplySupportedMember
