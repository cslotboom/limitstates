"""
THis moodule is used for designing connections.

"""

from dataclasses import dataclass
from limitstates import (Member, SectionRectangle, initSimplySupportedMember, SectionSteel)

#need to input GypusmRectangleCSA19 directly to avoid circular import errors
from limitstates import BeamColumn, EleDisplayProps




