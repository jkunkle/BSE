import pygame
from model.ui_state import UITab
from model.worker import NeedType


class PygameView:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.font = pygame.font.SysFont(None, 20)

        self.info_tab_draw_funcs = [
            ("overview",
            self._get_overview_lines),
            ("buildings",
            self._get_building_lines),
            ("inventories",
            self._get_inventory_lines),
            ("transport",
            self._get_transport_lines),
            ("workers",
            self._get_worker_lines),
            ("contracts",
            self._get_contracts_lines),
        ]



    def draw(self, screen, world, ui_state) -> None:
        screen.fill((25, 25, 25))

        self._draw_grid(screen, world)
        self._draw_buildings(screen, world)
        self._draw_transport_jobs(screen, world)
        self._draw_info_panel(screen, world, ui_state)

    def _draw_grid(self, screen, world) -> None:
        for y in range(world.grid.y_size):
            for x in range(world.grid.x_size):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )

                pygame.draw.rect(screen, (45, 55, 45), rect)
                pygame.draw.rect(screen, (70, 80, 70), rect, 1)

    def _draw_buildings(self, screen, world) -> None:
        for building in world.buildings.values():
            building_type = world.config.building_types[building.building_type_key]

            rect = pygame.Rect(
                building.x * self.tile_size,
                building.y * self.tile_size,
                building_type.x_size * self.tile_size,
                building_type.y_size * self.tile_size,
            )

            color = world.config.building_types[building.building_type_key].color
            if not color:
                color = [255, 0, 0]

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

            label = self.font.render(str(building.id), True, (255, 255, 255))
            screen.blit(label, (rect.x + 4, rect.y + 4))

    def _draw_transport_jobs(self, screen, world) -> None:
        for job in world.transport_jobs.values():
            source = world.buildings[job.source_building_id]
            target = world.buildings[job.target_building_id]

            progress = job.progress(world.time)

            source_x = source.x * self.tile_size + self.tile_size // 2
            source_y = source.y * self.tile_size + self.tile_size // 2

            target_x = target.x * self.tile_size + self.tile_size // 2
            target_y = target.y * self.tile_size + self.tile_size // 2

            current_x = source_x + (target_x - source_x) * progress
            current_y = source_y + (target_y - source_y) * progress

            pygame.draw.circle(
                screen,
                (240, 220, 80),
                (int(current_x), int(current_y)),
                5,
            )

            if job.amount > 0:
                pygame.draw.circle(
                    screen,
                    (0, 0, 0),
                    (int(current_x), int(current_y)),
                    2,
                )

    def _draw_info_panel(self, screen, world, ui_state) -> None:
        x = world.grid.x_size * self.tile_size + 20
        y = 20

        y = self._draw_tab_header(screen, ui_state, x, y)

        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.OVERVIEW:
            lines = self._get_overview_lines(world)
        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.BUILDINGS:
            lines = self._get_building_lines(world)
        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.INVENTORIES:
            lines = self._get_inventory_lines(world)
        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.TRANSPORT:
            lines = self._get_transport_lines(world)
        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.WORKERS:
            lines = self._get_worker_lines(world)
        if ui_state.info_tab_options[ui_state.info_tab_idx] == UITab.CONTRACTS:
            lines = self._get_contracts_lines(world, ui_state)

        #lines = self.info_tab_draw_funcs[ui_state.info_tab_idx][1](world)

        self._draw_lines(screen, lines, x, y)

    def _draw_tab_header(self, screen, ui_state, x: int, y: int) -> int:

        for idx, tab in enumerate(ui_state.info_tab_options):
            if ui_state.info_tab_idx == idx:
                text = f"{tab.value}"
                color = (255, 240, 160)
            else:
                text = f"{tab.value}"
                color = (170, 170, 170)

            rendered = self.font.render(text, True, color)
            screen.blit(rendered, (x, y))
            y += 20

        y += 10
        return y

    def _get_overview_lines(self, world) -> list[str]:

        building_keys = []
        for building_type in  world.config.building_types.values():
            building_keys.append((building_type.key_code, building_type.name))

        building_keys.sort()

        entries = [
            f"Day : {world.day} Time: {world.day_time:.1f}",
            f"$$$ : {world.money}",
            f'Available Workers : {world.get_n_idle_workers()}',
            f"Buildings: {len(world.buildings)}",
            f"Transport jobs: {len(world.transport_jobs)}",
            f"Workers: {len(getattr(world, 'workers', {}))}",
            "",
            "Controls:",
        ]

        for key_code, name in building_keys:
            entries.append(f'{key_code} : {name}')

        entries.append("Left click = place")

        return entries

    def _get_building_lines(self, world) -> list[str]:
        lines = [
            "Buildings",
            "---------",
            "",
        ]

        for building in world.buildings.values():
            lines.append(f"#{building.id} {building.building_type_key}")
            lines.append(f"  pos: ({building.x}, {building.y})")

            current_recipe_key = getattr(building, "current_recipe_key", None)
            if current_recipe_key is not None:
                lines.append(f"  recipe: {current_recipe_key}")

            production_end_time = getattr(building, "production_end_time", None)
            if production_end_time is not None:
                lines.append(f"  producing until: {production_end_time:.1f}")
            else:
                lines.append("  production: idle")

            lines.append("")

        return lines

    def _get_inventory_lines(self, world) -> list[str]:
        lines = [
            "Inventories",
            "-----------",
            "",
        ]

        for building in world.buildings.values():
            lines.append(f"#{building.id} {building.building_type_key}")

            for item_key, amount in building.inventory.amounts.items():
                limit = building.inventory.limits[item_key]
                lines.append(f"  {item_key}: {amount}/{limit}")

            lines.append("")

        return lines

    def _get_transport_lines(self, world) -> list[str]:
        lines = [
            "Transport jobs",
            "--------------",
            "",
        ]

        if not world.transport_jobs:
            lines.append("No active transport jobs")
            return lines

        for job in world.transport_jobs.values():
            lines.append(f"Job #{job.job_id}")
            lines.append(f"  from: #{job.source_building_id}")
            lines.append(f"  to: #{job.target_building_id}")

            item_key = getattr(job, "item_key", None)
            amount = getattr(job, "amount", 0)

            if item_key is not None and amount > 0:
                lines.append(f"  item: {item_key} x{amount}")
            else:
                lines.append("  empty movement")

            progress = job.progress(world.time)
            lines.append(f"  progress: {progress * 100:.0f}%")
            lines.append("")

        return lines


    def _get_worker_lines(self, world) -> list[str]:
        lines = [
            "Workers",
            "-------",
            "",
        ]

        workers = getattr(world, "workers", {})

        if not workers:
            lines.append("No workers")
            return lines

        n_total = len(world.workers)
        n_idle = world.get_n_idle_workers()
        sum_food = 0
        sum_rec = 0
        sum_sleep = 0
        for w in workers.values():
            sum_food += w.needs[NeedType.FOOD]
            sum_rec += w.needs[NeedType.RECREATION]
            sum_sleep += w.needs[NeedType.SLEEP]

        avg_food = sum_food/n_total
        avg_rec = sum_rec/n_total
        avg_sleep = sum_sleep/n_total

        lines.append(f'Active: {n_total-n_idle}, Idle: {n_idle}, Total : {n_total}')
        lines.append(f'Avg Food : {avg_food}')
        lines.append(f'Avg Recreation : {avg_rec}')
        lines.append(f'Avg Sleep : {avg_sleep}')

        lines.append('-------')

        for worker in workers.values():

            lines.append(f"Worker #{worker.id}")
            lines.append(f"  state: {worker.state}")

            current_building_id = getattr(worker, "current_building_id", None)
            current_job_id = getattr(worker, "current_job_id", None)

            if current_building_id is not None:
                lines.append(f"  at building: #{current_building_id}")
            else:
                lines.append("  in transit")

            if current_job_id is not None:
                lines.append(f"  job: #{current_job_id}")

            lines.append("")

        return lines
    
    def _get_contracts_lines(self, world, ui_state):

        lines = [
            "Down arrow to select, ",
            "right to increase, "
            "left to decrease",
            "-------",
            "",

        ]

        contract_ids_list = world.get_contract_ids_sorted_by_price()

        for cid in contract_ids_list:

            name = world.contracts[cid].item_key
            price = world.contracts[cid].price
            amount = world.contracts[cid].amount

            if ui_state.selected_contract_id is None:
                text = f'{name} ({price}) : {amount}'
            elif ui_state.selected_contract_id == cid:
                text = f'-> {name} ({price}) : {amount}'
            else:
                text = f'{name} ({price}) : {amount}'

            lines.append(text)

        lines.append('')
        
        if world.export_completed:

            lines.append('Bill')
            lines.append('-------')

            day_total = 0
            for b in world.bill:
                day_total += b.get_total()
                lines.append(f'{b.name} ({b.amount}) * {b.price}  = {b.get_total()}')

            lines.append('-------')
            lines.append(f'Day Total : {day_total}')


        return lines


    def _draw_lines(self, screen, lines: list[str], x: int, y: int) -> None:
        line_height = 20
        max_y = screen.get_height() - line_height

        for line in lines:
            if y > max_y:
                text = self.font.render("...", True, (230, 230, 230))
                screen.blit(text, (x, y))
                break

            text = self.font.render(line, True, (230, 230, 230))
            screen.blit(text, (x, y))
            y += line_height
    #def _draw_info_panel(self, screen, world) -> None:
    #    x = world.grid.x_size * self.tile_size + 20
    #    y = 20

    #    lines = [
    #        f"Time: {world.time:.1f}",
    #        f"Buildings: {len(world.buildings)}",
    #        f"Transport jobs: {len(world.transport_jobs)}",
    #        "",
    #    ]

    #    for building in world.buildings.values():
    #        lines.append(
    #            #f"#{building.id} {building.building_type_key} {building.state}"
    #            f"#{building.id} {building.building_type_key}"
    #        )

    #        for item_key, amount in building.inventory.amounts.items():
    #            limit = building.inventory.limits[item_key]
    #            lines.append(f"  {item_key}: {amount}/{limit}")

    #        #if building.active_production is not None:
    #        #    progress = building.active_production.progress(world.time)
    #        #    lines.append(f"  production: {progress * 100:.0f}%")
    #        lines.append(f"  production: 0%")

    #        lines.append("")

    #    for line in lines:
    #        text = self.font.render(line, True, (230, 230, 230))
    #        screen.blit(text, (x, y))
    #        y += 20

