from __future__ import annotations

from pathfinding.world.primitives import Direction, Vector
from pathfinding.world.world import Obstacle, World, Robot


def generate_objectives(world: World) -> dict[Obstacle, tuple[Vector, set[Vector]]]:
    objectives = dict()
    for obstacle in world.obstacles:
        generated = __generate_objectives(world, obstacle)
        if not generated:
            print(f"WARNING: Could not generate objectives for {obstacle}. Skipping.")
            continue

        objectives[obstacle] = next(iter(generated)), generated

    return objectives


def __generate_objectives(world: World, obstacle: Obstacle) -> set[Vector]:
    """
    Compute all possible objective locations for an obstacle.

    :param world: The world.
    :param obstacle: The obstacle.
    :return: The valid objectives.
    """

    """
    The minimum distance (in grid cells) between the obstacle and centre of objective, inclusive. (Total cm / cm per cell).
    """
    minimum_gap = 25 // world.cell_size
    """
    The maximum distance (in grid cells) between the obstacle and centre of objective, exclusive. (Total cm / cm per cell).
    """
    maximum_gap = 30 // world.cell_size

    """
    The offset to the sides (in grid cells) between the obstacle and objective, inclusive. 
    (Total cm / cm per cell). This should be increased as the difference in sizes between obstacles & the robot increases.
    """
    offset = 10 // world.cell_size

    objectives = set()
    for gap in range(minimum_gap, maximum_gap):
        if obstacle.south_west.x == 0 or obstacle.south_west.y == 0 or obstacle.north_east.x == world.size - 1 or obstacle.north_east.y == world.size - 1:
            offset += 2

        for alignment in range(-offset, obstacle.clearance + offset):
            objective = __suggest_objective(world.robot, obstacle, gap + 1, alignment)
            if world.contains(objective):
                objectives.add(objective)

    return objectives


def __suggest_objective(robot: Robot, obstacle: Obstacle, gap: int, alignment: int) -> Vector:
    """
    Creates an objective from this obstacle.

    This function assumes that obstacles are always smaller than the robot. It does not check whether the objective
    collides with other obstacles.

    :param obstacle: The obstacle.
    :param gap: The distance (in grid cells) between the obstacle and objective.
    :param alignment: An offset (in grid cells) to adjust the suggested objective's placement by.
    :return: An objective.
    """

    clearance = obstacle.clearance - 1
    match obstacle.direction:
        case Direction.NORTH:
            return Vector(
                Direction.SOUTH,
                obstacle.north_east.x - clearance + alignment,
                obstacle.north_east.y + robot.south_length + gap,
            )

        case Direction.EAST:
            return Vector(
                Direction.WEST,
                obstacle.north_east.x + robot.west_length + gap,
                obstacle.north_east.y - clearance + alignment
            )

        case Direction.SOUTH:
            return Vector(
                Direction.NORTH,
                obstacle.south_west.x + clearance - alignment,
                obstacle.south_west.y - robot.north_length - gap
            )

        case Direction.WEST:
            return Vector(
                Direction.EAST,
                obstacle.south_west.x - robot.east_length - gap,
                obstacle.south_west.y + clearance - alignment,
                )
