# systems/production_system.py

import logging

logger = logging.getLogger(__name__)


class ProductionSystem:
    def update(self, world, dt: float) -> None:
        for building_id in world.buildings.keys():
            self.update_building(world, building_id)

    def update_building(self, world, building_id: int) -> None:
        building = world.buildings[building_id]
        building_type = world.config.building_types[building.building_type_key]

        # This building type cannot produce anything.
        if not building_type.recipe_keys:
            return

        recipe_key = building.current_recipe_key

        recipe = world.config.recipes[recipe_key]

        if building.production_end_time is not None:
            self._check_finish_production(world, building_id, recipe)
        else:
            self._try_start_production(world, building_id, recipe)

    def _try_start_production(self, world, building_id: int, recipe) -> None:
        building = world.buildings[building_id]

        if not building.inventory.can_add_items(recipe.outputs):
            return

        if not building.inventory.can_remove_items(recipe.inputs):
            return

        building.inventory.remove_items(recipe.inputs)

        building.production_start_time = world.time
        building.production_end_time = world.time + recipe.duration

        logger.debug(
            "Building %s started recipe %s; finish_time=%.2f",
            building_id,
            building.current_recipe_key,
            building.production_end_time,
        )

        world.changed_buildings.add(building_id)

    def _check_finish_production(self, world, building_id: int, recipe) -> None:
        building = world.buildings[building_id]

        if world.time < building.production_end_time:
            return

        if not building.inventory.can_add_items(recipe.outputs):
            # This should be rare if you checked space at start.
            # But it may happen later if you allow external changes.
            logger.debug(
                "Building %s finished recipe but output storage is full",
                building_id,
            )
            return

        building.inventory.add_items(recipe.outputs)

        logger.info(
            "Building %s finished recipe %s",
            building_id,
            building.current_recipe_key,
        )

        building.production_start_time = None
        building.production_end_time = None

        world.changed_buildings.add(building_id)

        # Optional: immediately try to start next cycle.
        self._try_start_production(world, building_id, recipe)
