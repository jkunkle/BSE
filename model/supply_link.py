# model/supply_link.py

from dataclasses import dataclass
from model.worker import WorkerState


@dataclass
class SupplyLink:
    id: int

    source_building_id: int
    target_building_id: int

    worker_ids: List[int]
    item_key: str
    amount_per_job: int = 1

