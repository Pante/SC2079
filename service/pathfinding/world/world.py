from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import List

import numpy as np


GRID_CELL_LENGTH = 5


@dataclass
class Point:
    x: int
    y: int

    def direction(self, to: Point) -> Direction:
        assert self.x != to.x ^ self.y != to.y
        match (self.x, self.y):
            case (0, y) if y < 0:
                return Direction.NORTH
            case (x, 0) if x < 0:
                return Direction.EAST
            case (x, 0) if x > 0:
                return Direction.WEST
            case (0, y) if y > 0:
                return Direction.SOUTH


class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    def same_axis(self, direction: Direction) -> bool:
        """
        Determines if both directions are on the same axis, i.e. NORTH and SOUTH, EAST and WEST, or NORTH and NORTH.

        :param direction: The other direction.
        :return: True if both directions are on the same axis.
        """
        return self == direction or self == direction.opposite

    @property
    def opposite(self) -> Direction:
        match self:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.WEST:
                return Direction.EAST
            case Direction.SOUTH:
                return Direction.NORTH


class World:
    """
    A world. It applies a Brushfire-like algorithm to compute the true clearance of all cells in a grid.

    See https://harablog.wordpress.com/2009/01/29/clearance-based-pathfinding/
    """
    width: int
    height: int
    grid: np.ndarray
    robot: Robot
    obstacles: [Obstacle]

    def __init__(self, width: int, height: int, robot: Robot, obstacles: List[Obstacle]):
        assert self.__inside(robot)
        assert all(map(lambda obstacle: self.__inside(obstacle), self.obstacles))

        self.width = width
        self.height = height
        self.grid = np.zeros((0, 0), dtype=np.int32)
        self.robot = robot
        self.obstacles = obstacles

        self.__annotate_obstacles()
        self.__annotate_true_clearance()

    def __inside(self, entity: Entity) -> bool:
        return (0 <= entity.south_west.x < self.width and
                0 <= entity.north_east.x < self.width and
                0 <= entity.south_west.y < self.height and
                0 <= entity.north_east.y < self.height)

    def __annotate_obstacles(self: World) -> None:
        for obstacle in self.obstacles:
            for x in range(obstacle.south_west.x, obstacle.north_east.x + 1):
                for y in range(obstacle.south_west.y, obstacle.north_east.y + 1):
                    self.grid[x, y] = -1

    def __annotate_true_clearance(self: World) -> None:
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.grid[x, y] != -1:
                    self.grid[x, y] = self.__compute_true_clearance(x, y)

    def __compute_true_clearance(self: World, x: int, y: int) -> int:
        clearance = 1
        for size in range(1, max(self.width, self.height)):
            for box_x in range(x, x + size):
                for box_y in range(y, y + size):
                    if self.grid[x, y] == -1:
                        return clearance

    def can_contain(self, entity: Entity) -> bool:
        if not self.__inside(entity):
            return False

        for x in range(entity.south_west.x, entity.north_east.x):
            for y in range(entity.south_west.y, entity.north_east.y):
                if self.grid[x, y] == -1:
                    return False

        return True


@dataclass
class Entity:
    direction: Direction
    south_west: Point
    north_east: Point

    def __post_init__(self):
        assert 0 <= self.south_west.x <= self.north_east.x
        assert 0 <= self.south_west.y <= self.north_east.y

    @property
    def north_west(self) -> Point:
        return Point(self.north_east.x, self.south_west.y)

    @property
    def south_east(self) -> Point:
        return Point(self.south_west.x, self.north_east.y)


@dataclass
class Robot(Entity):
    @property
    def height(self):
        return self.north_east.y - self.south_west.y

    @property
    def width(self):
        return self.north_east.x - self.south_east.x


@dataclass()
class Obstacle(Entity):
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36
