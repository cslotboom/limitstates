.. _examples-1.1:

Hello World Example
===================

The following is a basic example showing how structural objects can be loaded and acted on by design codes.

First we import the base limitstates library, and a design library we're working with, in this case CSA's S16 steel from 2024. Design libraries are stand-alone modules, and will often be imported separately.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines: 8-9
   
We define some variables that define the element. In this example units will be set later when instantiating the object

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines: 11-13

We then define a material and it's units. In this example we will use a code specific material from our design library, but there are also code - agnostic materials that canbe used from the  base library. See :ref:`object <object-material>`:. We also import a steel section database from the  :ref:`availible databases <section-db>`: . All sections are code-agnostic.


.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines: 16, 19-20


See the :py:func:`~limitstates.objects.read.getSteelSections` and :py:func:`~limitstates.objects.read.getSteelSections` 

We define a simply supported member for our section using a helper function. Members represent where an element is in space, how many spans it has, it's support condition, etc. Complicated members, but in this case we are happy to initialize a simply supported member

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines: 23

Finally, we define a code specific design element. Elements combine sections and members and there are two type of elements: generic elements, and design elements. Further details about generic elements can be found in the :ref:`object section <objects>`. Design elements like the one we will use (:py:class:`~limitstates.design.csa.s16.c24.element.BeamColumnSteelCsa24`) are found in design libraries, and contain design specific information. In this case, the beam's lateral support conditon has been set on initialization.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines: 26

Once it is defined, we use code checks from the design library on our element. 
Each code function will return an output with a specific unit set, in this case Nm are returned.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py
   :lines:  29
  
  
The full example is seen below:

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.1 - hello world.py

