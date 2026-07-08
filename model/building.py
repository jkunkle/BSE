from dataclasses import dataclass
from typing import Dict, List, Optional
from model.inventory import Inventory
from model.worker import WorkerState



@dataclass(frozen=True)
class BuildingTypeDefinition:
    key: str
    name: str
    x_size: int
    y_size: int
    workers: int
    capabilities: List[str]
    recipe_keys: List[str]
    storage_limits: Dict[str, int]

@dataclass
class Door:
    x: int
    y: int
    direction : str

@dataclass
class Building:
    id: int
    building_type_key: str
    x: int
    y: int
    x_size : int 
    y_size : int
    doors : List[Door] 
    inventory: Inventory
    worker_ids: List[int]

    recipe_keys: List[str] 
    current_recipe_key : str | None = None

    production_start_time : float | None = None
    production_end_time : float | None = None


