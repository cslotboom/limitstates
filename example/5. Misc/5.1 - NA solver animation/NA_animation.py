"""
This is some very rough work that makes an animation of the neutral axis
NA solver
"""

import limitstates.design.csa.a23.c24 as c24
from limitstates.objects.read import DBConfig
import limitstates as ls

import matplotlib.pyplot as plt
import matplotlib.animation as animation

def get_concrete_section():
    """

    """

    h = 500
    b = 200
    deff = 450
    fc = 25
    fy = 400
    cover = 50
    mat      = c24.MaterialConcreteCSA24(fc)
    matRebar = c24.MaterialRebarCSA24(fy)
    
    section = ls.SectionRectangle(mat, b, h)
    config = DBConfig('csa', 'rebar', 'rebar')
    
    rebarFactory  = ls.RebarFactory(matRebar, config, 'mm')
    placer = ls.RebarPlacer(rebarFactory)
    
    layer2 = placer.getRebarLayer(2, '25M', deff, b  -2*cover, cover)
    Lbars = ls.RebarCollection([layer2])
    concreteSection = ls.SectionConcrete(section, Lbars)
    
    return concreteSection

section = get_concrete_section()
solver = ls.SectionNASolver(section, c24.getSectionCr, c24.getSectionSr)
NAsolutions = solver.calcNA()


# =============================================================================
# Initialize Plot
# =============================================================================
NA = solver.trials[-1]
eyConc = section.concrete.mat.ey

h = section.concrete.d 
emax = (eyConc * h / NA - eyConc)

fig, axes = plt.subplots(ncols=3, sharey = True)
# plt.subplots_adjust(right=0.1)
fig.suptitle('Neutral Axis Solver', fontweight='bold')
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

f = r"animation.gif" 
writergif = animation.PillowWriter(fps=9) 
ani.save(f, writer=writergif)