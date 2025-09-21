"""
This is some very rough work that makes an animation of the neutral axis
NA solver
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import limitstates as ls
import limitstates.design.csa.a23.c24 as a23

"""
Next the beam section is defined. A concrete material is created, as well as
a section and set of stirrups.
"""
# fc = 25
# c = 30
# L = 5
# h = 900 
# b = 450

# barType = '30M'
# Mf = 1100

# mat         = a23.MaterialConcreteCSA24(fc)
# section     = ls.SectionRectangle(mat, b, h)
# stirrupBar  = a23.getStandardRebar('10M')
# stirrups    = ls.StirrupGroup(stirrupBar)
# concreteSection = ls.SectionConcrete(section, stirrups = stirrups)

# designProps = a23.DesignPropsConcrete24(cover= 50)

# member = ls.initSimplySupportedMember(L, 'm')
# beam   = a23.BeamColumnConcreteCsa24(member, concreteSection, designProps) 




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
ls.plotSection(beam.section)

Mr = a23.getSectionMr(beam.section) / 1000


print('Overrienforced:', status)
print(Mf, Mr)




# =============================================================================
# Initialize Plot
# =============================================================================
solver = ls.SectionNASolver(section, c24.getSectionCr, c24.getSectionSr)
NAsolutions = solver.calcNA()


NA = solver.trials[-1]
eyConc = section.concrete.mat.ey
h = section.concrete.d 
emax = (eyConc * h / NA - eyConc)


fig, axes = plt.subplots(ncols=3, sharey = True)
# plt.subplots_adjust(right=0.1)
fig.suptitle('Concrete Beam Rebar Placer', fontweight='bold')
axes[0].axvline(color="grey")
axes[0].set_xlabel('Strain (1e-3)')
axes[0].set_ylabel('Height (mm)')
lines = axes[0].plot([ 0, emax*1000, -eyConc*1000, 0], [0, 0, h, h])

axes[1].get_yaxis().set_visible(False)
axes[1].get_xaxis().set_visible(False)
axes[1].axis('off')
axes[2].axis('off')

Tr = 2000

ii = int(1)
NAmm = int(NA)
Cr = int(solver.getCr(NA) / 1000)
Tr = int(sum(solver.getFsteel(NA)) / 1000)

message = r"$\bf{Output}$\n" +  f'\nN.A. Position: {NAmm} (mm)\nSteel Force: {Tr} (kN)\nConcrete Force: {Cr} (kN)\nIteration: {ii}'
text = axes[1].text(0.65, 0.75, message, 
                    ha='left', va='center', ma='left',
                    fontsize=10, transform=plt.gcf().transFigure)

ls.plotSection(section, ax = axes[1])

# =============================================================================
# Run Animation
# =============================================================================

def plot(ii):
    
    NA = solver.trials[ii]
    Cr = int(solver.getCr(NA) / 1000)
    Tr = int(sum(solver.getFsteel(NA)) / 1000)
    NAmm = int(NA)

    message = r"$\bf{Output}$" +  f'\nN.A. Position: {NAmm} (mm)\nSteel Force: {Tr} (kN)\nConcrete Force: {Cr} (kN)\nIteration: {ii+1}'
    text.set_text(message)
    
    emax = (eyConc * h / NA - eyConc)
    lines[0].set_xdata([ 0, emax*1000, -eyConc*1000, 0])
    lines[0].set_ydata([0, 0, h, h])
    # line = axes[0].plot([ 0, emax, -eyConc, 0], [0, 0, h, h])
    return lines

Nitems = len(solver.trials)
ani = animation.FuncAnimation(fig=fig, func=plot, frames=Nitems, interval=200)
plt.show()

# f = r"animation.gif" 
# writergif = animation.PillowWriter(fps=9) 
# ani.save(f, writer=writergif)