from enum import Enum, auto
class PlacementError(Enum):
    LACKING_WORKERS = auto()
    OUTSIDE_GRID = auto()
    AREA_OCCUPIED = auto()
    LACKING_FUNDING = auto()
