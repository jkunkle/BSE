import pygame


class PygameView:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.font = pygame.font.SysFont(None, 20)

    def draw(self, screen, world) -> None:
        screen.fill((25, 25, 25))

        self._draw_grid(screen, world)
        self._draw_buildings(screen, world)
        self._draw_transport_jobs(screen, world)
        self._draw_info_panel(screen, world)

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

            color = self._get_building_color(building.building_type_key)
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

    def _draw_info_panel(self, screen, world) -> None:
        x = world.grid.x_size * self.tile_size + 20
        y = 20

        lines = [
            f"Time: {world.time:.1f}",
            f"Buildings: {len(world.buildings)}",
            f"Transport jobs: {len(world.transport_jobs)}",
            "",
        ]

        for building in world.buildings.values():
            lines.append(
                #f"#{building.id} {building.building_type_key} {building.state}"
                f"#{building.id} {building.building_type_key}"
            )

            for item_key, amount in building.inventory.amounts.items():
                limit = building.inventory.limits[item_key]
                lines.append(f"  {item_key}: {amount}/{limit}")

            #if building.active_production is not None:
            #    progress = building.active_production.progress(world.time)
            #    lines.append(f"  production: {progress * 100:.0f}%")
            lines.append(f"  production: 0%")

            lines.append("")

        for line in lines:
            text = self.font.render(line, True, (230, 230, 230))
            screen.blit(text, (x, y))
            y += 20

    def _get_building_color(self, building_type_key: str) -> tuple[int, int, int]:
        if building_type_key == "wood_harvester":
            return (60, 130, 60)

        if building_type_key == "sawmill":
            return (140, 95, 45)

        if building_type_key == "warehouse":
            return (90, 90, 130)

        return (120, 120, 120)
