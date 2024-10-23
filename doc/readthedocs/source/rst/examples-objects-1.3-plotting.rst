.. _examples-1.3:
.. currentmodule:: limitstates


Plotting Example
================


This example showcases features limitstates has for plotting structural sections/elements. All plotting is done through matplotlib's pyplot library. We start by importing the base libary and some material standards.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 8-10, 11-12

There are two main ways of plotting commonly supported for sections. Direct plotting through throught the :py:func:`~limitstates.objects.output.pyplot.plotSection` function, or plotting via a design element with the :py:func:`~limitstates.objects.output.pyplot.plotElementSection` function.

The plotsection function makes some basic assumption, but mostly leaves customizing the plot to the user. The plotElementSection can only be applied to has access to design information, and uses these to 
make more complicated plots with less user input. 

A basic example is shown below.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 26-32

Parts of plots can be controlled with the "PlotConfigCanvas", which configures the plot's canvas, and "PlotConfigObject", which configures the appearance of an individual objects.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 40-44

The plotSection function can also be customized using kwargs for matplotlib's ax.fill object. Any properties given to the kwargs will overwrite properties set in the configuration objects.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 52-53

Element plotting has less direct user customization, but can be used to easily make more complicated plots. All design elements Elements have a :py:class:`~limitstates.objects.display.EleDisplayProps` object, which stores a :py:class:`~limitstates.objects.display.PlotConfigObject` , and :py:class:`~limitstates.objects.display.PlotConfigCanvas`. Design specific plotting information is also stored in these.

The element will also store a section and member object. By default the section and member used will be the same as the section/member used by design, but these could be overwritten to display different sections.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 71-78


Special Plot types - Glulam
---------------------------

plotElementSection will include special properties with each element. For example, glulam elements with a fire section will have the char plotted if the burnsection is set.

They will also include a fill, estimating where laminations would be. Note that the glulam lamination height is only decorative right now, it doesn't have any physical meaning.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 92-101


Special Plot types - CLT
------------------------

CLT sections and their char layers can also be plotted. If the section is burned, the plotElementSection will attempt to plot the burned section.

.. literalinclude:: ../../../../example/1. Basic Objects/Ex1.3 - plotting.py
   :lines: 110-124



