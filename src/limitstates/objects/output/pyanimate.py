"""
These functions manages matplotlib plotting of sections.
"""
"""
Features of a plot:
    - Create a visualization of the section
    - Show a dictionary of common propreties Ix, Sx, Zx, etc.
    - Show a dictionary of results

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Circle, Polygon

import matplotlib.patches as mpatches
import matplotlib.path as mpath
from matplotlib.axes import  Axes
import matplotlib.animation as animation

from .. section import SectionAbstract, SectionRectangle, SectionConcrete, SectionNASolver
from .. element import BeamColumn, NAsolver

import limitstates.objects.output.model as md
from . pyplot import plotSection
         
class ConcreteConvergenceAnimator:
        
    def __init__(self, naSolver:SectionNASolver):
        self.solver  = naSolver
        self.section = naSolver.section
        
        
        
