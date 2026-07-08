from utils.error import Error
from utils.error_type import PlacementError

from model.grid import Grid
from model.building import Building, Door
from model.inventory import Inventory
from model.supply_link import SupplyLink


class World():

    def __init__(self, config_store, workers=0, x=50, y=50):

        self._x_max = x
        self._y_max = y


        self.grid = Grid(x, y)
        self.buildings = {}
        self.config = config_store
        self._recpies = {}
        self.transport_jobs = {}
        self.supply_links: dict[int, SupplyLink] = {}
        self.workers : [int, Worker]

        self._next_building_id: int = 0
        self._next_supply_link_id: int = 0
        self._next_transport_job_id: int = 0
        self._next_worker_id: int = 0

        self.changed_buildings = set()
        self.changed_transport_jobs = set()
        self.changed_grid = False
        self.time = 0
        self.avaialble_workers = workers


    def __repr__(self):

        info_str = ''
        for building in self.buildings:
            info_str += building.__repr__() + '\n'

        return info_str


    def advance_time(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.time += dt
        print ('SUPPLY')
        print (self.supply_links)
        print (self.transport_jobs)

    def get_next_building_id(self):

        self._next_building_id +=1 

        return self._next_building_id - 1

    def get_next_supply_link_id(self) -> int:
    
        self._next_supply_link_id += 1
    
        return self._next_building_id - 1

    def get_next_transport_job_id(self) -> int:
    
        self._next_transport_job_id += 1
    
        return self._next_transport_job_id - 1

    def get_next_worker_id(self) -> int:
    
        self._next_worker_id += 1
    
        return self._next_worker_id - 1

    def add_building(self, building_type_key: str, x: int, y: int):

        if building_type_key not in self.config.building_types:
            raise ValueError(f"Unknown building type: {building_type_key}")
    
        building_type = self.config.building_types[building_type_key]
    
        if not self.grid.is_area_free_for_building(
            x=x,
            y=y,
            x_size=building_type.x_size,
            y_size=building_type.y_size,
        ):
            return Error(PlacementError.AREA_OCCUPIED, 'Area occupied')

        if building_type.workers > self.avaialble_workers:
            return Error(
                PlacementError.LACKING_WORKERS,
                f'Building requires {building_type.avaialble_workers}, '
                'but only {self.avaialble_workers} avaialble'
            )

        building_id = self.get_next_building_id()

        doors = []
        if 'production' in building_type.capabilities:
            doors.append(Door(0, 0, 'out'))

        if 'transformation' in building_type.capabilities:
            doors.append(Door(0, 0, 'out'))
            doors.append(Door(building_type.x_size, building_type.y_size, 'in'))

        if 'storage' in building_type.capabilities:
            #FIXME -- ignornig number of doors

            doors.append(Door(0, 1, 'both'))
            doors.append(Door(1, 0, 'both'))
            doors.append(Door(1, 2, 'both'))
            doors.append(Door(2, 1, 'both'))

        inventory = Inventory(limits=building_type.storage_limits) 

        curr_recipe_key = None
        if building_type.recipe_keys:
            curr_recipe_key = building_type.recipe_keys[0]

        worker_ids = []
        for iw in range(0, building_type.workers):
            wid = self.get_next_worker_id()
            self.workers.append(
                Worker(
                    wid,
                    assigned_building_id=building_id
                    state=WorkerState.ASSIGNED
                ))

            worker_ids.append(wid)

        self.avaialble_workers -= len(workers)
    
        building = Building(
            id=building_id,
            building_type_key=building_type_key,
            x=x,
            y=y,
            x_size=building_type.x_size,
            y_size=building_type.y_size,
            doors = doors,
            worker_ids = worker_ids
            inventory = inventory,
            recipe_keys = building_type.recipe_keys,
            current_recipe_key = curr_recipe_key
        )
    
        self.buildings[building_id] = building
    
        self.grid.mark_occupied_building(
            x=x,
            y=y,
            x_size=building_type.x_size,
            y_size=building_type.y_size,
            building_id=building_id,
        )
    
        self.changed_buildings.add(building_id)
        self.changed_grid = True
    
        return building_id

    def add_supply_link(
        self,
        source_building_id: int,
        target_building_id: int,
        item_key: str,
        required_workers : int,
        amount_per_job: int = 1,
    ) -> int:
        if amount_per_job <= 0:
            raise ValueError("amount_per_job must be positive")

        if source_building_id not in self.buildings:
            raise ValueError(f"Unknown source building: {source_building_id}")
    
        if target_building_id not in self.buildings:
            raise ValueError(f"Unknown target building: {target_building_id}")

        if required_workers > self.avaialble_workers:
            return Error(
                PlacementError.LACKING_WORKERS,
                f'Supply link requires {required_workers} workers, '
                'but only {self.avaialble_workers} avaialble'
            )
    
        supply_link_id = self.get_next_supply_link_id()

        worker_ids = []
        for iw in range(0, required_workers):
            wid = self.get_next_worker_id(),
            self.workers.append(
                Worker(
                    wid,
                    assigned_supply_id=supply_link_id,
                    assigned_building_id=building_id
                    located_building_id=building_id
                    state=WorkerState.ASSIGNED
                ))
            worker_ids.append(wid)

        self.avaialble_workers -= len(workers)
    
        self.supply_links[supply_link_id] = SupplyLink(
            id=supply_link_id,
            source_building_id=source_building_id,
            target_building_id=target_building_id,
            item_key=item_key,
            amount_per_job=amount_per_job,
            worker_ids = worker_ids,
        )
    
        return supply_link_id



