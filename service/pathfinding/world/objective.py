from __future__ import annotations

from dataclasses import dataclass

from pathfinding.world.world import Entity, World, Obstacle, Direction, Point


def __place_objective(world: World, obstacle: Obstacle) -> Objective:
    # TODO: call __suggest_objective(...)
    pass

def __suggest_objective(world: World, obstacle: Obstacle, gap: int, left_align: bool) -> Objective:
    """
    Creates an objective from this obstacle.

    This function assumes that obstacles are always smaller than the robot. It does not check whether the objective 
    collides with other obstacles. It left aligns the objective by default. 
    
    :param world: The world.
    :param obstacle: The obstacle.
    :param gap: The minimum distance between the obstacle and objective.
    :param left_align: True if the objective is left-aligned to the obstacle. False if it is right-aligned.
    :return: An objective.
    """
    robot = world.robot
    match (obstacle.direction, left_align):
        case (Direction.NORTH, True):
            north_west = obstacle.north_west
            return Objective(
                Direction.SOUTH,
                Point(north_west.x, north_west.y + gap),
                Point(north_west.x + robot.width, north_west.y + gap + robot.height),
                obstacle.image_id
            )
        case (Direction.NORTH, False):
            return Objective(
                Direction.SOUTH,
                Point(obstacle.north_east.x - robot.width, obstacle.north_east.y + gap),
                Point(obstacle.north_east.x, obstacle.north_east.y + gap + robot.height),
                obstacle.image_id
            )

        case (Direction.EAST, True):
            return Objective(
                Direction.WEST,
                Point(obstacle.north_east.x + gap, obstacle.north_east.x - robot.height),
                Point(obstacle.north_east.x + gap + robot.width, obstacle.north_east.y),
                obstacle.image_id
            )
        case (Direction.EAST, False):
            south_east = obstacle.south_east
            return Objective(
                Direction.WEST,
                Point(south_east.x + gap, south_east.x),
                Point(south_east.x + gap + robot.width, south_east.y + robot.height),
                obstacle.image_id
            )

        case (Direction.SOUTH, True):
            south_east = obstacle.south_east
            return Objective(
                Direction.NORTH,
                Point(obstacle.north_east.x - robot.width, south_east.y - gap - robot.height),
                Point(obstacle.north_east.x, south_east.y - gap),
                obstacle.image_id
            )
        case (Direction.SOUTH, False):
            return Objective(
                Direction.WEST,
                Point(obstacle.south_west.x, obstacle.south_west.y - gap - robot.height),
                Point(obstacle.south_west.x + robot.width, obstacle.south_west.y - gap),
                obstacle.image_id
            )

        case (Direction.WEST, True):
            return Objective(
                Direction.EAST,
                Point(obstacle.south_west.x - gap - robot.width, obstacle.south_west.y),
                Point(obstacle.south_west.x - gap, obstacle.south_west.y + robot.height),
                obstacle.image_id
            )
        case (Direction.WEST, False):
            north_west = obstacle.north_west
            return Objective(
                Direction.EAST,
                Point(north_west.x - gap - robot.width, north_west.y - robot.height),
                Point(north_west.x - gap, north_west.y),
                obstacle.image_id
            )


@dataclass
class Objective(Entity):
    image_id: int

    def __post_init__(obstacle):
        assert 1 <= obstacle.image_id < 36
