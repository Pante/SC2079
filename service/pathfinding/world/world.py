from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List

import numpy as np

from pathfinding.world.primitives import Direction, Point, Vector

# The dimensions of the square grid (in number of cells).
GRID_SIZE = 40
# The length & width of each square grid cell (in cm).
GRID_CELL_SIZE = 5


class World:
    """
    A world. It applies a Brushfire-like algorithm to compute the true clearance of all cells in a grid.

    See https://harablog.wordpress.com/2009/01/29/clearance-based-pathfinding/
    """

    def __init__(self, width: int, height: int, robot: Robot, obstacles: List[Obstacle]):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), -1, dtype=np.int32)
        self.robot = robot
        self.obstacles = obstacles

        assert self.__inside(robot)
        assert all(map(lambda obstacle: self.__inside(obstacle), self.obstacles))

        self.__annotate_obstacles()
        self.__annotate_true_clearance()
        print(self.grid)

    def __inside(self, entity: Entity) -> bool:
        return (0 <= entity.south_west.x < self.width and
                0 <= entity.north_east.x < self.width and
                0 <= entity.south_west.y < self.height and
                0 <= entity.north_east.y < self.height)

    def __annotate_obstacles(self: World) -> None:
        for obstacle in self.obstacles:
            for x in range(obstacle.south_west.x, obstacle.north_east.x + 1):
                for y in range(obstacle.south_west.y, obstacle.north_east.y + 1):
                    self.grid[x, y] = 0

    def __annotate_true_clearance(self: World) -> None:
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.grid[x, y] != 0:
                    self.grid[x, y] = self.__compute_true_clearance(x, y)

    def __compute_true_clearance(self: World, x: int, y: int) -> int:
        max_size = min(self.width, self.height)
        for size in range(0, max_size):
            min_x = max(x - size, 0)
            max_x = min(x + size + 1, self.width)
            min_y = max(y - size, 0)
            max_y = min(y + size + 1, self.height)

            for box_x in range(min_x, max_x):
                for box_y in range(min_y, max_y):
                    if self.grid[box_x, box_y] == 0:
                        return size

        return max_size

    def contains(self, entity: Entity) -> bool:
        return self.__inside(entity) and entity.clearance <= self.grid[entity.south_west.x, entity.south_west.y]


@dataclass
class Entity(ABC):
    direction: Direction
    south_west: Point
    north_east: Point

    def __post_init__(self):
        assert 0 <= self.south_west.x <= self.north_east.x
        assert 0 <= self.south_west.y <= self.north_east.y
        assert (self.north_east.y - self.south_west.y) == (self.north_east.x - self.south_east.x)

    @property
    def vector(self) -> Vector:
        return Vector(self.direction, self.south_west.x, self.south_west.y)

    @property
    def north_west(self) -> Point:
        return Point(self.north_east.x, self.south_west.y)

    @property
    def south_east(self) -> Point:
        return Point(self.south_west.x, self.north_east.y)

    @property
    def clearance(self):
        # Assumes that height & width are the same
        return self.north_east.y - self.south_west.y + 1


@dataclass
class Robot(Entity):
    direction: Direction
    south_west: Point
    north_east: Point


@dataclass
class Cell(Entity):
    def set_vector(self, vector: Vector) -> Cell:
        clearance = self.clearance - 1

        self.direction = vector.direction
        self.south_west = Point(vector.x, vector.y)
        self.north_east = Point(vector.x + clearance, vector.y + clearance)
        return self

    def set_point(self, point: Point) -> Cell:
        clearance = self.clearance - 1

        self.south_west = point
        self.north_east = Point(point.x + clearance, point.y + clearance)
        return self


@dataclass
class Obstacle(Entity):
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36
        super().__post_init__()
