import logging
from math import sqrt

from model.transport_job import TransportJob, TransportJobState

logger = logging.getLogger(__name__)


class TransportSystem:
    def __init__(self, transport_speed_tiles_per_second: float = 3.0):
        if transport_speed_tiles_per_second <= 0:
            raise ValueError("transport_speed_tiles_per_second must be positive")

        self.transport_speed_tiles_per_second = transport_speed_tiles_per_second

    def update(self, world, dt: float) -> None:
        self.complete_finished_jobs(world)
        self.create_jobs_for_worker_return(world)
        self.create_jobs_from_supply_links(world)

    def complete_finished_jobs(self, world) -> None:
        for job_id, job in list(world.transport_jobs.items()):
            if job.state != TransportJobState.IN_TRANSIT:
                continue

            if world.time < job.finish_time:
                continue

            self._complete_job(world, job_id)

    def create_jobs_from_supply_links(self, world) -> None:
        for supply_link in world.supply_links.values():
            self._try_create_job_for_supply_link(world, supply_link)

    def create_jobs_for_worker_return(self, world) -> None:
        for supply_link in world.supply_links.values():
            
            for supply_worker_id in supply_link.worker_ids:
                sworker = world.workers[supply_worker_id] 
                if sworker.state != MOVING:
                    self._try_create_job_for_worker_return(world, supply_link, sworker)

    def _try_create_job_for_supply_link(self, world, supply_link) -> None:

        source = world.buildings[supply_link.source_building_id]
        target = world.buildings[supply_link.target_building_id]

        item_key = supply_link.item_key
        amount = supply_link.amount_per_job

        if not source.inventory.can_remove(item_key, amount):
            return

        if not target.inventory.can_add(item_key, amount):
            return

        worker_at_source_id = None
        for w in self.workers:
            if w.located_building_id is not None and w.located_building_id == supply_link.source_building_id:
                worker_at_source_id = w.id
                break

        if worker_at_source_id is None:
            return
        
        print ('Worker available!')
        # Important: reserve by removing from source immediately.
        # This prevents the same item being assigned to many jobs.
        source.inventory.remove(item_key, amount)

        duration = self._calculate_transport_duration(world, source, target)

        job_id = world.get_next_transport_job_id()

        job = TransportJob(
            job_id=job_id,
            source_building_id=source.id,
            target_building_id=target.id,
            item_key=item_key,
            amount=amount,
            worker=worker_at_source_id,
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

        source = world.buildings[supply_link.source_building_id]
        target = world.buildings[supply_link.target_building_id]

        if worker.located_building_id == supply_link.target_building_id:
        
            duration = self._calculate_transport_duration(world, target, source)

            job_id = world.get_next_transport_job_id()

            job = TransportJob(
                job_id=job_id,
                source_building_id=target.id,
                target_building_id=source.id,
                item_key=None,
                amount=0,
                worker=worker.id,
                start_time=world.time,
                finish_time=world.time + duration,

            )

        world.transport_jobs[job_id] = job

        world.changed_transport_jobs.add(job_id)

        logger.info(
            "Created Return job %s from building %s to building %s, finish_time=%.2f",
            job_id,
            target.id,
            source.id,
            job.finish_time,
        )

    def _complete_job(self, world, job_id: int) -> None:
        job = world.transport_jobs[job_id]
        target = world.buildings[job.target_building_id]

        if job.amount > 0
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

        job.state = TransportJobState.COMPLETED
        world.workers[job.worker.id].state = WorkerState.ASSIGNED
        world.workers[job.worker.id].located_building_id = target.id

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
