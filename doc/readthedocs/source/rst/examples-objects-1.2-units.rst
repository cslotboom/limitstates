.. _examples-1.2:

Units Example
=============


Units are an important part of limitstates. All limitstates objects that have units store the type of unit they use. The following example showcases how the unit converters are embeded in different objects, and can be used. The types of converters avalible is detailed in :ref:`units <units>`.

Similar to example 1, we define a material object. On initiation it will have one set of units:

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.2 - unit basics.py
   :lines: 7-8, 11-12

The units for stress used in this material are stored in the 'iUnit' attribute, where "i" is the type of unit. In this case were getting stress, so the sUnit attribute stores the stress and sConvert method can be used to find the conversion factor between the base unit and another valid input unit. Using the converter attribute, we can easily do spot conversions on our attribute to determine the in a different unit.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.2 - unit basics.py
   :lines: 15-17


Similarly, object that has a length dimension will have a lUnit attribute, and a lConvert method. An example is shown below, where a sections area can be converted from one set of units to another.


.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.2 - unit basics.py
   :lines: 20-23, 26, 29-30

The full example is below:

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.2 - unit basics.py


