from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pathfinding.world.world import Entity, World, Obstacle
from pathfinding.world.primitives import Direction, Point

"""
The minimum distance (in grid cells) between the obstacle and objective, inclusive.
"""
MINIMUM_GAP = 1
"""
The ideal distance (in grid cells) between the obstacle and objective.
"""
IDEAL_GAP = 3
"""
The maximum distance (in grid cells) between the obstacle and objective, exclusive.
"""
MAXIMUM_GAP = 5


def generate_objectives(world: World) -> List[Objective]:
    return [
        objective for obstacle in world.obstacles if (objective := __generate_objective(world, obstacle)) is not None
    ]


def __generate_objective(world: World, obstacle: Obstacle) -> Objective | None:
    """
    Tries to place an objective in an ideal location. Failing that, iteratively tries to place the objective in a valid
    location.

    :param world: The world.
    :param obstacle: The obstacle.
    :return: An objective if one can be placed. None otherwise.
    """
    ideal = __suggest_objective(world, obstacle, IDEAL_GAP, world.robot.clearance // 2)
    if world.contains(ideal):
        return ideal

    # TODO: Can we find a nice way to return objectives closer to ideal first?
    for alignment in range(0, world.robot.clearance):
        for gap in range(MINIMUM_GAP, MAXIMUM_GAP):
            objective = __suggest_objective(world, obstacle, gap, alignment)
            if world.contains(objective):
                return objective

    return None


def __suggest_objective(world: World, obstacle: Obstacle, gap: int, alignment: int) -> Objective:
    """
    Creates an objective from this obstacle.

    This function assumes that obstacles are always smaller than the robot. It does not check whether the objective 
    collides with other obstacles.
    
    :param world: The world.
    :param obstacle: The obstacle.
    :param gap: The distance (in grid cells) between the obstacle and objective.
    :param alignment: An alignment (in grid cells) to adjust the suggested objective's placement by.
    :return: An objective.
    """
    assert alignment < world.robot.clearance

    clearance = world.robot.clearance
    match obstacle.direction:
        case Direction.NORTH:
            north_west = obstacle.north_west
            return Objective.from_obstacle(
                Direction.SOUTH,
                Point(north_west.x - alignment, north_west.y + gap),
                clearance,
                clearance,
                obstacle.image_id
            )

        case Direction.EAST:
            return Objective.from_obstacle(
                Direction.WEST,
                Point(obstacle.north_east.x + gap, obstacle.north_east.x - clearance + alignment),
                clearance,
                clearance,
                obstacle.image_id
            )

        case Direction.SOUTH:
            south_east = obstacle.south_east
            return Objective.from_obstacle(
                Direction.NORTH,
                Point(obstacle.north_east.x - clearance + alignment, south_east.y - gap - clearance),
                clearance,
                clearance,
                obstacle.image_id
            )

        case Direction.WEST:
            return Objective.from_obstacle(
                Direction.EAST,
                Point(obstacle.south_west.x - gap - clearance, obstacle.south_west.y - alignment),
                clearance,
                clearance,
                obstacle.image_id
            )


@dataclass
class Objective(Entity):
    image_id: int

    @classmethod
    def from_obstacle(
            cls,
            direction: Direction,
            south_west: Point,
            width: int,
            height: int,
            image_id: int,
    ) -> Objective:
        return cls(
            direction,
            south_west,
            Point(south_west.x + width, south_west.y + height),
            image_id,
        )

    def __post_init__(self):
        assert 1 <= self.image_id < 36
        super().__post_init__()
