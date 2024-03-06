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
    A world. Clearance computation is optimized for rectangular/square obstacles.
    """

    def __init__(self, size: int, robot: Robot, obstacles: List[Obstacle]):
        self.size = size
        self.grid = np.full((size, size), True)
        self.obstacles = obstacles
        self.robot = robot

        assert all(map(lambda obstacle: self.__inside(obstacle), self.obstacles))
        self.__annotate_grid()

        assert self.__inside(robot)

    def __inside(self, entity: Entity) -> bool:
        return (0 <= entity.south_west.x < self.size and
                0 <= entity.south_west.y < self.size and
                0 <= entity.north_east.x < self.size and
                0 <= entity.north_east.y < self.size)

    def __annotate_grid(self: World) -> None:
        self.grid[0:self.robot.north_length, :] = False
        self.grid[:, -self.robot.east_length:] = False
        self.grid[-self.robot.south_length:, :] = False
        self.grid[:, 0:self.robot.west_length] = False

        for obstacle in self.obstacles:
            west_x = max(obstacle.south_west.x - self.robot.clearance, 0)
            east_x = min(obstacle.north_east.x + self.robot.clearance + 1, self.size)
            south_y = max(obstacle.south_west.y - self.robot.clearance, 0)
            north_y = min(obstacle.north_east.y + self.robot.clearance + 1, self.size)

            self.grid[west_x:east_x, south_y:north_y] = False

    def contains(self, centre: Point | Vector) -> bool:
        return (0 <= centre.x < self.size and 0 <= centre.y < self.size) and self.grid[centre.x, centre.y]

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
        self.centre = Point(self.north_east.x // 2, self.north_east.y // 2)
        self.north_length = self.north_east.y // 2
        self.east_length = self.north_east.x // 2
        self.south_length = self.north_east.y // 2
        self.west_length = self.north_east.x // 2

    @property
    def clearance(self):
        # Assumes that height & width are the same
        return self.north_east.y - self.south_west.y + 1

    @property
    def vector(self) -> Vector:
        return Vector(self.direction, self.centre.x, self.centre.y)

    @property
    def north_west(self) -> Point:
        return Point(self.south_west.x, self.north_east.y)

    @property
    def south_east(self) -> Point:
        return Point(self.north_east.x, self.south_west.y)


@dataclass(unsafe_hash=True)
class Obstacle(Entity):
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36
        super().__post_init__()


@dataclass
class Robot(Entity):
    def __post_init__(self):
        super().__post_init__()
