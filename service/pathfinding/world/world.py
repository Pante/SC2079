from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import List

import numpy as np

from pathfinding.grid import Objective
from pathfinding.world.primitives import Direction, Point, Vector


class World:
    """
    The actual size of the world in centimetres.
    """
    __actual_size = 200

    """
    A world. Clearance computation is optimized for rectangular/square obstacles.
    """

    def __init__(self, size: int, robot: Robot, obstacles: List[Obstacle]):
        self.size = size
        self.grid = np.full((size, size), True)
        self.robot = robot
        self.obstacles = obstacles

        assert self.__inside(robot)
        assert all(map(lambda obstacle: self.__inside(obstacle), self.obstacles))

        self.__annotate_obstacles()

    def __inside(self, entity: Entity) -> bool:
        return (0 <= entity.south_west.x < self.size and
                0 <= entity.south_west.y < self.size and
                0 <= entity.north_east.x < self.size and
                0 <= entity.north_east.y < self.size)

    def __annotate_obstacles(self: World) -> None:
        for obstacle in self.obstacles:
            west_x = obstacle.south_west.x - self.robot.east_length
            east_x = obstacle.north_east.x + self.robot.west_length + 1
            south_y = obstacle.south_west.y - self.robot.north_length
            north_y = obstacle.north_east.y + self.robot.south_length + 1

            self.grid[west_x:east_x, south_y:north_y] = False

    def contains(self, entity: Robot | Objective) -> bool:
        return self.__inside(entity) and self.grid[entity.centre.x, entity.centre.y]

    @property
    def cell_size(self) -> int:
        return self.__actual_size // self.size


@dataclass
class Entity(ABC):
    direction: Direction
    south_west: Point
    north_east: Point
    centre: Point = field(init=False)

    def __post_init__(self):
        assert 0 <= self.south_west.x <= self.north_east.x
        assert 0 <= self.south_west.y <= self.north_east.y
        assert (self.north_east.y - self.south_west.y) == (self.north_east.x - self.south_west.x)
        self.centre = Point(
            self.south_west.x + (self.north_east.x - self.south_west.x) // 2,
            self.south_west.y + (self.north_east.y - self.south_west.y) // 2,
        )

    @property
    def north_length(self) -> int:
        return self.north_east.y - self.centre.y

    @property
    def east_length(self) -> int:
        return self.north_east.x - self.centre.x

    @property
    def south_length(self) -> int:
        return self.centre.y - self.south_west.y

    @property
    def west_length(self) -> int:
        return self.centre.x - self.south_west.x

    # @property
    # def vector(self) -> Vector:
    #     return Vector(self.direction, self.south_west.x, self.south_west.y)

    # @property
    # def clearance(self):
    #     # Assumes that height & width are the same
    #     return self.north_east.y - self.south_west.y + 1


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
