import pygame


class PygameView:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.font = pygame.font.SysFont(None, 20)

        self.info_tab_idx = 0
        self.info_tab_options = [
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

        self.contract_item_idx = None

        # store sorted list of contracts
        # which may be updated time to time
        self._contract_item_list : List[(float, str)] = []



    def advance_info_tab(self, left=False):
        if left:
            self.info_tab_idx = max(0, self.info_tab_idx - 1)
        else:
            self.info_tab_idx += 1
            if self.info_tab_idx >= len(self.info_tab_options):
                self.info_tab_idx = 0


    def draw(self, screen, world) -> None:
        screen.fill((25, 25, 25))

        self._draw_grid(screen, world)
        self._draw_buildings(screen, world)
        self._draw_transport_jobs(screen, world)
        self._draw_info_panel(screen, world)

    def process_up_key(self) -> None:

        if self.info_tab_options[self.info_tab_idx][0] != 'contracts':
            return

        if self.contract_item_idx is None or self.contract_item_idx == 0:
            self.contract_item_idx = len(self._contract_item_list) - 1
        else :
            self.contract_item_idx -= 1


    def process_down_key(self) -> None:

        if self.info_tab_options[self.info_tab_idx][0] != 'contracts':
            return

        if self.contract_item_idx is None:
            self.contract_item_idx = 0

        else:
            self.contract_item_idx += 1
            if self.contract_item_idx >= len(self._contract_item_list):
                self.contract_item_idx = 0

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

    def _draw_info_panel(self, screen, world) -> None:
        x = world.grid.x_size * self.tile_size + 20
        y = 20

        y = self._draw_tab_header(screen, x, y)

        lines = self.info_tab_options[self.info_tab_idx][1](world)

        self._draw_lines(screen, lines, x, y)

    def _draw_tab_header(self, screen, x: int, y: int) -> int:

        for idx, (name, _) in enumerate(self.info_tab_options):
            if self.info_tab_idx == idx:
                text = f"{name}"
                color = (255, 240, 160)
            else:
                text = f"{name}"
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
            f'Available Workers : {world.avaialble_workers}',
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
    
    def _get_contracts_lines(self, world):

        self._update_contract_list(world)

        lines = [
            "Down arrow to select, ",
            "right to increase, "
            "left to decrease",
            "-------",
            "",

        ]
        for idx, (price, ikey) in enumerate(self._contract_item_list):
            amount = world.contracts.items[ikey]

            if self.contract_item_idx is None:
                text = f'{ikey} ({price}) : {amount}'
            elif self.contract_item_idx == idx:
                text = f'-> {ikey} ({price}) : {amount}'
            else:
                text = f'{ikey} ({price}) : {amount}'

            lines.append(text)

        lines.append('')

        lines.append('Bill')

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

