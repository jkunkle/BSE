# model/grid.py

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterator


class TerrainType(Enum):
    GRASS = auto()
    WATER = auto()
    ROCK = auto()
    FOREST = auto()


@dataclass
class Tile:
    terrain: TerrainType = TerrainType.GRASS
    buildable: bool = True
    walkable: bool = True

    building_id : int | None = None
    road_id : int | None = None


@dataclass
class Grid:
    x_size : int
    y_size : int
    _tiles: list[list[Tile]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.x_size <= 0 or self.y_size <= 0:
            raise ValueError("Grid x and y sizes must be positive")

        self.tiles = [
            [Tile() for _ in range(self.x_size)]
            for _ in range(self.y_size)
        ]

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.x_size and 0 <= y < self.y_size

    def require_inside(self, x: int, y: int) -> None:
        if not self.is_inside(x, y):
            raise IndexError(f"Tile ({x}, {y}) is outside the grid")

    def get_tile(self, x: int, y: int) -> Tile:
        self.require_inside(x, y)
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        self.require_inside(x, y)
        self.tiles[y][x] = tile

    def is_area_inside(self, x: int, y: int, x_size: int, y_size: int) -> bool:
        if x_size <= 0 or y_size <= 0:
            return False

        return (
            x >= 0
            and y >= 0
            and x + x_size <= self.x_size
            and y + y_size <= self.y_size
        )

    def iter_area(self, x: int, y: int, x_size: int, y_size: int) -> Iterator[tuple[int, int, Tile]]:
        if not self.is_area_inside(x, y, x_size, y_size):
            raise ValueError(
                f"Area ({x}, {y}, {x_size}, {y_size}) is outside the grid"
            )

        for tile_y in range(y, y + y_size):
            for tile_x in range(x, x + x_size):
                yield tile_x, tile_y, self.tiles[tile_y][tile_x]

    def is_area_free_for_building(self, x: int, y: int, x_size: int, y_size: int) -> bool:
        if not self.is_area_inside(x, y, x_size, y_size):
            return False
    
        for tile_x, tile_y, tile in self.iter_area(x, y, x_size, y_size):
            if tile.building_id is not None or tile.road_id is not None:
                return False
    
        return True

    def is_area_walkable(self, x: int, y: int, x_size: int, y_size: int) -> bool:
        if not self.is_area_inside(x, y, x_size, y_size):
            return False

        return all(
            tile.walkable
            for _, _, tile in self.iter_area(x, y, x_size, y_size)
        )
    
    def mark_occupied_building(self, x: int, y: int, x_size: int, y_size: int, building_id: int):
        for _, _, tile in self.iter_area(x, y, x_size, y_size):
            print (building_id)
            tile.building_id = building_id
            

