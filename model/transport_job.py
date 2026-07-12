# model/transport_job.py

from dataclasses import dataclass
from enum import Enum, auto
from model.worker import WorkerState


class TransportJobState(Enum):
    IN_TRANSIT = auto()
    COMPLETED = auto()
    CANCELLED = auto()


@dataclass
class TransportJob:
    job_id: int

    source_building_id: int
    target_building_id: int

    item_key: str
    amount: int

    start_time: float
    finish_time: float

    worker_id : int 

    state: TransportJobState = TransportJobState.IN_TRANSIT
    
    def progress(self, world_time: float) -> float:
        duration = self.finish_time - self.start_time

        if duration <= 0:
            return 1.0

        value = (world_time - self.start_time) / duration
        return max(0.0, min(1.0, value))
