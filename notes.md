


design will have two sections
- design for the pure code
- element for specific object representations within that code.


Certain information will be code agnostic, for example, a section and it's
geometry will be independant of the code.

material is generally coupled with design and design databases.
for example, CLT and glulam have code related propreties.


Elements
- represents a physical member in space
  - has a line
  - has a section
  - can get geometry information for design/rendering
  - can get volume information.


DesignMember
- Aggregates member with design information stuff
- These are code dependant, and contain code information.
  - supports
  - loading
  - design specific information,
    - GlulamBeamCSA will have k, fire portection, etc.
	- SteelBeamCSA
  - Applied loads (Mf, Pf, etc.)
    - these are the propreties needed to complete a design