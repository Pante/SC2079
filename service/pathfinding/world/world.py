from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

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

    def __init__(self, size: int, robot: Robot, obstacles: list[Obstacle]):
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
        edge_error = round(-1 // self.cell_size)
        obstacle_error = round(6 // self.cell_size)

        self.grid[0:(self.robot.north_length + edge_error), :] = False
        self.grid[:, -(self.robot.east_length + edge_error):] = False
        self.grid[-(self.robot.south_length + edge_error):, :] = False
        self.grid[:, 0:(self.robot.west_length + edge_error)] = False

        for obstacle in self.obstacles:
            west_x = max(obstacle.south_west.x - self.robot.west_length - obstacle_error, 0)
            east_x = min(obstacle.north_east.x + self.robot.east_length + 1 + obstacle_error, self.size)
            south_y = max(obstacle.south_west.y - self.robot.south_length - obstacle_error, 0)
            north_y = min(obstacle.north_east.y + self.robot.north_length + 1 + obstacle_error, self.size)

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
        self.centre = Point((self.north_east.x - self.south_west.x) // 2, (self.north_east.y - self.south_west.y) // 2)
        self.north_length = self.north_east.y - self.centre.y
        self.east_length = self.north_east.x - self.centre.x
        self.south_length = self.centre.y - self.south_west.y
        self.west_length = self.centre.x - self.south_west.x

    @property
    def clearance(self):
        # Assumes that height & width are the same
        return self.north_east.y - self.south_west.y + 1

    @property
    def vector(self) -> Vector:
        return Vector(self.direction, self.centre.x, self.centre.y)


@dataclass(unsafe_hash=True)
class Obstacle(Entity):
    image_id: int

    def __post_init__(self):
        super().__post_init__()
        assert 1 <= self.image_id < 36


@dataclass
class Robot(Entity):
    def __post_init__(self):
        super().__post_init__()
