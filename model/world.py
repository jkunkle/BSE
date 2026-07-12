from utils.error import Error
from utils.error_type import PlacementError

from model.grid import Grid
from model.building import Building, Door
from model.inventory import Inventory
from model.supply_link import SupplyLink
from model.worker import Worker, WorkerState
from model.contract import Contract


class World():

    def __init__(self, config_store, workers=0, x=50, y=50, money=1000):

        self._x_max = x
        self._y_max = y


        self.grid = Grid(x, y)
        self.buildings : dict[int, Building] = {}
        self.config = config_store
        self.transport_jobs = {}
        self.supply_links: dict[int, SupplyLink] = {}
        self.workers : dict[int, Worker] = {}
        self.contracts = dict[int, Contract] = {}

        self._next_building_id: int = 0
        self._next_supply_link_id: int = 0
        self._next_transport_job_id: int = 0
        self._next_worker_id: int = 0
        self._next_contract_id: int = 0

        self.changed_buildings = set()
        self.changed_transport_jobs = set()
        changed_contracts: set[int] = set()
        self.changed_grid = False
        self.day = 0
        self.day_time = 0
        self.time = 0
        self.money = money
        self.avaialble_workers = workers
        self.speed = 500

        self.minutes_in_day = 200
        self.export_day_time = 100

        self._init_contracts()
        self.contract_list_order : List[int] = []
        self.contract_item_key = None

    def __repr__(self):

        info_str = ''
        for building in self.buildings:
            info_str += building.__repr__() + '\n'

        return info_str

    def _init_contracts(self):

        for ikey, item in self.config.items.items():

            cid = self.get_next_contract_id()

            self.contracts[cid] = Contract(
                id = cid,
                item_key=ikey,
                amount=0,
                price=item.price
            )
    def get_contract_ids_sorted_by_price(self) -> list[int]:
        return sorted(
            self.contracts.keys(),
            key=lambda contract_id: (
                -self.contracts[contract_id].price,
                self.contracts[contract_id].item_key,
            ),
        )

    def increase_speed(self):
        self.speed += 100

    def decrease_speed(self):
        if self.speed > 100:
            self.speed -= 100

    def advance_time(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.time += dt
        self.day_time += dt
        if self.day_time >= self.minutes_in_day:
            self.day += 1
            self.day_time = 0

    def get_next_building_id(self):

        self._next_building_id +=1 

        return self._next_building_id - 1

    def get_next_supply_link_id(self) -> int:
    
        self._next_supply_link_id += 1
    
        return self._next_supply_link_id - 1

    def get_next_transport_job_id(self) -> int:
    
        self._next_transport_job_id += 1
    
        return self._next_transport_job_id - 1

    def get_next_worker_id(self) -> int:
    
        self._next_worker_id += 1
    
        return self._next_worker_id - 1

    def get_next_contract_id(self) -> int:
    
        self._next_contract_id += 1
    
        return self._next_contract_id - 1

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

        if 'housing' not in building_type.capabilities:
            if building_type.workers > self.avaialble_workers:
                return Error(
                    PlacementError.LACKING_WORKERS,
                    f'Building requires {building_type.workers}, '
                    f'but only {self.avaialble_workers} avaialble'
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

        cost = self.config.building_types[building_type_key].cost
        if building_type_key == 'export':
            already_exists = False
            for b in self.buildings.values():
                if b.building_type_key == 'export':
                    already_exists = True
                    break

            if not already_exists:
                cost = 0
        
        if cost > self.money:
            return Error(
                PlacementError.LACKING_FUNDING,
                f'Building cost {cost}, exceeds available funds!'
            )

        self.money -= cost

        # FIXME - a bit of a hack
        worker_ids = []
        if 'housing' in building_type.capabilities:
            self.avaialble_workers += building_type.workers
        else:
            for iw in range(0, building_type.workers):
                wid = self.get_next_worker_id()
                wkr = Worker(
                        wid,
                        assigned_building_id=building_id,
                        state=WorkerState.ASSIGNED
                    )
                self.workers[wid] = wkr

                worker_ids.append(wid)

            self.avaialble_workers -= len(worker_ids)

    
        curr_recipe_key = None
        if building_type.recipe_keys:
            curr_recipe_key = building_type.recipe_keys[0]

        building = Building(
            id=building_id,
            building_type_key=building_type_key,
            x=x,
            y=y,
            x_size=building_type.x_size,
            y_size=building_type.y_size,
            doors = doors,
            worker_ids = worker_ids,
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

    def delete_building(self, building_id):

        building = self.buildings[building_id]

        jobs_to_remove = []
        for jid, job in self.transport_jobs:
            if (
                job.source_building_id == building_id 
                or job.target_building_id == building_id
            ):
                jobs_to_remove.append(jid)

        for jid in jobs_to_remove:
            del self.transport_jobs[jid]
            

        link_ids_to_remove = []
        for link_id, supply_link in self.supply_links.items():
            if (
                supply_link.source_building_id == building_id 
                or supply_link.target_building_id == building_id
            ):
                link_ids_to_remove.append(link_id)

        for link_id in link_ids_to_remove:
            self.delete_supply_link(link_id)

        for wid in building.worker_ids:
            self.free_worker(wid)

        del self.buildings[building_id]



    def delete_supply_link(self, link_id):

        supply_link = self.supply_links[link_id]

        for wid in supply_link.worker_ids:
            self.free_worker(wid)

        del self.supply_links[link_id]

    def free_worker(self, wid):

        del self.workers[wid]
        self.avaialble_workers += 1

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
            wkr = Worker(
                    wid,
                    assigned_supply_id=supply_link_id,
                    assigned_building_id=source_building_id,
                    located_building_id=source_building_id,
                    state=WorkerState.ASSIGNED,
                )
            self.workers[wid] = wkr
            worker_ids.append(wid)

        self.avaialble_workers -= len(worker_ids)
    
        self.supply_links[supply_link_id] = SupplyLink(
            id=supply_link_id,
            source_building_id=source_building_id,
            target_building_id=target_building_id,
            item_key=item_key,
            amount_per_job=amount_per_job,
            worker_ids = worker_ids,
        )

        print ('Added supply link')
        print (self.supply_links[supply_link_id])
    
        return supply_link_id



