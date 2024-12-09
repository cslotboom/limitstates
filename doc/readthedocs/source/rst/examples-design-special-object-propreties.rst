.. _examples-design-special-object-propreties:

Examples: Special Object Propreties
===================================

All "design" structural objects will have three special overviews the special object propreties:
    - userProps
    - designProps
    - eleDisplayProps
	
The following example shows how they can be used. The examle starts with creating a basic section.


.. literalinclude:: ../../../../example/2. Design/2.1.0 - Special Object Propreties.py
   :lines: 11-21

The userProps is the simplest object - it's a dictionary that can be safely used by downstream clients to store data. The limitstates library will never touch this data. For example, if you need to store points of inflection in a beam for script, you could create a custom POI variable. 

.. literalinclude:: ../../../../example/2. Design/2.1.0 - Special Object Propreties.py
   :lines: 31-33


As the name suggests, design propreties are used by design libraries to to determine outputs such as section capacity. Each design element class, 
will have it's own design propreties subclass, i.e. :py:class:`~limitstates.design.csa.o86.c19.element.DesignPropsGlulam19` for glulam elements from csa-o86-19.

These propreties are set by the user, but used directly by the limitstates library, and sometimes changed by the limitstates library.

Using the design propreties, it's also possible to decouple element geometry from "design" element geometry for certain checks. In the example below, we set a shorter design length for a member.

.. literalinclude:: ../../../../example/2. Design/2.1.0 - Special Object Propreties.py
   :lines: 49-57


The attribute :py:class:`~limitstates.objects.display.EleDisplayProps` are used to manage all display outputs from the model. This includes the all plots for the section, and configuration variables that are used in the plot.
Each design structural element will have it's own display proprety class for configuration, and by default structural elements will use their design section for display. However, it's possible to overwrite the basic object to decouple the design element from the display element.
In the example we define a custom display element, which will be used to create plots instead of the basic display element.
 
.. literalinclude:: ../../../../example/2. Design/2.1.0 - Special Object Propreties.py
   :lines: 72-83

The full example can be seen below.
 
.. literalinclude:: ../../../../example/2. Design/2.1.0 - Special Object Propreties.py
