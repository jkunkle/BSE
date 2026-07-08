from dataclasses import dataclass
from enum import Enum, auto

class WorkerState(Enum):
    IDLE = auto()
    ASSIGNED = auto()
    MOVING = auto()
    WORKING = auto()
    RESTING = auto()


@dataclass
class Worker:
    id: int

    state: WorkerState = WorkerState.IDLE

    assigned_building_id: Optional[int] = None
    assigned_supply_id: Optional[int] = None
    assigned_job_id: Optional[int] = None

    located_building_id :Optional[int] = None

    carrying_item_type_id: Optional[str] = None
    carrying_amount: int = 0

    speed: float = 1.0

