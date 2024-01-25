from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from service.utils.constants import Direction

@dataclass
class Entity:
    """
    An entity in a grid.

    Attributes:
        direction (Direction): The direction that the entity is currently facing.
        south_west (Tuple[int, int]): The x & y coordinates of the south-west corner of this entity.
        north_east (Tuple[int, int]): The x & y coordinates of the north-east corner of this entity.
    """
    direction: Direction
    south_west: Tuple[int, int]
    north_east: Tuple[int, int]

    def __post_init__(self):
        assert 0 <= self.south_west[0] <= self.north_east[0]
        assert 0 <= self.south_west[1] <= self.north_east[1]

    def center_x(self) -> int:
        return (self.north_east[0] - self.south_west[0]) // 2

    def center_y(self) -> int:
        return (self.north_east[1] - self.south_west[1]) // 2
    
@dataclass
class Objective(Entity):
    """
    An objective that a robot should move towards.
    """
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36

@dataclass
class Robot(Entity):
    pass


@dataclass
class Obstacle(Entity):
    """
    Attributes:
        GAP: The gap between an obstacle and generated objective.
    """
    GAP = 1

    """
    An obstacle on the grid.
    """
    image_id: int

    def __post_init__(self):
        assert 1 <= self.image_id < 36

    def left_aligned_objective(self, robot: Robot) -> Objective:
        """
        Creates an objective from this obstacle.

        This function does not check whether the objective collides with other obstacles. Furthermore, the objective is
        always aligned to the left of the obstacle which lead to issues in edge cases.

        :param robot: The robot.
        :return: An objective
        """
        width, height = robot.north_east[0] - robot.south_west[0], robot.north_east[0] - robot.south_west[0]
        match self.direction:
            case Direction.NORTH:
                return Objective(
                    Direction.SOUTH,
                    (self.south_west[0], self.north_east[1] + self.GAP),
                    (self.south_west[0] + width, self.north_east[1] + self.GAP + height),
                    self.image_id
                )
            case Direction.EAST:
                return Objective(
                    Direction.WEST,
                    (self.north_east[0] + self.GAP, self.north_east[1] - height),
                    (self.north_east[0] + self.GAP + width, self.north_east[1]),
                    self.image_id
                )

            case Direction.SOUTH:
                return Objective(
                    Direction.NORTH,
                    (self.north_east[0] - width, self.south_west[1] - self.GAP - height),
                    (self.north_east[0], self.south_west[1] - self.GAP),
                    self.image_id
                )

            case Direction.WEST:
                return Objective(
                    Direction.EAST,
                    (self.south_west[0] - self.GAP - width, self.south_west[1]),
                    (self.south_west[0] - self.GAP, self.south_west[1] + height),
                    self.image_id
                )

class Grid:
    """
    Attributes:
        width (int): The grid's width (x-axis).
        height (int): The grid's height (y-axis).
        __cells (dict[Tuple[int, int], Entity]): The south-west corners of the entities in the grid.
    """
    width: int
    height: int
    __cells: dict[Tuple[int, int], Entity]

    def __init__(self, width: int, height: int, robot: Robot, obstacles: [Obstacle]):
        assert 0 <= robot.north_east[0] < width
        assert 0 <= robot.north_east[1] < height

        self.width = width
        self.height = height
        self.__cells = {robot.south_west: robot}

        for obstacle in obstacles:
            assert 0 <= obstacle.north_east[0] < width
            assert 0 <= obstacle.north_east[1] < height

            self.__cells[obstacle.south_west] = obstacle

