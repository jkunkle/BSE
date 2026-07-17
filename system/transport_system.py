import logging
from math import sqrt

from model.transport_job import TransportJob, TransportJobState
from model.worker import WorkerState, NeedType

logger = logging.getLogger(__name__)


class TransportSystem:
    def __init__(
        self,
        transport_speed_tiles_per_second: float = 3.0,
        rest_need_threshold: float = 0.95,
    ):
        if transport_speed_tiles_per_second <= 0:
            raise ValueError("transport_speed_tiles_per_second must be positive")

        self.transport_speed_tiles_per_second = transport_speed_tiles_per_second
        self.rest_need_threshold = rest_need_threshold
        self.food_need_per_vegetable = 0.5

    def update(self, world, dt: float) -> None:
        self.complete_finished_jobs(world)
        self.create_jobs_for_worker_activities(world)
        self.create_jobs_for_worker_return(world)
        self.create_jobs_from_supply_links(world)

    def complete_finished_jobs(self, world) -> None:
        for job_id, job in list(world.transport_jobs.items()):
            if job.state != TransportJobState.IN_TRANSIT:
                continue

            if world.time < job.finish_time:
                continue

            self._complete_job(world, job_id)

    def create_jobs_for_worker_activities(self, world) -> None:

        for worker in world.workers.values():
            if worker.state == WorkerState.RESTING:
                self._try_finish_resting(world, worker)
                continue

            if worker.state != WorkerState.ASSIGNED:
                continue

            if self._is_mid_production(world, worker):
                continue

            if worker.needs[NeedType.FOOD] < 0.5:
                self._try_create_market_job(world, worker)
                continue
            if worker.needs[NeedType.SLEEP] < 0.5:
                self._try_create_return_home_job(world, worker)
                continue
            if worker.needs[NeedType.RECREATION] < 0.5:
                self._try_create_return_home_job(world, worker)
                continue

    def _is_mid_production(self, world, worker) -> bool:
        building = world.buildings.get(worker.assigned_building_id)
        if building is None:
            return False

        return building.production_end_time is not None

    def _try_finish_resting(self, world, worker) -> None:
        if worker.needs[NeedType.SLEEP] < self.rest_need_threshold:
            return
        if worker.needs[NeedType.RECREATION] < self.rest_need_threshold:
            return

        origin = world.buildings[worker.home_building_id]
        destination = world.buildings[worker.assigned_building_id]
        self.create_empty_transport_job(world, worker, origin, destination)


    def create_jobs_from_supply_links(self, world) -> None:
        for supply_link in world.supply_links.values():
            self._try_create_job_for_supply_link(world, supply_link)

    def create_jobs_for_worker_return(self, world) -> None:
        for supply_link in world.supply_links.values():
            for supply_worker_id in supply_link.worker_ids:
                sworker = world.workers[supply_worker_id] 
                self._try_create_job_for_worker_return(world, supply_link, sworker)

    def _try_create_return_home_job(self, world, worker) -> None:
        origin = world.buildings[worker.located_building_id]
        destination = world.buildings[worker.home_building_id]
        self.create_empty_transport_job(world, worker, origin, destination)

    def _try_create_market_job(self, world, worker) -> None:

        # FIXME -- may need to update to handle multiple markets
        market = None
        for b in world.buildings.values():
            if b.building_type_key == 'market':
                market = b
                break

        if market is None:
            logger.warning('Market not found!')
            return

        if worker.located_building_id == market.id:
            return

        origin = world.buildings[worker.located_building_id]
        destination = market

        self.create_empty_transport_job(world, worker, origin, destination)


    def _try_create_job_for_supply_link(self, world, supply_link) -> None:

        source = world.buildings[supply_link.source_building_id]
        target = world.buildings[supply_link.target_building_id]

        item_key = supply_link.item_key
        amount = supply_link.amount_per_job

        if not source.inventory.can_remove(item_key, amount):
            return

        if not target.inventory.can_add(item_key, amount):
            return

        if not supply_link.worker_ids:
            raise ValueError('Supply Link must provide workers')
            return

        
        chosen_worker = None
        for wid in supply_link.worker_ids:
            worker = world.workers[wid]

            if worker.located_building_id == supply_link.source_building_id:
                chosen_worker = wid
                break

        if chosen_worker is None:
            return
        
        # Important: reserve by removing from source immediately.
        # This prevents the same item being assigned to many jobs.
        source.inventory.remove(item_key, amount)

        duration = self._calculate_transport_duration(world, source, target)

        job_id = world.get_next_transport_job_id()

        world.workers[chosen_worker].assigned_job_id = job_id
        world.workers[chosen_worker].located_building_id = None
        world.workers[chosen_worker].state = WorkerState.MOVING

        job = TransportJob(
            job_id=job_id,
            source_building_id=source.id,
            target_building_id=target.id,
            item_key=item_key,
            amount=amount,
            worker_id=chosen_worker,
            start_time=world.time,
            finish_time=world.time + duration,

        )

        world.transport_jobs[job_id] = job

        world.changed_buildings.add(source.id)
        world.changed_transport_jobs.add(job_id)

        logger.info(
            "Created transport job %s: %s x%s from building %s to building %s, finish_time=%.2f",
            job_id,
            item_key,
            amount,
            source.id,
            target.id,
            job.finish_time,
             
        )

    def _try_create_job_for_worker_return(self, world, supply_link, worker) -> None:

        if worker.state != WorkerState.ASSIGNED:
            return;

        if worker.located_building_id != supply_link.target_building_id:
            return

        origin = world.buildings[supply_link.target_building_id]
        destination = world.buildings[supply_link.source_building_id]

        self.create_empty_transport_job(world, worker, origin, destination)

    def create_empty_transport_job(self, world, worker, origin, destination):

        duration = self._calculate_transport_duration(world, origin, destination)

        job_id = world.get_next_transport_job_id()

        job = TransportJob(
            job_id=job_id,
            source_building_id=origin.id,
            target_building_id=destination.id,
            item_key=None,
            amount=0,
            worker_id=worker.id,
            start_time=world.time,
            finish_time=world.time + duration,

        )

        world.transport_jobs[job_id] = job

        worker.state = WorkerState.MOVING
        worker.located_building_id = None
        worker.assigned_job_id = job_id

        world.changed_transport_jobs.add(job_id)

        logger.info(
            "Created Empty job %s from building %s to building %s, finish_time=%.2f",
            job_id,
            origin.id,
            destination.id,
            job.finish_time,
        )

    def _complete_job(self, world, job_id: int) -> None:
        job = world.transport_jobs[job_id]
        target = world.buildings[job.target_building_id]

        if job.amount > 0:
            if not target.inventory.can_add(job.item_key, job.amount):
                # In the first design this should rarely happen, because we checked target space
                # before creating the job. But it may happen if other systems add items meanwhile.
                logger.warning(
                    "Transport job %s arrived, but target building %s has no space for %s x%s",
                    job_id,
                    target.id,
                    job.item_key,
                    job.amount,
                )
                return

            target.inventory.add(job.item_key, job.amount)

        if target.building_type_key == 'market':
            eating_worker = world.workers[job.worker_id]
            if eating_worker.needs[NeedType.FOOD] < 0.5:
                #FIXME -- only one type of food consumed
                if target.inventory.can_remove('vegetables', 1):
                    target.inventory.remove('vegetables', 1)
                    eating_worker.needs[NeedType.FOOD] += self.food_need_per_vegetable
                else:
                    logger.warning(
                        "Transport job %s arrived, but market building %s has no supply",
                        job_id,
                        target.id,
                    )


        job.state = TransportJobState.COMPLETED

        worker = world.workers[job.worker_id]
        worker.located_building_id = target.id

        if target.id == worker.home_building_id and (
            worker.needs[NeedType.SLEEP] < self.rest_need_threshold
            or worker.needs[NeedType.RECREATION] < self.rest_need_threshold
        ):
            worker.state = WorkerState.RESTING
        else:
            worker.state = WorkerState.ASSIGNED

        world.changed_buildings.add(target.id)
        world.changed_transport_jobs.add(job_id)

        logger.info(
            "Completed transport job %s: delivered %s x%s to building %s",
            job_id,
            job.item_key,
            job.amount,
            target.id,
        )

        # For now, remove completed jobs from active world state.
        del world.transport_jobs[job_id]

    def _calculate_transport_duration(self, world, source, target) -> float:
        distance = self._distance_between_buildings(source, target)
        return distance / self.transport_speed_tiles_per_second

    def _distance_between_buildings(self, source, target) -> float:
        dx = target.x - source.x
        dy = target.y - source.y
        return max(1.0, sqrt(dx * dx + dy * dy))
