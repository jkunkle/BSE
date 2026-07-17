from dataclasses import dataclass, field
from enum import Enum, auto

class WorkerState(Enum):
    IDLE = auto()
    ASSIGNED = auto()
    MOVING = auto()
    WORKING = auto()
    RESTING = auto()

class NeedType(Enum):
    FOOD = 'food'
    RECREATION = 'recreation'
    SLEEP = 'sleep'

@dataclass
class WorkerType:

    key : str
    name : str
    price : float
    need_rates : Dict[NeedType, float]
    

def default_worker_needs() -> Dict[NeedType, float]:
    return {
        NeedType.FOOD: 1.0,
        NeedType.RECREATION: 1.0,
        NeedType.SLEEP: 1.0,
    }

@dataclass
class Worker:
    id: int
    type_key: str

    state: WorkerState = WorkerState.IDLE

    assigned_building_id: Optional[int] = None
    assigned_supply_id: Optional[int] = None
    assigned_job_id: Optional[int] = None
    home_building_id : Optional[int] = None

    located_building_id :Optional[int] = None

    carrying_item_type_id: Optional[str] = None
    carrying_amount: int = 0

    speed: float = 1.0
    salary: float = 5
    needs: dict[NeedType, float] = field(default_factory=default_worker_needs)


