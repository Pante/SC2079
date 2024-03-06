from __future__ import annotations

from pathfinding.world.primitives import Direction, Vector
from pathfinding.world.world import Obstacle, World


def generate_objectives(world: World) -> dict[Obstacle, set[Vector]]:
    objectives: dict[Obstacle, set[Vector]] = {}
    for obstacle in world.obstacles:
        generated = __generate_objectives(world, obstacle)
        if not generated:
            print(f"WARNING: Could not generate objectives for {obstacle}. Skipping.")
            continue

        objectives[obstacle] = generated

    return objectives


def __generate_objectives(world: World, obstacle: Obstacle) -> set[Vector]:
    """
    Compute all possible objective locations for an obstacle.

    :param world: The world.
    :param obstacle: The obstacle.
    :return: The valid objectives.
    """

    """
    The minimum distance (in grid cells) between the obstacle and objective, inclusive. (Total cm / cm per cell).
    """
    minimum_gap = 22 // world.cell_size
    """
    The maximum distance (in grid cells) between the obstacle and objective, exclusive. (Total cm / cm per cell).
    """
    maximum_gap = 32 // world.cell_size

    """
    The offset to the sides (in grid cells) between the obstacle and objective, inclusive. 
    (Total cm / cm per cell). This should be increased as the difference in sizes between obstacles & the robot increases.
    """
    offset = 0 // world.cell_size

    objectives = set()

    for alignment in range(-offset, obstacle.clearance + offset):
        for gap in range(minimum_gap, maximum_gap):
            objective = __suggest_objective(obstacle, gap + 1, alignment)
            if world.contains(objective):
                objectives.add(objective)

    return objectives


def __suggest_objective(obstacle: Obstacle, gap: int, alignment: int) -> Vector:
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
                max(obstacle.north_east.x - clearance + alignment, 0),
                max(obstacle.north_east.y + gap, 0),
            )

        case Direction.EAST:
            return Vector(
                Direction.WEST,
                max(obstacle.north_east.x + gap, 0),
                max(obstacle.north_east.y - clearance + alignment, 0),
            )

        case Direction.SOUTH:
            south_east = obstacle.south_east
            return Vector(
                Direction.NORTH,
                max(south_east.x - clearance + alignment, 0),
                max(south_east.y - gap, 0),
            )

        case Direction.WEST:
            north_west = obstacle.north_west
            return Vector(
                Direction.EAST,
                max(north_west.x - gap, 0),
                max(north_west.y - clearance + alignment, 0),
            )
