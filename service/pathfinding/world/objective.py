from __future__ import annotations

from dataclasses import dataclass

from pathfinding.world.primitives import Direction, Point, Vector
from pathfinding.world.world import Entity, World, Obstacle


def generate_objectives(world: World) -> dict[Obstacle, set[Vector]]:
    objectives: dict[Obstacle, set[Vector]] = {}
    for obstacle in world.obstacles:
        generated = __generate_objectives(world, obstacle)
        if not generated:
            print(f'WARNING: Could not generate objectives for {obstacle}. Skipping.')
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
    minimum_gap = 5 // world.cell_size
    """
    The maximum distance (in grid cells) between the obstacle and objective, exclusive. (Total cm / cm per cell).
    """
    maximum_gap = 25 // world.cell_size

    """
    The minimum left/bottom alignment (in grid cells) between the obstacle and objective, inclusive. 
    (Total cm / cm per cell). This should be increased as the difference in sizes between obstacles & the robot increases.
    """
    minimum_alignment = 5 // world.cell_size

    # Max alignment computation assumes that obstacle clearance is less than robot. It stops when the robot is
    # left-aligned with the obstacle. This excludes valid positions to the right if the obstacle is larger than the
    # robot.
    assert minimum_alignment < world.robot.clearance
    assert obstacle.clearance < world.robot.clearance

    objectives: set[Vector] = set()
    for alignment in range(minimum_alignment, world.robot.clearance + 1):
        for gap in range(minimum_gap, maximum_gap):
            objective = __suggest_objective(world, obstacle, gap + 1, alignment)
            if world.contains(objective):
                objectives.add(objective.vector)

    return objectives


def __suggest_objective(world: World, obstacle: Obstacle, gap: int, alignment: int) -> __Objective:
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
    assert alignment <= world.robot.clearance

    clearance = world.robot.clearance
    match obstacle.direction:
        case Direction.NORTH:
            print(obstacle.north_east.x - clearance + alignment, 0)
            return __Objective.from_obstacle(
                Direction.SOUTH,
                Point(max(obstacle.north_east.x - clearance + alignment, 0), max(obstacle.north_west.y + gap, 0)),
                clearance,
                clearance,
            )

        case Direction.EAST:
            return __Objective.from_obstacle(
                Direction.WEST,
                Point(max(obstacle.north_east.x + gap, 0), max(obstacle.north_east.y - clearance + alignment, 0)),
                clearance,
                clearance,
            )

        case Direction.SOUTH:
            south_east = obstacle.south_east
            return __Objective.from_obstacle(
                Direction.NORTH,
                Point(max(south_east.x - clearance + alignment, 0), max(south_east.y - gap - clearance, 0)),
                clearance,
                clearance,
            )

        case Direction.WEST:
            north_west = obstacle.north_west
            return __Objective.from_obstacle(
                Direction.EAST,
                Point(max(north_west.x - gap - clearance, 0),
                      max(north_west.y - clearance + alignment, 0)),
                clearance,
                clearance,
            )


@dataclass()
class __Objective(Entity):

    @classmethod
    def from_obstacle(
            cls,
            direction: Direction,
            south_west: Point,
            width: int,
            height: int,
    ) -> __Objective:
        return cls(
            direction,
            south_west,
            Point(south_west.x + width - 1, south_west.y + height - 1),
        )

    def __post_init__(self):
        super().__post_init__()
