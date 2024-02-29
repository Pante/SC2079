from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List

import numpy as np

from pathfinding.world.primitives import Direction, Point, Vector


class World:
    """
    The actual size of the world in centimetres.
    """
    __actual_size = 200

    """
    A world. True clearance computation is optimized for rectangular/square obstacles.

    A Brushfire-like algorithm should be used if irregular shaped obstacles are allowed.

    See https://harablog.wordpress.com/2009/01/29/clearance-based-pathfinding/
    """

    def __init__(self, size: int, robot: Robot, obstacles: List[Obstacle]):
        self.size = size
        self.grid = np.full((size, size), -1, dtype=np.int32)
        self.robot = robot
        self.obstacles = obstacles

        assert self.__inside(robot)
        assert all(map(lambda obstacle: self.__inside(obstacle), self.obstacles))

        self.__annotate_obstacles()

    def __inside(self, entity: Entity) -> bool:
        return (0 <= entity.south_west.x < self.size and
                0 <= entity.north_east.x < self.size and
                0 <= entity.south_west.y < self.size and
                0 <= entity.north_east.y < self.size)

    def __annotate_obstacles(self: World) -> None:
        for obstacle in self.obstacles:
            for x in range(obstacle.south_west.x, obstacle.north_east.x + 1):
                for y in range(obstacle.south_west.y, obstacle.north_east.y + 1):
                    self.grid[x, y] = 0

    def contains(self, entity: Entity) -> bool:
        if not self.__inside(entity):
            return False

        x = entity.south_west.x
        y = entity.south_west.y

        if self.grid[x, y] == -1:
            self.grid[x, y] = self.__compute_true_clearance(x, y)

        return entity.clearance <= self.grid[x, y]

    def __compute_true_clearance(self: World, x: int, y: int) -> int:
        clearance = self.size - x
        for obstacle in self.obstacles:
            vector = obstacle.south_west
            if vector.x < x or vector.y < y:
                continue

            next_clearance = max(vector.x - x, vector.y - y)
            if vector.x - x < next_clearance:
                clearance = next_clearance

        return clearance

    @property
    def cell_size(self) -> int:
        return self.__actual_size // self.size


@dataclass
class Entity(ABC):
    direction: Direction
    south_west: Point
    north_east: Point

    def __post_init__(self):
        assert 0 <= self.south_west.x <= self.north_east.x
        assert 0 <= self.south_west.y <= self.north_east.y
        assert (self.north_east.y - self.south_west.y) == (self.north_east.x - self.south_west.x)

    @property
    def vector(self) -> Vector:
        return Vector(self.direction, self.south_west.x, self.south_west.y)

    @property
    def north_west(self) -> Point:
        return Point(self.south_west.x, self.north_east.y)

    @property
    def south_east(self) -> Point:
        return Point(self.north_east.x, self.south_west.y)

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


@dataclass(unsafe_hash=True)
class Obstacle(Entity):
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36
        super().__post_init__()
