"""
Tests if plots summary information is implemented correctly.
"""

import limitstates as ls
import matplotlib.pyplot as plt
import numpy as np
import pytest

# switch the back-end if running through command line
# if __name__ != "__main__":
#     plt.switch_backend("Agg")

# def test_plot_rectangle():  
#     myMat       = ls.MaterialElastic(9.5*1000)
#     section     = ls.SectionRectangle(myMat, 300, 200)
#     fig, ax     = ls.plotSection(section)
    
#     ax.lines
#     xy = ax.patches[0].get_xy()
#     assert xy[0][1] == 0
#     assert xy[1][1] == 300



# if __name__ == "__main__":
#     test_plot_rectangle()

# else:
#     plt.close('all')



myMat       = ls.MaterialElastic(9.5*1000)
section     = ls.SectionRectangle(myMat, 300, 200)
plotDetails = {'Iy':section.Ix, 'Ix':section.Ix}

fig, ax     = ls.plotSection(section, summarizeGeometry=True)