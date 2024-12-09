"""
An example that overviews the special object propreties elements have,
in particular, the design propreties.

All structural elements have three objects:
    - userProps
    - designProps
    - eleDisplayProps

"""
import limitstates as ls
import limitstates.design.csa.o86.c19 as o86

MPa = 1
width = 200 # Section width in mm
depth = 600 # Section depth in mm
length = 8  # Beam length in m

glulamMat = ls.MaterialElastic(9500)
glulamMat.fb = 24
section   = ls.SectionRectangle(glulamMat, width, depth)


"""
The userProps is the simplest object - it's a dictionary that can be safely 
used by downstream clients to store data. The limitstates library will never 
touch this data. For example, if you need to store points of inflection in a 
beam for script, you could create a custom POI variable. 
"""

beam = o86.getBeamColumnGlulamCsa19(length, section)
pointsOfInflection = [3,5]
beam.userProps['poi'] = pointsOfInflection

"""
As the name suggests, design propreties are used by design libraries to 
to determine outputs such as section capacity. Each design element class, 
will have it's own design propreties subclass, i.e. DesignPropsGlulam19 for 
glulam elements from csa-o86-19

These propreties are set by the user, but used directly by the limitstates 
library, and sometimes changed by the limitstates library.

Using the design propreties, it's also possible to decouple element geometry 
from "design" element geometry for certain checks. In the example below, we
set a shorter design length for a member.

"""
Lx = 7
customDesignProps = o86.DesignPropsGlulam19(Lx = Lx, kexB = 1, lateralSupport=False)

member     = ls.initSimplySupportedMember(length, 'm')
beamBasic  = o86.BeamColumnGlulamCsa19(member, section)
beamCustom = o86.BeamColumnGlulamCsa19(member, section, customDesignProps)

Mr1 = o86.checkMrGlulamBeamSimple(beamBasic)
Mr2 = o86.checkMrGlulamBeamSimple(beamCustom)


"""
The attribute eleDisplayProps are used to manage all display outputs from the
model. This includes the all plots for the section, and configuration variables
that are used in the plot.
Each design structural element will have it's own display proprety class for 
configuration, and by default structural elements will use their design section
for display. However, it's possible to overwrite the basic object to decouple 
the design element from the display element.

In the example we define a custom display element, which will be used to create
plots instead of the basic display element.
"""
displaySection   = ls.SectionRectangle(glulamMat, 100, 100)
dispProps = o86.EleDisplayPropsGlulam19(section = displaySection)
beamCustomDisplay = o86.BeamColumnGlulamCsa19(member, section, 
                                              eleDisplayProps = dispProps)

# The elements have different looking plots...
ls.plotElementSection(beamBasic)
ls.plotElementSection(beamCustomDisplay)

# But moments of both sections are the same!
Mr1 = o86.checkMrGlulamBeamSimple(beamBasic)
Mr2 = o86.checkMrGlulamBeamSimple(beamCustomDisplay)