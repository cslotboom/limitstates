"""
This is some very rough work that makes an animation of the neutral axis
NA solver

Some truely awful matplotlib hackery is used.
"""

import limitstates.design.csa.a23.c24 as c24
# from limitstates.objects.read import DBConfig
import limitstates as ls


from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Circle, Polygon
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from limitstates.objects.display import MATCOLOURS

import limitstates.design.csa.a23.c24 as a23

def get_concrete_section(h = 900, b = 450):
    """

    """
    fc = 25
    c = 30
    L = 5
     

    mat         = a23.MaterialConcreteCSA24(fc)
    section     = ls.SectionRectangle(mat, b, h)
    stirrupBar  = a23.getStandardRebar('10M')
    stirrups    = ls.StirrupGroup(stirrupBar)
    concreteSection = ls.SectionConcrete(section, stirrups = stirrups)
    
    designProps = a23.DesignPropsConcrete24(cover= c)
    
    member = ls.initSimplySupportedMember(L, 'm')
    beam   = a23.BeamColumnConcreteCsa24(member, concreteSection, designProps) 
        
    return beam
    
    
barType = '30M'
Mf = 1100
    
beam = get_concrete_section()
section = beam.getSection()
status = a23.designBottomSteelForMr(Mf, beam, barType)
# ls.plotSection(beam.section)

Mr = round(a23.getSectionMr(beam.section) / 1000)


# print('Overrienforced:', status)
# print(Mf, Mr)


# heights = [1500, 1400, 1300, 1200, 1100, 1000, 900, 800, 700]
# heights = [1200, 1100, 1000, 900, 800, 700]
heights = list(range(1200, 650, -50))
heights += [700, 700, 700]
hmax = max(heights)

# =============================================================================
# Initialize Plot
# =============================================================================
solver = ls.SectionNASolver(section, c24.getSectionCr, c24.getSectionSr)
NAsolutions = solver.calcNA()


NA = solver.trials[-1]
h = section.concrete.d 
# eyConc = section.concrete.mat.ey
# emax = (eyConc * h / NA - eyConc)


fig, axes = plt.subplots(ncols=2, sharey = True)
# plt.subplots_adjust(right=0.1)
fig.suptitle('Limitstates Beam Rebar Design', fontweight='bold')
# axes[0].axvline(color="grey")
axes[0].set_ylim([-50, hmax])
axes[0].set_xlabel('Strain (1e-3)')
axes[0].set_ylabel('Height (mm)')
axes[0].axis('off')

line, = axes[0].plot([ -100, section.getWidth() + 100], [h - NA, h - NA])

axes[1].get_yaxis().set_visible(False)
axes[1].get_xaxis().set_visible(False)
axes[1].axis('off')

NAmm = int(NA)
Cr = int(solver.getCr(NA) / 1000)
Tr = int(sum(solver.getFsteel(NA)) / 1000)

message = r"$\bf{Output}$" 
message += f'\nHeight: {h} (mm)\n'
message += f'Demands: {Mf} (kNm)\n'
message += f'Capacity: {Mr} (kNm)\n'
message += f'Over-reinforced Status: {status}\n'
message += f'\nN.A. Position: {NAmm} (mm)\n'
message += f"Steel Force: {Tr} (kN)\n"
# message += f'Concrete Force: {Cr} (kN)\n'
text = axes[1].text(0.5, 0.5, message, 
                    ha='left', va='center', ma='left',
                    fontsize=10, transform=plt.gcf().transFigure)

ls.plotSection(section, ax = axes[0])

rectanglePatches = axes[0].patches
rebarCollection  = axes[0].collections
rectangleLines  = axes[0].lines[1]

# ls.plotSection(section, ax = axes[0])

# =============================================================================
# Run Animation
# =============================================================================


# heights = [1500, 1400, 1300, 1200, 1100, 1000, 900, 800]


# =============================================================================
# 
# =============================================================================




def plot(ii):

    beam = get_concrete_section(heights[ii])
    section = beam.section
    status = a23.designBottomSteelForMr(Mf, beam, barType)
    Mr = round(a23.getSectionMr(section) / 1000)
    h = section.concrete.d 
    b = section.concrete.b
    
    solver = ls.SectionNASolver(section, c24.getSectionCr, c24.getSectionSr)
    solver.calcNA()
    
    NA = solver.trials[-1]
    Tr = int(sum(solver.getFsteel(NA)) / 1000)
    NAmm = int(NA)

    axes[0].set_ylim([-50, hmax])
    
    rectanglePatches[0].set_xy([[0, h], [b, h], [b, 0], [0, 0]])
    
    rectangleLines.set_xdata([0, b, b, 0, 0])
    rectangleLines.set_ydata([h, h, 0, 0, h])
    
    # rebarCollection[0].remove()
    rebarCollection[0].remove()

    lverts = section.rebar.getCoords(flatten=True)
    radii  = [d/2 for d in section.rebar.getAttr('d', flatten=True)]
    p = PatchCollection([Circle(vert, r) for vert, r in zip(lverts, radii)], 
                        color = MATCOLOURS['steel'])   
    
    axes[0].add_collection(p)
    
    # print(axes[0].patches)

    message = r"$\bf{Output}$"  + '\n'
    message += f'Demand: {Mf} (kNm)\n'
    message += f'Capacity: {Mr} (kNm)\n\n'
    message += f'Height: {h} (mm)\n'
    message += f'Over-reinforced Status: {status}\n'
    message += f'\nN.A. Position: {NAmm} (mm)\n'
    message += f"Net Steel Force: {Tr} (kN)\n"
    text.set_text(message)
    
    line.set_xdata([ -100, section.getWidth() + 100])
    line.set_ydata([h - NA, h - NA])
    # print(h-NA)
    return ()

Nitems = len(heights)
ani = animation.FuncAnimation(fig=fig, func=plot, frames=Nitems, interval=500)
plt.show()

f = r"animation.gif" 
writergif = animation.PillowWriter(fps=2.5) 
ani.save(f, writer=writergif)